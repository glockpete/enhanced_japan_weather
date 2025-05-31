"""Config flow for Enhanced Japan Weather integration."""
from __future__ import annotations

import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_LATITUDE, DEFAULT_LONGITUDE

DATA_SCHEMA = vol.Schema({
    vol.Optional("latitude", default=DEFAULT_LATITUDE): cv.latitude,
    vol.Optional("longitude", default=DEFAULT_LONGITUDE): cv.longitude,
})

class JapanWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Enhanced Japan Weather."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Basic validation
            latitude = user_input.get("latitude", DEFAULT_LATITUDE)
            longitude = user_input.get("longitude", DEFAULT_LONGITUDE)
            
            # Check if coordinates are in reasonable range for Japan
            if not (24.0 <= latitude <= 46.0):
                errors["latitude"] = "latitude_out_of_range"
            elif not (123.0 <= longitude <= 146.0):
                errors["longitude"] = "longitude_out_of_range"
            else:
                # Create entry
                title = f"Enhanced Japan Weather ({latitude:.4f}, {longitude:.4f})"
                return self.async_create_entry(
                    title=title,
                    data={
                        "latitude": latitude,
                        "longitude": longitude,
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "default_lat": str(DEFAULT_LATITUDE),
                "default_lon": str(DEFAULT_LONGITUDE),
            },
        ) 