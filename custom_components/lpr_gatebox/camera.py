# =========================================================
# File: custom_components/lpr_gatebox/camera.py
# Project: LPR GateBox HA integration
# Version: 0.1.0
# =========================================================

from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CAMERA_LIVE_FRAME
from .coordinator import LprGateBoxCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coord: LprGateBoxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LprLiveFrameCamera(coord)])


class LprLiveFrameCamera(Camera):
    def __init__(self, coord: LprGateBoxCoordinator) -> None:
        super().__init__()
        self._coord = coord
        self._attr_unique_id = f"{coord.entry.entry_id}_{CAMERA_LIVE_FRAME}"
        self._attr_name = "LPR Последний кадр"

    async def async_camera_image(self, width=None, height=None):
        url = f"{self._coord.base_url}/api/v1/rtsp/frame.jpg"
        try:
            async with self._coord.session.get(url, timeout=8) as resp:
                if resp.status != 200:
                    return None
                return await resp.read()
        except Exception:
            return None