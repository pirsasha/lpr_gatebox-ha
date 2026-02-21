# =========================================================
# File: custom_components/lpr_gatebox/sensor.py
# Project: LPR GateBox HA integration
# Version: 0.1.0
# =========================================================

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    SENSOR_LAST_PLATE,
    SENSOR_LAST_CONF,
    SENSOR_LAST_STATUS,
    SENSOR_LAST_MESSAGE,
    SENSOR_LAST_TS,
)
from .coordinator import LprGateBoxCoordinator

# Human-friendly Russian entity names (UI)
_SENSOR_NAMES_RU = {
    "last_plate": "LPR Последний номер",
    "last_confidence": "LPR Уверенность",
    "last_status": "LPR Статус",
    "last_message": "LPR Сообщение",
    "last_ts": "LPR Время последнего события",
}



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coord: LprGateBoxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            LprSensor(coord, SENSOR_LAST_PLATE),
            LprSensor(coord, SENSOR_LAST_CONF),
            LprSensor(coord, SENSOR_LAST_STATUS),
            LprSensor(coord, SENSOR_LAST_MESSAGE),
            LprSensor(coord, SENSOR_LAST_TS),
        ]
    )


class LprSensor(SensorEntity):
    def __init__(self, coord: LprGateBoxCoordinator, kind: str) -> None:
        self._coord = coord
        self._kind = kind
        self._attr_unique_id = f"{coord.entry.entry_id}_{kind}"
        self._attr_name = _SENSOR_NAMES_RU.get(kind, f"LPR {kind}")
        self._unsub = None

    async def async_added_to_hass(self):
        self._unsub = self._coord.add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        if self._unsub:
            self._unsub()
            self._unsub = None

    @property
    def native_value(self):
        s = self._coord.state
        if self._kind == SENSOR_LAST_PLATE:
            return s.last_plate
        if self._kind == SENSOR_LAST_CONF:
            return s.last_conf
        if self._kind == SENSOR_LAST_STATUS:
            return s.last_status
        if self._kind == SENSOR_LAST_MESSAGE:
            return s.last_message
        if self._kind == SENSOR_LAST_TS:
            return s.last_ts
        return None