"""Config flow for the Aquilo integration."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MIN_SCAN_INTERVAL, REQUEST_TIMEOUT

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


async def _async_validate_host(hass: HomeAssistant, host: str) -> dict[str, Any]:
    """Try to read /state from the given host. Raises on failure."""
    session = async_get_clientsession(hass)
    async with asyncio.timeout(REQUEST_TIMEOUT):
        response = await session.get(f"http://{host}/state")
        response.raise_for_status()
        return await response.json(content_type=None)


class AquiloConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aquilo."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            try:
                payload = await _async_validate_host(self.hass, host)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_response"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                if not payload.get("sensors"):
                    errors["base"] = "no_sensors"
                else:
                    title = payload.get("from") or host
                    return self.async_create_entry(
                        title=f"Aquilo ({title})",
                        data={CONF_HOST: host},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return AquiloOptionsFlow()


class AquiloOptionsFlow(OptionsFlow):
    """Handle Aquilo options (polling interval)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
