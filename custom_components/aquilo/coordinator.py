"""DataUpdateCoordinator for the Aquilo integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class AquiloDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Poll the Aquilo device ``/state`` endpoint and expose it per sensor id."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.entry = entry
        self._host: str = entry.data[CONF_HOST]
        self._session = async_get_clientsession(hass)

    @property
    def url(self) -> str:
        """Return the state endpoint URL."""
        return f"http://{self._host}/state"

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch the latest state, keyed by sensor id."""
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(self.url)
                response.raise_for_status()
                # The device may not send a proper JSON content-type header,
                # so do not enforce it.
                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with {self.url}: {err}") from err
        except ValueError as err:
            raise UpdateFailed(f"Invalid JSON from {self.url}: {err}") from err

        sensors = payload.get("sensors") if isinstance(payload, dict) else None
        if not isinstance(sensors, list) or not sensors:
            raise UpdateFailed(f"Unexpected payload from {self.url}: {payload!r}")

        result: dict[str, dict[str, Any]] = {}
        for sensor in sensors:
            if not isinstance(sensor, dict):
                continue
            sensor_id = sensor.get("id")
            if sensor_id is None:
                continue
            result[str(sensor_id)] = sensor

        if not result:
            raise UpdateFailed("No sensors with an 'id' field in the payload")

        return result
