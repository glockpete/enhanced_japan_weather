"""Enhanced Weather Sensors for Japan Weather Integration."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorEntity, 
    SensorDeviceClass, 
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature, 
    UnitOfPressure, 
    UnitOfSpeed, 
    UnitOfLength,
    PERCENTAGE,
    UV_INDEX,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Comprehensive sensor definitions
WEATHER_SENSORS = [
    # Temperature sensors
    SensorEntityDescription(
        key="temperature",
        name="Current Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="apparent_temperature",
        name="Feels Like Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-alert",
    ),
    SensorEntityDescription(
        key="heat_index",
        name="Heat Index",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-plus",
    ),
    
    # Humidity and atmospheric pressure
    SensorEntityDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
    ),
    SensorEntityDescription(
        key="pressure",
        name="Atmospheric Pressure",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.HPA,
        icon="mdi:gauge",
    ),
    
    # Wind measurements
    SensorEntityDescription(
        key="wind_speed",
        name="Wind Speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        icon="mdi:weather-windy",
    ),
    SensorEntityDescription(
        key="wind_direction",
        name="Wind Direction",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="°",
        icon="mdi:compass-outline",
    ),
    SensorEntityDescription(
        key="wind_gusts",
        name="Wind Gusts",
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        icon="mdi:weather-windy-variant",
    ),
    
    # Visibility and cloud cover
    SensorEntityDescription(
        key="visibility",
        name="Visibility",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        icon="mdi:eye-outline",
    ),
    SensorEntityDescription(
        key="cloud_cover",
        name="Cloud Coverage",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:weather-cloudy",
    ),
    
    # Precipitation
    SensorEntityDescription(
        key="precipitation",
        name="Current Precipitation",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="mm",
        icon="mdi:weather-rainy",
    ),
    SensorEntityDescription(
        key="precipitation_probability",
        name="Precipitation Probability",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:weather-pouring",
    ),
    
    # UV and solar
    SensorEntityDescription(
        key="uv_index",
        name="UV Index",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-sunny-alert",
    ),
    
    # Comfort and air quality
    SensorEntityDescription(
        key="comfort_level",
        name="Weather Comfort Level",
        icon="mdi:account-check",
    ),
    
    # Daily forecasts
    SensorEntityDescription(
        key="today_max_temp",
        name="Today's Maximum Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-chevron-up",
    ),
    SensorEntityDescription(
        key="today_min_temp", 
        name="Today's Minimum Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-chevron-down",
    ),
    SensorEntityDescription(
        key="today_precipitation_sum",
        name="Today's Total Precipitation",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="mm",
        icon="mdi:cup-water",
    ),
    
    # Sunrise/sunset
    SensorEntityDescription(
        key="sunrise",
        name="Sunrise Time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-up",
    ),
    SensorEntityDescription(
        key="sunset",
        name="Sunset Time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-down",
    ),
    
    # Weather alerts and status
    SensorEntityDescription(
        key="weather_alerts_count",
        name="Active Weather Alerts",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:alert-circle",
    ),
    SensorEntityDescription(
        key="weather_condition_code",
        name="Weather Condition Code",
        icon="mdi:weather-partly-cloudy",
    ),
    
    # Satellite-derived sensors
    SensorEntityDescription(
        key="sea_surface_temperature",
        name="Sea Surface Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-water",
    ),
    SensorEntityDescription(
        key="cloud_top_height",
        name="Cloud Top Height",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        icon="mdi:cloud-upload",
    ),
    SensorEntityDescription(
        key="satellite_solar_radiation",
        name="Satellite Solar Radiation",
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="W/m²",
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="aerosol_optical_depth",
        name="Aerosol Optical Depth",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="AOD",
        icon="mdi:smog",
    ),
    SensorEntityDescription(
        key="wildfire_detection_count",
        name="Wildfire Detection Count",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="detections",
        icon="mdi:fire",
    ),
    SensorEntityDescription(
        key="vegetation_index",
        name="Vegetation Index (NDVI)",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="NDVI",
        icon="mdi:leaf",
    ),
    SensorEntityDescription(
        key="satellite_imagery_status",
        name="Satellite Imagery Status",
        icon="mdi:satellite-variant",
    ),
    SensorEntityDescription(
        key="satellite_data_quality",
        name="Satellite Data Quality",
        icon="mdi:check-circle",
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enhanced weather sensors."""
    enhanced_coordinator = hass.data[DOMAIN].get("enhanced_coordinator")
    
    if not enhanced_coordinator:
        _LOGGER.error("Enhanced coordinator not found")
        return
    
    # Create sensor entities
    sensors = []
    for description in WEATHER_SENSORS:
        sensor = EnhancedWeatherSensor(enhanced_coordinator, entry.entry_id, description)
        sensors.append(sensor)
    
    # Add specialized sensors
    sensors.extend([
        WeatherTrendSensor(enhanced_coordinator, entry.entry_id, "temperature_trend", "Temperature Trend"),
        WeatherTrendSensor(enhanced_coordinator, entry.entry_id, "pressure_trend", "Pressure Trend"), 
        WeatherForecastSensor(enhanced_coordinator, entry.entry_id, "tomorrow_weather", "Tomorrow's Weather"),
        WeatherSummarySensor(enhanced_coordinator, entry.entry_id, "weather_summary", "Weather Summary"),
    ])
    
    async_add_entities(sensors)

class EnhancedWeatherSensor(SensorEntity):
    """Enhanced weather sensor with comprehensive data."""
    
    def __init__(self, coordinator, entry_id: str, description: SensorEntityDescription):
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"enhanced_weather_{description.key}_{entry_id}"
        self._attr_name = description.name
        self._last_error = None
        
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
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        current = self.coordinator.data.get("current", {})
        daily = self.coordinator.data.get("daily", {})
        alerts = self.coordinator.data.get("alerts", [])
        key = self.entity_description.key
        self._last_error = None
        try:
            # Current weather data
            if key == "temperature":
                value = current.get("temperature")
                if value is None:
                    self._last_error = "Temperature data unavailable"
                    return "unknown"
                return value
            elif key == "apparent_temperature":
                value = current.get("apparent_temperature")
                if value is None:
                    self._last_error = "Apparent temperature data unavailable"
                    return "unknown"
                return value
            elif key == "heat_index":
                value = current.get("heat_index")
                if value is None:
                    self._last_error = "Heat index data unavailable"
                    return "unknown"
                return value
            elif key == "humidity":
                value = current.get("humidity")
                if value is None:
                    self._last_error = "Humidity data unavailable"
                    return "unknown"
                return value
            elif key == "pressure":
                value = current.get("pressure")
                if value is None:
                    self._last_error = "Pressure data unavailable"
                    return "unknown"
                return value
            elif key == "wind_speed":
                value = current.get("wind_speed")
                if value is None:
                    self._last_error = "Wind speed data unavailable"
                    return "unknown"
                return value
            elif key == "wind_direction":
                direction = current.get("wind_direction")
                if direction is None:
                    self._last_error = "Wind direction data unavailable"
                    return "unknown"
                return direction
            elif key == "wind_gusts":
                value = current.get("wind_gusts")
                if value is None:
                    self._last_error = "Wind gusts data unavailable"
                    return "unknown"
                return value
            elif key == "visibility":
                visibility = current.get("visibility")
                if visibility is None:
                    self._last_error = "Visibility data unavailable"
                    return "unknown"
                return visibility / 1000
            elif key == "cloud_cover":
                value = current.get("cloud_cover")
                if value is None:
                    self._last_error = "Cloud cover data unavailable"
                    return "unknown"
                return value
            elif key == "precipitation":
                value = current.get("precipitation")
                if value is None:
                    self._last_error = "Precipitation data unavailable"
                    return "unknown"
                return value
            elif key == "precipitation_probability":
                value = current.get("precipitation_probability")
                if value is None:
                    self._last_error = "Precipitation probability data unavailable"
                    return "unknown"
                return value
            elif key == "uv_index":
                value = current.get("uv_index")
                if value is None:
                    self._last_error = "UV index data unavailable"
                    return "unknown"
                return value
            elif key == "comfort_level":
                value = current.get("comfort_level")
                if value is None:
                    self._last_error = "Comfort level data unavailable"
                    return "unknown"
                return value
            elif key == "weather_condition_code":
                value = current.get("weather_code")
                if value is None:
                    self._last_error = "Weather code data unavailable"
                    return "unknown"
                return value
            elif key == "weather_alerts_count":
                if alerts is None:
                    self._last_error = "Weather alerts data unavailable"
                    return "unknown"
                return len(alerts)
            # Satellite-derived data
            elif key in ["sea_surface_temperature", "cloud_top_height", "satellite_solar_radiation", 
                         "aerosol_optical_depth", "wildfire_detection_count", "vegetation_index",
                         "satellite_imagery_status", "satellite_data_quality"]:
                value = self._get_satellite_value(key)
                if value is None:
                    self._last_error = f"{key.replace('_', ' ').capitalize()} data unavailable"
                    return "unknown"
                return value
            # Daily data (today's values)
            elif key.startswith("today_") and daily and "time" in daily:
                today = datetime.now().strftime("%Y-%m-%d")
                try:
                    today_idx = daily["time"].index(today)
                    if key == "today_max_temp":
                        value = daily.get("temperature_2m_max", [None])[today_idx] if len(daily.get("temperature_2m_max", [])) > today_idx else None
                        if value is None:
                            self._last_error = "Today's max temperature data unavailable"
                            return "unknown"
                        return value
                    elif key == "today_min_temp":
                        value = daily.get("temperature_2m_min", [None])[today_idx] if len(daily.get("temperature_2m_min", [])) > today_idx else None
                        if value is None:
                            self._last_error = "Today's min temperature data unavailable"
                            return "unknown"
                        return value
                    elif key == "today_precipitation_sum":
                        value = daily.get("precipitation_sum", [None])[today_idx] if len(daily.get("precipitation_sum", [])) > today_idx else None
                        if value is None:
                            self._last_error = "Today's precipitation sum data unavailable"
                            return "unknown"
                        return value
                except (ValueError, IndexError):
                    self._last_error = "Today's data unavailable"
                    return "unknown"
            # Sunrise/sunset
            elif key in ["sunrise", "sunset"] and daily and "time" in daily:
                today = datetime.now().strftime("%Y-%m-%d")
                try:
                    today_idx = daily["time"].index(today)
                    if key == "sunrise":
                        value = daily.get("sunrise", [None])[today_idx] if len(daily.get("sunrise", [])) > today_idx else None
                        if value is None:
                            self._last_error = "Sunrise data unavailable"
                            return "unknown"
                        return value
                    elif key == "sunset":
                        value = daily.get("sunset", [None])[today_idx] if len(daily.get("sunset", [])) > today_idx else None
                        if value is None:
                            self._last_error = "Sunset data unavailable"
                            return "unknown"
                        return value
                except (ValueError, IndexError):
                    self._last_error = "Sunrise/sunset data unavailable"
                    return "unknown"
            return None
        except Exception as e:
            self._last_error = f"Error: {e}"
            return "unknown"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        attributes = {
            "last_update": self.coordinator.data.get("last_update"),
            "data_sources": self.coordinator.data.get("sources", []),
        }
        
        # Add specific attributes based on sensor type
        key = self.entity_description.key
        current = self.coordinator.data.get("current", {})
        
        if key == "wind_direction":
            direction = current.get("wind_direction")
            if direction is not None:
                attributes["cardinal_direction"] = self._degrees_to_cardinal(direction)
                
        elif key == "uv_index":
            uv = current.get("uv_index")
            if uv is not None:
                attributes["uv_risk_level"] = self._get_uv_risk_level(uv)
                attributes["protection_needed"] = uv >= 3
                
        elif key == "comfort_level":
            attributes["comfort_factors"] = {
                "temperature": current.get("temperature"),
                "humidity": current.get("humidity"),
                "wind_speed": current.get("wind_speed"),
                "precipitation": current.get("precipitation", 0),
            }
            
        elif key == "weather_alerts_count":
            alerts = self.coordinator.data.get("alerts", [])
            if alerts:
                attributes["alert_types"] = list(set(alert.get("type") for alert in alerts))
                attributes["highest_severity"] = self._get_highest_severity(alerts)
        
        # Add error if present
        if self._last_error:
            attributes["error"] = self._last_error
        
        return attributes
    
    def _degrees_to_cardinal(self, degrees: float) -> str:
        """Convert wind direction degrees to cardinal direction."""
        if degrees is None:
            return "Unknown"
            
        directions = [
            "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
        ]
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def _get_uv_risk_level(self, uv_index: float) -> str:
        """Get UV risk level description."""
        if uv_index <= 2:
            return "Low"
        elif uv_index <= 5:
            return "Moderate"
        elif uv_index <= 7:
            return "High"
        elif uv_index <= 10:
            return "Very High"
        else:
            return "Extreme"
    
    def _get_highest_severity(self, alerts: list) -> str:
        """Get the highest severity level from alerts."""
        severities = [alert.get("severity", "low") for alert in alerts]
        if "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        elif "low" in severities:
            return "low"
        return "unknown"

    def _get_satellite_value(self, key: str):
        """Get satellite-derived sensor values."""
        if not self.coordinator.data:
            return None
        
        current = self.coordinator.data.get("current", {})
        
        # Return satellite product values from coordinator
        return current.get(key, None)

class WeatherTrendSensor(SensorEntity):
    """Sensor for weather trends and changes."""
    
    def __init__(self, coordinator, entry_id: str, trend_type: str, name: str):
        self.coordinator = coordinator
        self._trend_type = trend_type
        self._attr_name = name
        self._attr_unique_id = f"weather_trend_{trend_type}_{entry_id}"
        self._attr_icon = "mdi:chart-line"
        self._previous_values = []
        
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
    def native_value(self) -> str:
        """Return the trend direction."""
        current = self.coordinator.data.get("current", {})
        
        if self._trend_type == "temperature_trend":
            current_value = current.get("temperature")
        elif self._trend_type == "pressure_trend":
            current_value = current.get("pressure")
        else:
            return "unknown"
            
        if current_value is None:
            return "unknown"
            
        # Store recent values for trend calculation
        self._previous_values.append(current_value)
        if len(self._previous_values) > 6:  # Keep last 6 readings (1 hour)
            self._previous_values.pop(0)
            
        if len(self._previous_values) < 3:
            return "insufficient_data"
            
        # Calculate trend
        recent_avg = sum(self._previous_values[-3:]) / 3
        older_avg = sum(self._previous_values[:-3]) / max(1, len(self._previous_values[:-3]))
        
        difference = recent_avg - older_avg
        
        if self._trend_type == "temperature_trend":
            threshold = 0.5  # 0.5°C
        else:  # pressure_trend
            threshold = 1.0  # 1 hPa
            
        if difference > threshold:
            return "rising"
        elif difference < -threshold:
            return "falling"
        else:
            return "steady"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return trend attributes."""
        current = self.coordinator.data.get("current", {})
        
        attributes = {
            "trend_type": self._trend_type,
            "current_value": current.get(self._trend_type.replace("_trend", "")),
            "data_points": len(self._previous_values),
            "last_update": self.coordinator.data.get("last_update"),
        }
        
        if len(self._previous_values) >= 2:
            attributes["change_1h"] = self._previous_values[-1] - self._previous_values[0]
            
        return attributes

class WeatherForecastSensor(SensorEntity):
    """Sensor for tomorrow's weather forecast."""
    
    def __init__(self, coordinator, entry_id: str, forecast_type: str, name: str):
        self.coordinator = coordinator
        self._forecast_type = forecast_type
        self._attr_name = name
        self._attr_unique_id = f"weather_forecast_{forecast_type}_{entry_id}"
        self._attr_icon = "mdi:calendar-today"
        
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
    def native_value(self) -> str:
        """Return tomorrow's weather condition."""
        daily = self.coordinator.data.get("daily", {})
        
        if not daily or "time" not in daily:
            return "unknown"
            
        # Get tomorrow's date
        tomorrow = datetime.now().strftime("%Y-%m-%d")
        try:
            # This is a simplified version - you'd want to add proper date handling
            tomorrow_idx = 1  # Assuming index 1 is tomorrow
            
            if "weather_code" in daily and len(daily["weather_code"]) > tomorrow_idx:
                weather_code = daily["weather_code"][tomorrow_idx]
                # Map weather code to condition
                weather_map = {
                    0: "sunny", 1: "partly_cloudy", 2: "partly_cloudy", 3: "cloudy",
                    45: "fog", 48: "fog", 51: "light_rain", 53: "rain", 55: "heavy_rain",
                    61: "light_rain", 63: "rain", 65: "heavy_rain", 71: "light_snow",
                    73: "snow", 75: "heavy_snow", 95: "thunderstorm"
                }
                return weather_map.get(weather_code, "unknown")
                
        except (ValueError, IndexError):
            pass
            
        return "unknown"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return tomorrow's forecast attributes."""
        daily = self.coordinator.data.get("daily", {})
        attributes = {
            "forecast_day": "tomorrow",
            "last_update": self.coordinator.data.get("last_update"),
        }
        
        if daily and "time" in daily:
            try:
                tomorrow_idx = 1
                if len(daily.get("temperature_2m_max", [])) > tomorrow_idx:
                    attributes["max_temperature"] = daily["temperature_2m_max"][tomorrow_idx]
                if len(daily.get("temperature_2m_min", [])) > tomorrow_idx:
                    attributes["min_temperature"] = daily["temperature_2m_min"][tomorrow_idx]
                if len(daily.get("precipitation_sum", [])) > tomorrow_idx:
                    attributes["precipitation_sum"] = daily["precipitation_sum"][tomorrow_idx]
                if len(daily.get("precipitation_probability_max", [])) > tomorrow_idx:
                    attributes["precipitation_probability"] = daily["precipitation_probability_max"][tomorrow_idx]
            except IndexError:
                pass
                
        return attributes

class WeatherSummarySensor(SensorEntity):
    """Sensor providing weather summary and recommendations."""
    
    def __init__(self, coordinator, entry_id: str, summary_type: str, name: str):
        self.coordinator = coordinator
        self._summary_type = summary_type
        self._attr_name = name
        self._attr_unique_id = f"weather_summary_{summary_type}_{entry_id}"
        self._attr_icon = "mdi:weather-partly-cloudy"
        
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
    def native_value(self) -> str:
        """Return weather summary."""
        current = self.coordinator.data.get("current", {})
        alerts = self.coordinator.data.get("alerts", [])
        
        # Generate summary based on current conditions
        temp = current.get("temperature")
        condition = current.get("weather_code")
        comfort = current.get("comfort_level", "unknown")
        
        summary_parts = []
        
        if temp is not None:
            if temp >= 30:
                summary_parts.append("Hot weather")
            elif temp >= 25:
                summary_parts.append("Warm weather")  
            elif temp >= 15:
                summary_parts.append("Mild weather")
            elif temp >= 5:
                summary_parts.append("Cool weather")
            else:
                summary_parts.append("Cold weather")
        
        if comfort != "unknown":
            summary_parts.append(f"comfort level: {comfort}")
            
        if alerts:
            summary_parts.append(f"{len(alerts)} active alert(s)")
            
        return ", ".join(summary_parts) if summary_parts else "Weather data unavailable"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return detailed summary attributes."""
        current = self.coordinator.data.get("current", {})
        alerts = self.coordinator.data.get("alerts", [])
        
        # Generate recommendations
        recommendations = []
        
        temp = current.get("temperature")
        uv = current.get("uv_index")
        precipitation_prob = current.get("precipitation_probability", 0)
        wind_speed = current.get("wind_speed", 0)
        
        if temp is not None:
            if temp >= 35:
                recommendations.append("Stay hydrated and avoid prolonged sun exposure")
            elif temp <= 0:
                recommendations.append("Dress warmly and protect against frostbite")
                
        if uv and uv >= 6:
            recommendations.append("Use sunscreen and protective clothing")
            
        if precipitation_prob >= 70:
            recommendations.append("Carry an umbrella or raincoat")
            
        if wind_speed >= 30:
            recommendations.append("Secure loose objects and avoid high-rise areas")
        
        attributes = {
            "current_temperature": temp,
            "comfort_level": current.get("comfort_level"),
            "active_alerts": len(alerts),
            "recommendations": recommendations,
            "weather_quality": self._assess_weather_quality(current),
            "outdoor_activity_suitability": self._assess_outdoor_suitability(current),
            "last_update": self.coordinator.data.get("last_update"),
        }
        
        return attributes
    
    def _assess_weather_quality(self, current: Dict) -> str:
        """Assess overall weather quality."""
        score = 0
        
        temp = current.get("temperature", 20)
        humidity = current.get("humidity", 50)
        precipitation = current.get("precipitation", 0)
        wind_speed = current.get("wind_speed", 10)
        
        # Temperature scoring
        if 18 <= temp <= 26:
            score += 25
        elif 15 <= temp <= 30:
            score += 15
        elif 10 <= temp <= 35:
            score += 5
            
        # Humidity scoring  
        if 40 <= humidity <= 60:
            score += 25
        elif 30 <= humidity <= 70:
            score += 15
        elif 20 <= humidity <= 80:
            score += 5
            
        # Precipitation penalty
        if precipitation == 0:
            score += 25
        elif precipitation <= 2:
            score += 10
            
        # Wind scoring
        if 5 <= wind_speed <= 20:
            score += 25
        elif wind_speed <= 30:
            score += 15
        elif wind_speed <= 40:
            score += 5
            
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "poor"
    
    def _assess_outdoor_suitability(self, current: Dict) -> str:
        """Assess suitability for outdoor activities."""
        temp = current.get("temperature", 20)
        precipitation = current.get("precipitation", 0)
        wind_speed = current.get("wind_speed", 10)
        uv = current.get("uv_index", 3)
        
        # Basic suitability assessment
        if precipitation > 5:
            return "not_suitable"
        elif wind_speed > 40:
            return "not_suitable"
        elif temp < -5 or temp > 40:
            return "caution_required"
        elif precipitation > 0 or wind_speed > 25 or uv > 9:
            return "moderate"
        else:
            return "suitable"
