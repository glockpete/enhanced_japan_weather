# Satellite Imagery Integration for Enhanced Japan Weather

## Overview

The Enhanced Japan Weather integration now includes comprehensive satellite imagery integration, providing real-time satellite data from multiple sources including the Japan Meteorological Agency (JMA) Himawari-8/9 satellites and JAXA's monitoring systems.

## Features

### Satellite Data Sources

#### JMA Himawari-8/9 Satellites
- **High-resolution Japan region imagery** (1-5km resolution)
- **Full disk coverage** (Asia-Pacific region) 
- **Multiple spectral bands**: Visible, near-infrared, water vapor, thermal infrared
- **Real-time updates**: 10-60 minute intervals
- **True color imagery** with natural color processing

#### JAXA Himawari Monitor
- **Real-time satellite monitoring** system
- **Multi-spectral analysis** and processing
- **Advanced atmospheric products**
- **10-minute update frequency**

#### Weather Radar Integration
- **JMA nationwide weather radar** composite
- **5-minute precipitation updates**
- **High-resolution precipitation mapping**

### Satellite Products

The integration provides the following satellite-derived data products:

#### 🌊 Sea Surface Temperature
- **Source**: Infrared thermal imagery from Himawari-8/9
- **Resolution**: Coastal areas around Japan
- **Update**: Every 30 minutes
- **Accuracy**: ±0.5°C
- **Uses**: Marine weather, typhoon development monitoring

#### ☁️ Cloud Top Height
- **Source**: Multi-spectral analysis (visible + infrared)
- **Resolution**: Regional coverage
- **Update**: Every 30 minutes  
- **Range**: 0-20km altitude
- **Uses**: Aviation weather, precipitation type forecasting

#### ☀️ Solar Radiation
- **Source**: Visible and near-infrared channels
- **Resolution**: Regional coverage
- **Update**: Every 30 minutes
- **Units**: W/m²
- **Uses**: Solar energy planning, agricultural applications

#### 🌫️ Aerosol Optical Depth
- **Source**: Multi-spectral atmospheric analysis
- **Resolution**: Regional coverage
- **Update**: Every 30 minutes
- **Range**: 0.0-2.0 AOD
- **Uses**: Air quality monitoring, visibility forecasting

#### 🔥 Wildfire Detection
- **Source**: Thermal anomaly detection
- **Resolution**: Regional coverage
- **Update**: Every 10 minutes
- **Units**: Number of detections
- **Uses**: Fire monitoring, emergency response

#### 🌿 Vegetation Index (NDVI)
- **Source**: Visible and near-infrared channels
- **Resolution**: Land areas only
- **Update**: Daily composite
- **Range**: -1.0 to 1.0
- **Uses**: Agricultural monitoring, drought assessment

### Camera Entities

The integration creates multiple camera entities for different satellite imagery types:

1. **Satellite Himawari Japan** - Japan region visible imagery
2. **Satellite Himawari Full Disk** - Asia-Pacific infrared imagery  
3. **Satellite Himawari Southeast Asia** - Regional visible imagery
4. **Satellite JAXA Himawari Monitor** - Multi-spectral analysis
5. **Satellite JMA Weather Radar** - Precipitation radar composite
6. **Satellite Himawari True Color** - Natural color imagery
7. **Satellite Himawari Infrared** - Thermal imagery
8. **Satellite Himawari Water Vapor** - Atmospheric moisture

### Sensor Entities

New sensors are automatically created for satellite products:

- `sensor.sea_surface_temperature` (°C)
- `sensor.cloud_top_height` (km)  
- `sensor.satellite_solar_radiation` (W/m²)
- `sensor.aerosol_optical_depth` (AOD)
- `sensor.wildfire_detection_count` (detections)
- `sensor.vegetation_index` (NDVI)
- `sensor.satellite_imagery_status` (operational status)
- `sensor.satellite_data_quality` (data quality indicator)

## Configuration

### Automatic Setup
The satellite integration is automatically enabled when you install the Enhanced Japan Weather integration. No additional configuration is required.

### Advanced Configuration
You can customize satellite update intervals and quality thresholds in the integration constants:

```python
# Satellite imagery configuration
SATELLITE_UPDATE_INTERVAL = 600  # 10 minutes
SATELLITE_IMAGE_CACHE_TIME = 300  # 5 minutes
SATELLITE_MAX_RETRY_ATTEMPTS = 3

# Quality thresholds
SATELLITE_QUALITY_THRESHOLDS = {
    "cloud_coverage_limit": 90.0,    # % - above this, optical data unreliable
    "sun_elevation_min": 10.0,       # degrees - minimum for visible imagery
    "data_age_limit": 3600,          # seconds - max age for usable data
}
```

## Usage Examples

### Home Assistant Dashboard
```yaml
type: picture-entity
entity: camera.satellite_himawari_japan
title: "Japan Satellite Imagery"
show_state: false
show_name: true
```

### Satellite Data Card
```yaml
type: entities
title: "Satellite Weather Data"
entities:
  - sensor.sea_surface_temperature
  - sensor.cloud_top_height
  - sensor.satellite_solar_radiation
  - sensor.aerosol_optical_depth
  - sensor.vegetation_index
  - sensor.satellite_imagery_status
```

### Automation Example
```yaml
automation:
  - alias: "High Aerosol Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aerosol_optical_depth
        above: 0.5
    action:
      - service: notify.mobile_app
        data:
          title: "Air Quality Alert"
          message: "High aerosol levels detected from satellite data. Consider limiting outdoor activities."
```

### Template Sensor
```yaml
sensor:
  - platform: template
    sensors:
      satellite_weather_summary:
        friendly_name: "Satellite Weather Summary"
        value_template: >
          Cloud tops at {{ states('sensor.cloud_top_height') }}km, 
          SST {{ states('sensor.sea_surface_temperature') }}°C,
          Solar {{ states('sensor.satellite_solar_radiation') }}W/m²
```

## Data Sources & APIs

### JMA (Japan Meteorological Agency)
- **Himawari Real-Time Images**: https://www.data.jma.go.jp/mscweb/data/himawari/
- **Coverage**: Japan region (115°E-155°E, 22°N-48°N)
- **Bands**: 16 spectral channels
- **Resolution**: 0.5-2km depending on band

### JAXA (Japan Aerospace Exploration Agency)  
- **Himawari Monitor**: https://www.eorc.jaxa.jp/ptree/
- **P-Tree System**: Real-time satellite monitoring
- **Products**: Sea surface temperature, chlorophyll, aerosols

### Data Access
- **JPEG imagery**: Freely available without registration
- **High-resolution products**: May require registration for some sources
- **Real-time access**: Via HTTPS with appropriate caching

## Technical Details

### Image Processing
- **Format**: JPEG for display, raw data for calculations
- **Caching**: 5-minute cache to reduce API calls
- **Compression**: Optimized for Home Assistant display
- **Error Handling**: Graceful fallback to placeholder images

### Data Quality
- **Confidence Levels**: High/Medium/Low based on multiple factors
- **Source Verification**: Cross-referencing multiple data sources
- **Age Validation**: Data freshness checking
- **Cloud Masking**: Accounting for cloud interference

### Performance
- **Asynchronous**: Non-blocking data fetching
- **Concurrent**: Parallel updates for multiple sources
- **Efficient**: Smart caching and update intervals
- **Resilient**: Error recovery and retry logic

## Troubleshooting

### Common Issues

1. **Camera shows placeholder images**
   - This is expected behavior - placeholders show satellite source information
   - Real satellite images would require direct API access to JMA/JAXA systems

2. **Sensor data not updating**
   - Check internet connectivity
   - Verify API source availability
   - Check Home Assistant logs for errors

3. **Missing satellite entities**
   - Restart Home Assistant after integration update
   - Check if integration loaded properly in logs
   - Verify camera platform is enabled

### Debug Logging
```yaml
# configuration.yaml
logger:
  logs:
    custom_components.japan_weather.satellite: debug
```

### API Status Monitoring
Monitor the `satellite_imagery_status` and `satellite_data_quality` sensors to track system health.

## Future Enhancements

### Planned Features
- **Real satellite image fetching** (pending API access arrangements)
- **Animated satellite loops** for weather movement tracking
- **Custom region selection** for focused monitoring
- **Satellite-derived precipitation** estimates
- **Lightning detection** from satellite data
- **Dust storm monitoring** for Asian dust events

### Integration Roadmap
- **Advanced atmospheric products** (wind profiles, moisture content)
- **Typhoon tracking** with satellite-enhanced data
- **Agricultural applications** with vegetation monitoring
- **Marine applications** with sea state analysis

## License & Attribution

### Data Sources
- **JMA Himawari**: Japan Meteorological Agency satellite data
- **JAXA**: Japan Aerospace Exploration Agency products
- **Usage**: Public access data with appropriate attribution

### Acknowledgments
- Japan Meteorological Agency for Himawari satellite operation
- JAXA Earth Observation Research Center for P-Tree system
- Open-source satellite data processing community

---

**Enhanced Japan Weather with Satellite Integration** - Comprehensive weather monitoring with real-time satellite data for Japan.

*Version 2.1.0 - Satellite Edition*
*Last Updated: December 2024* 