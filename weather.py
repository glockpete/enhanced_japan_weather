"""Enhanced Weather Entity for Japan Weather Integration."""
from __future__ import annotations

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
    Forecast,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, WEATHER_CODES
from .coordinator import JapanWeatherCoordinator

_LOGGER = logging.getLogger(__name__)

# Weather code mapping for Home Assistant conditions
WEATHER_CODE_MAP = {
    0: "sunny",           # Clear sky
    1: "sunny",           # Mainly clear
    2: "partlycloudy",    # Partly cloudy
    3: "cloudy",          # Overcast
    45: "fog",            # Fog
    48: "fog",            # Depositing rime fog
    51: "rainy",          # Drizzle: Light
    53: "rainy",          # Drizzle: Moderate
    55: "rainy",          # Drizzle: Dense intensity
    56: "rainy",          # Freezing Drizzle: Light
    57: "rainy",          # Freezing Drizzle: Dense intensity
    61: "rainy",          # Rain: Slight
    63: "rainy",          # Rain: Moderate
    65: "rainy",          # Rain: Heavy intensity
    66: "rainy",          # Freezing Rain: Light
    67: "rainy",          # Freezing Rain: Heavy intensity
    71: "snowy",          # Snow fall: Slight
    73: "snowy",          # Snow fall: Moderate
    75: "snowy",          # Snow fall: Heavy intensity
    77: "snowy",          # Snow grains
    80: "rainy",          # Rain showers: Slight
    81: "rainy",          # Rain showers: Moderate
    82: "pouring",        # Rain showers: Violent
    85: "snowy",          # Snow showers slight
    86: "snowy",          # Snow showers heavy
    95: "lightning-rainy", # Thunderstorm: Slight or moderate
    96: "lightning-rainy", # Thunderstorm with slight hail
    99: "lightning-rainy", # Thunderstorm with heavy hail
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Enhanced Japan Weather platform from a config entry."""
    
    # Get the coordinator that was created in __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    if not coordinator:
        _LOGGER.error("Coordinator not found for Enhanced Japan Weather")
        return
    
    # Create weather entities using the existing coordinator
    entities = [
        EnhancedJapanWeatherEntity(coordinator, entry.entry_id, "primary"),
        DetailedWeatherEntity(coordinator, entry.entry_id, "detailed"),
        WeatherAlertsEntity(coordinator, entry.entry_id, "alerts"),
    ]
    
    async_add_entities(entities)

class EnhancedJapanWeatherEntity(WeatherEntity):
    """Enhanced weather entity with comprehensive data."""

    _attr_attribution = "Enhanced Japan Weather - Multiple Sources"
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | 
        WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(self, coordinator: JapanWeatherCoordinator, entry_id: str, entity_type: str):
        self.coordinator = coordinator
        self._entity_type = entity_type
        self._attr_name = f"Enhanced Japan Weather - {entity_type.title()}"
        self._attr_unique_id = f"enhanced_japan_weather_{entity_type}_{entry_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "enhanced_japan_weather")},
            name="Enhanced Japan Weather",
            manufacturer="Enhanced Weather Team",
            model="Multi-Source Weather Monitor",
            sw_version="2.0.0",
        )

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("current", {}).get("temperature")

    @property
    def native_temperature_unit(self) -> str:
        return UnitOfTemperature.CELSIUS

    @property
    def humidity(self) -> int | None:
        """Return the humidity."""
        humidity = self.coordinator.data.get("current", {}).get("humidity")
        return int(humidity) if humidity is not None else None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self.coordinator.data.get("current", {}).get("pressure")

    @property
    def native_pressure_unit(self) -> str:
        return UnitOfPressure.HPA

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return self.coordinator.data.get("current", {}).get("wind_speed")

    @property
    def native_wind_speed_unit(self) -> str:
        return UnitOfSpeed.KILOMETERS_PER_HOUR

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        return self.coordinator.data.get("current", {}).get("wind_direction")

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility."""
        visibility = self.coordinator.data.get("current", {}).get("visibility")
        return visibility / 1000 if visibility is not None else None  # Convert m to km

    @property
    def native_visibility_unit(self) -> str:
        return UnitOfLength.KILOMETERS

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the wind gust speed."""
        return self.coordinator.data.get("current", {}).get("wind_gusts")

    @property
    def uv_index(self) -> float | None:
        """Return the UV index."""
        return self.coordinator.data.get("current", {}).get("uv_index")

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        weather_code = self.coordinator.data.get("current", {}).get("weather_code")
        if weather_code is not None:
            return WEATHER_CODE_MAP.get(int(weather_code), "exceptional")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        current = self.coordinator.data.get("current", {})
        attributes = {
            "apparent_temperature": current.get("apparent_temperature"),
            "heat_index": current.get("heat_index"),
            "comfort_level": current.get("comfort_level"),
            "cloud_cover": current.get("cloud_cover"),
            "precipitation": current.get("precipitation"),
            "precipitation_probability": current.get("precipitation_probability"),
            "data_sources": self.coordinator.data.get("sources", []),
            "last_update": self.coordinator.data.get("last_update"),
            "alerts_count": len(self.coordinator.data.get("alerts", [])),
        }
        return {k: v for k, v in attributes.items() if v is not None}

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return hourly forecast."""
        try:
            hourly = self.coordinator.data.get("hourly", {})
            if not hourly:
                return None

            forecasts = []
            times = hourly.get("time", [])
            temperatures = hourly.get("temperature_2m", [])
            weather_codes = hourly.get("weather_code", [])
            precipitation = hourly.get("precipitation", [])
            precipitation_prob = hourly.get("precipitation_probability", [])

            # Get next 24 hours
            for i in range(min(24, len(times))):
                if i < len(temperatures):
                    forecast = Forecast(
                        datetime=times[i],
                        native_temperature=temperatures[i],
                        condition=WEATHER_CODE_MAP.get(
                            int(weather_codes[i]) if i < len(weather_codes) else 0, 
                            "exceptional"
                        ),
                        native_precipitation=precipitation[i] if i < len(precipitation) else None,
                        precipitation_probability=precipitation_prob[i] if i < len(precipitation_prob) else None,
                    )
                    forecasts.append(forecast)

            return forecasts
        except Exception as e:
            _LOGGER.error(f"Error creating hourly forecast: {e}")
            return None

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return daily forecast."""
        try:
            daily = self.coordinator.data.get("daily", {})
            if not daily:
                return None

            forecasts = []
            times = daily.get("time", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            weather_codes = daily.get("weather_code", [])
            precipitation_sum = daily.get("precipitation_sum", [])
            precipitation_prob = daily.get("precipitation_probability_max", [])

            for i in range(min(7, len(times))):  # 7-day forecast
                if i < len(temp_max) and i < len(temp_min):
                    forecast = Forecast(
                        datetime=times[i],
                        native_temperature=temp_max[i],
                        native_templow=temp_min[i],
                        condition=WEATHER_CODE_MAP.get(
                            int(weather_codes[i]) if i < len(weather_codes) else 0,
                            "exceptional"
                        ),
                        native_precipitation=precipitation_sum[i] if i < len(precipitation_sum) else None,
                        precipitation_probability=precipitation_prob[i] if i < len(precipitation_prob) else None,
                    )
                    forecasts.append(forecast)

            return forecasts
        except Exception as e:
            _LOGGER.error(f"Error creating daily forecast: {e}")
            return None

    async def async_update(self) -> None:
        """Update the entity."""
        await self.coordinator.async_request_refresh()

class DetailedWeatherEntity(WeatherEntity):
    """Detailed weather entity with additional metrics."""

    def __init__(self, coordinator: JapanWeatherCoordinator, entry_id: str, entity_type: str):
        self.coordinator = coordinator
        self._entity_type = entity_type
        self._attr_name = f"Detailed Weather Metrics"
        self._attr_unique_id = f"detailed_weather_{entry_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "enhanced_japan_weather")},
            name="Enhanced Japan Weather",
            manufacturer="Enhanced Weather Team",
            model="Multi-Source Weather Monitor",
            sw_version="2.0.0",
        )

    @property
    def native_temperature(self) -> float | None:
        """Return apparent temperature (feels like)."""
        return self.coordinator.data.get("current", {}).get("apparent_temperature")

    @property
    def native_temperature_unit(self) -> str:
        return UnitOfTemperature.CELSIUS

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed weather attributes."""
        current = self.coordinator.data.get("current", {})
        daily = self.coordinator.data.get("daily", {})
        
        # Get today's daily data
        today_data = {}
        if daily and "time" in daily:
            today = datetime.now().strftime("%Y-%m-%d")
            try:
                today_idx = daily["time"].index(today)
                today_data = {
                    "sunrise": daily.get("sunrise", [None])[today_idx] if len(daily.get("sunrise", [])) > today_idx else None,
                    "sunset": daily.get("sunset", [None])[today_idx] if len(daily.get("sunset", [])) > today_idx else None,
                    "max_uv_index": daily.get("uv_index_max", [None])[today_idx] if len(daily.get("uv_index_max", [])) > today_idx else None,
                    "total_precipitation": daily.get("precipitation_sum", [None])[today_idx] if len(daily.get("precipitation_sum", [])) > today_idx else None,
                }
            except (ValueError, IndexError):
                pass

        attributes = {
            # Current conditions
            "real_temperature": current.get("temperature"),
            "apparent_temperature": current.get("apparent_temperature"),
            "heat_index": current.get("heat_index"),
            "comfort_level": current.get("comfort_level"),
            "humidity": current.get("humidity"),
            "pressure": current.get("pressure"),
            "cloud_cover": current.get("cloud_cover"),
            "visibility_km": current.get("visibility", 0) / 1000 if current.get("visibility") else None,
            
            # Wind data
            "wind_speed_kmh": current.get("wind_speed"),
            "wind_direction": current.get("wind_direction"),
            "wind_gusts_kmh": current.get("wind_gusts"),
            
            # Precipitation
            "current_precipitation_mm": current.get("precipitation"),
            "precipitation_probability": current.get("precipitation_probability"),
            
            # UV and solar
            "uv_index": current.get("uv_index"),
            "uv_risk": self._get_uv_risk_level(current.get("uv_index")),
            
            # Daily summary
            **today_data,
            
            # Data quality
            "data_sources": self.coordinator.data.get("sources", []),
            "last_update": self.coordinator.data.get("last_update"),
        }
        
        return {k: v for k, v in attributes.items() if v is not None}

    def _get_uv_risk_level(self, uv_index: Optional[float]) -> str:
        """Get UV risk level description."""
        if uv_index is None:
            return "unknown"
        elif uv_index <= 2:
            return "low"
        elif uv_index <= 5:
            return "moderate"
        elif uv_index <= 7:
            return "high"
        elif uv_index <= 10:
            return "very_high"
        else:
            return "extreme"

class WeatherAlertsEntity(WeatherEntity):
    """Weather alerts entity."""

    def __init__(self, coordinator: JapanWeatherCoordinator, entry_id: str, entity_type: str):
        self.coordinator = coordinator
        self._entity_type = entity_type
        self._attr_name = f"Weather Alerts"
        self._attr_unique_id = f"weather_alerts_{entry_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "enhanced_japan_weather")},
            name="Enhanced Japan Weather",
            manufacturer="Enhanced Weather Team",
            model="Multi-Source Weather Monitor",
            sw_version="2.0.0",
        )

    @property
    def native_temperature(self) -> float | None:
        """Return alert count as state."""
        alerts = self.coordinator.data.get("alerts", [])
        return len(alerts)

    @property
    def native_temperature_unit(self) -> str:
        return "alerts"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return weather alerts as attributes."""
        alerts = self.coordinator.data.get("alerts", [])
        
        attributes = {
            "total_alerts": len(alerts),
            "active_alerts": alerts,
            "high_severity_count": sum(1 for alert in alerts if alert.get("severity") == "high"),
            "medium_severity_count": sum(1 for alert in alerts if alert.get("severity") == "medium"),
            "low_severity_count": sum(1 for alert in alerts if alert.get("severity") == "low"),
            "alert_types": list(set(alert.get("type", "unknown") for alert in alerts)),
            "last_update": self.coordinator.data.get("last_update"),
        }
        
        # Add individual alert details
        for i, alert in enumerate(alerts[:5]):  # Limit to 5 most recent alerts
            attributes[f"alert_{i+1}_type"] = alert.get("type")
            attributes[f"alert_{i+1}_severity"] = alert.get("severity")
            attributes[f"alert_{i+1}_title"] = alert.get("title")
            attributes[f"alert_{i+1}_description"] = alert.get("description")
            attributes[f"alert_{i+1}_time"] = alert.get("timestamp")
        
        return attributes 