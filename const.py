"""Constants for Enhanced Japan Weather integration."""

DOMAIN = "japan_weather"

# Default coordinates (Tokyo)
DEFAULT_LATITUDE = 35.6762
DEFAULT_LONGITUDE = 139.6503

# Update intervals (in seconds)
DEFAULT_UPDATE_INTERVAL = 600  # 10 minutes
FAST_UPDATE_INTERVAL = 300     # 5 minutes during severe weather

# Weather alert thresholds
ALERT_THRESHOLDS = {
    "temperature_high": 35.0,    # °C
    "temperature_low": -10.0,    # °C
    "wind_speed_high": 50.0,     # km/h
    "wind_gust_high": 70.0,      # km/h
    "precipitation_prob": 80.0,  # %
    "uv_index_high": 8.0,        # UV index
}

# Weather comfort scoring
COMFORT_RANGES = {
    "temperature_optimal": (20, 25),   # °C
    "temperature_good": (15, 30),      # °C
    "humidity_optimal": (40, 60),      # %
    "humidity_good": (30, 70),         # %
    "wind_optimal": (5, 15),           # km/h
    "wind_good": (0, 25),              # km/h
}

# Data quality settings
CACHE_TIMEOUT = 300  # 5 minutes
MAX_RETRY_ATTEMPTS = 3
REQUEST_TIMEOUT = 30  # seconds

# Sensor configuration
SENSOR_UPDATE_BUFFER = 6  # Keep last 6 readings for trend analysis

# Weather codes mapping (WMO codes used by Open-Meteo)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate", 
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy intensity", 
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate", 
    82: "Rain showers: Violent",
    85: "Snow showers slight",
    86: "Snow showers heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

# Satellite imagery configuration
SATELLITE_UPDATE_INTERVAL = 600  # 10 minutes
SATELLITE_IMAGE_CACHE_TIME = 300  # 5 minutes
SATELLITE_MAX_RETRY_ATTEMPTS = 3

# Satellite data quality thresholds
SATELLITE_QUALITY_THRESHOLDS = {
    "cloud_coverage_limit": 90.0,    # % - above this, optical data unreliable
    "sun_elevation_min": 10.0,       # degrees - minimum for visible imagery
    "data_age_limit": 3600,          # seconds - max age for usable data
}

# Available satellite bands and products
SATELLITE_BANDS = {
    "visible": {"wavelength": "0.64μm", "resolution": "1km", "description": "Visible light"},
    "near_infrared": {"wavelength": "0.86μm", "resolution": "1km", "description": "Near-infrared"},
    "water_vapor": {"wavelength": "6.2μm", "resolution": "2km", "description": "Water vapor channel"},
    "infrared": {"wavelength": "10.4μm", "resolution": "2km", "description": "Thermal infrared"},
    "longwave_infrared": {"wavelength": "12.4μm", "resolution": "2km", "description": "Longwave infrared"}
}

# Satellite data sources
SATELLITE_DATA_SOURCES = {
    "himawari_8": {
        "name": "Himawari-8",
        "operator": "JMA",
        "coverage": "Asia-Pacific",
        "resolution": "0.5-2km",
        "update_frequency": "10-60min"
    },
    "himawari_9": {
        "name": "Himawari-9", 
        "operator": "JMA",
        "coverage": "Asia-Pacific", 
        "resolution": "0.5-2km",
        "update_frequency": "10-60min"
    }
}
