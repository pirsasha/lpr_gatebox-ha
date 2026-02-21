# =========================================================
# File: custom_components/lpr_gatebox/__init__.py
# Project: LPR GateBox HA integration
# Version: 0.1.0
# =========================================================

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import LprGateBoxCoordinator


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = LprGateBoxCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator: LprGateBoxCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_stop()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)