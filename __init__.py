"""Enhanced Japan Weather Integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import JapanWeatherCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "weather", "camera"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Japan Weather integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Enhanced Japan Weather from a config entry."""
    
    # Get coordinates from config entry
    latitude = entry.data.get("latitude", 35.6762)  # Default to Tokyo
    longitude = entry.data.get("longitude", 139.6503)
    
    _LOGGER.debug(f"Setting up Enhanced Japan Weather for coordinates: {latitude}, {longitude}")
    
    # Create coordinator
    coordinator = JapanWeatherCoordinator(hass, latitude, longitude)
    
    # Fetch initial data
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"Failed to initialize Enhanced Japan Weather: {err}")
        return False
    
    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    # Also store with the key that sensor.py expects
    hass.data[DOMAIN]["enhanced_coordinator"] = coordinator
    
    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Enhanced Japan Weather config entry."""
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Remove coordinator
        coordinator = hass.data[DOMAIN].pop(entry.entry_id, None)
        # Also remove the enhanced_coordinator key
        hass.data[DOMAIN].pop("enhanced_coordinator", None)
        if coordinator:
            await coordinator.async_close()
    
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload Enhanced Japan Weather config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
