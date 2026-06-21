"""The Aquilo integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import AquiloDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type AquiloConfigEntry = ConfigEntry[AquiloDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AquiloConfigEntry) -> bool:
    """Set up Aquilo from a config entry."""
    coordinator = AquiloDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: AquiloConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: AquiloConfigEntry) -> None:
    """Reload the entry when its options (e.g. scan interval) change."""
    await hass.config_entries.async_reload(entry.entry_id)
