# =========================================================
# File: custom_components/lpr_gatebox/config_flow.py
# Project: LPR GateBox HA integration
# Version: 0.1.0
# Notes:
# - Fix for HA new OptionsFlow: config_entry is read-only.
# =========================================================

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_INCLUDE_DEBUG,
    CONF_HEARTBEAT_SEC,
    CONF_POLL_MS,
    DEFAULT_INCLUDE_DEBUG,
    DEFAULT_HEARTBEAT_SEC,
    DEFAULT_POLL_MS,
)



async def _check_health(hass, base_url: str) -> bool:
    """Best-effort health check."""
    session = async_get_clientsession(hass)
    url = f"{base_url}/api/v1/health"
    try:
        async with session.get(url, timeout=8) as resp:
            return resp.status == 200
    except Exception:
        return False


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

        base_url = user_input[CONF_BASE_URL].rstrip("/")

        # quick connectivity check
        if not await _check_health(self.hass, base_url):
            errors["base"] = "cannot_connect"
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

        await self.async_set_unique_id(base_url)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"LPR GateBox ({base_url})",
            data={
                CONF_BASE_URL: base_url,
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        # NOTE: in new HA `config_entry` property is read-only; keep our own.
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is None:
            schema = vol.Schema(
                {
                    vol.Optional(
                        CONF_INCLUDE_DEBUG,
                        default=self._config_entry.options.get(CONF_INCLUDE_DEBUG, DEFAULT_INCLUDE_DEBUG),
                    ): bool,
                    vol.Optional(
                        CONF_HEARTBEAT_SEC,
                        default=self._config_entry.options.get(CONF_HEARTBEAT_SEC, DEFAULT_HEARTBEAT_SEC),
                    ): vol.Coerce(int),
                    vol.Optional(
                        CONF_POLL_MS,
                        default=self._config_entry.options.get(CONF_POLL_MS, DEFAULT_POLL_MS),
                    ): vol.Coerce(int),
                }
            )
            return self.async_show_form(step_id="init", data_schema=schema)

        return self.async_create_entry(title="", data=user_input)