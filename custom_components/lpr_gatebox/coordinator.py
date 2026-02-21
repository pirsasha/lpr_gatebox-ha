from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Optional, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_BASE_URL,
    CONF_INCLUDE_DEBUG,
    DEFAULT_INCLUDE_DEBUG,
)

LOGGER = logging.getLogger(__name__)

EVENT_TYPE = "lpr_gatebox_event"


@dataclass
class LprState:
    last_plate: str = ""
    last_conf: Optional[float] = None
    last_status: str = ""
    last_message: str = ""
    last_ts: float = 0.0
    rtsp_alive: Optional[bool] = None
    rtsp_age_ms: Optional[int] = None


class LprGateBoxCoordinator:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.session = async_get_clientsession(hass)

        data = entry.data
        opts = entry.options

        self.base_url: str = (data.get(CONF_BASE_URL) or "").rstrip("/")
        self.include_debug: bool = bool(opts.get(CONF_INCLUDE_DEBUG, data.get(CONF_INCLUDE_DEBUG, DEFAULT_INCLUDE_DEBUG)))

        self.state = LprState()

        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()
        self._listeners: list[Callable[[], Any]] = []

    def add_listener(self, cb: Callable[[], Any]):
        self._listeners.append(cb)

        def _unsub():
            try:
                self._listeners.remove(cb)
            except ValueError:
                pass

        return _unsub

    def _notify(self):
        for cb in list(self._listeners):
            try:
                cb()
            except Exception:
                pass

    async def async_start(self) -> None:
        self._stop.clear()
        self._task = asyncio.create_task(self._run(), name="lpr_gatebox_poll")
        LOGGER.info("LPR GateBox: started (poll-only) base_url=%s include_debug=%s", self.base_url, self.include_debug)

        # bootstrap: подтянуть последнее событие, чтобы сенсоры не были пустыми
        try:
            await self._poll_events_once(limit=1, bootstrap=True)
        except Exception:
            pass

    async def async_stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass
        LOGGER.info("LPR GateBox: stopped")

    async def _run(self) -> None:
        status_task = asyncio.create_task(self._status_loop(), name="lpr_gatebox_status_loop")
        try:
            while not self._stop.is_set():
                await self._poll_events_once(limit=50, bootstrap=False)
                await asyncio.sleep(1.0)
        finally:
            status_task.cancel()

    async def _status_loop(self) -> None:
        url = f"{self.base_url}/api/v1/rtsp/status"
        while not self._stop.is_set():
            try:
                async with self.session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.state.rtsp_alive = bool(data.get("alive")) if data.get("ok") else False
                        self.state.rtsp_age_ms = data.get("age_ms")
                    else:
                        self.state.rtsp_alive = None
                        self.state.rtsp_age_ms = None
            except Exception:
                self.state.rtsp_alive = None
                self.state.rtsp_age_ms = None

            self._notify()
            await asyncio.sleep(2.0)

    async def _poll_events_once(self, limit: int = 50, bootstrap: bool = False) -> None:
        url = f"{self.base_url}/api/v1/events"
        params = {
            "limit": int(limit),
            "after_ts": 0 if bootstrap else self.state.last_ts,
            "include_debug": "1" if self.include_debug else "0",
        }

        try:
            async with self.session.get(url, params=params, timeout=8) as resp:
                if resp.status != 200:
                    LOGGER.warning("LPR GateBox: poll bad status=%s", resp.status)
                    return

                data = await resp.json()
                items = data.get("items") or []

                if not items:
                    return

                # items приходят по времени (в твоём ответе они уже отсортированы по убыванию ts),
                # но мы всё равно пройдём все и обновим last_ts корректно.
                for ev in items:
                    await self._handle_event(ev)

        except Exception as e:
            LOGGER.warning("LPR GateBox: poll error: %s", e)

    async def _handle_event(self, ev: dict[str, Any]) -> None:
        ts = float(ev.get("ts") or 0.0)
        plate = str(ev.get("plate") or "")
        conf = ev.get("conf", None)

        if ts > 0:
            self.state.last_ts = max(self.state.last_ts, ts)

        if plate:
            self.state.last_plate = plate
            self.state.last_conf = float(conf) if conf is not None else None
            self.state.last_status = str(ev.get("status") or "")
            self.state.last_message = str(ev.get("message") or "")

        # событие для автоматизаций HA
        self.hass.bus.async_fire(EVENT_TYPE, ev)

        self._notify()