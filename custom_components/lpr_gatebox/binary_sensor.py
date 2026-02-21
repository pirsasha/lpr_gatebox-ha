# =========================================================
# File: custom_components/lpr_gatebox/binary_sensor.py
# Project: LPR GateBox HA integration
# Version: 0.1.0
# =========================================================

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, BINARY_RTSP_ALIVE
from .coordinator import LprGateBoxCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coord: LprGateBoxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RtspAliveBinarySensor(coord)])


class RtspAliveBinarySensor(BinarySensorEntity):
    _attr_device_class = "connectivity"

    def __init__(self, coord: LprGateBoxCoordinator) -> None:
        self._coord = coord
        self._attr_unique_id = f"{coord.entry.entry_id}_{BINARY_RTSP_ALIVE}"
        self._attr_name = "LPR RTSP доступен"
        self._unsub = None

    async def async_added_to_hass(self):
        self._unsub = self._coord.add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        if self._unsub:
            self._unsub()
            self._unsub = None

    @property
    def is_on(self):
        if self._coord.state.rtsp_alive is None:
            return None
        return bool(self._coord.state.rtsp_alive)

    @property
    def extra_state_attributes(self):
        return {"age_ms": self._coord.state.rtsp_age_ms}