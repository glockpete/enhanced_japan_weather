"""Satellite Camera platform for Enhanced Japan Weather integration."""
from __future__ import annotations

import logging
import io
from typing import Any
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None

_LOGGER = logging.getLogger(__name__)

SATELLITE_CAMERAS = [
    {
        "key": "himawari_japan_region",
        "name": "Himawari Japan Region Satellite",
        "description": "High-resolution Japan region satellite imagery"
    },
    {
        "key": "himawari_full_disk",
        "name": "Himawari Full Disk Satellite",
        "description": "Full disk Asia-Pacific satellite imagery"
    },
    {
        "key": "himawari_true_color",
        "name": "Himawari True Color Satellite",
        "description": "True color satellite imagery"
    },
    {
        "key": "himawari_infrared",
        "name": "Himawari Infrared Satellite",
        "description": "Infrared satellite imagery"
    },
    {
        "key": "himawari_water_vapor",
        "name": "Himawari Water Vapor Satellite",
        "description": "Water vapor satellite imagery"
    },
    {
        "key": "weather_radar_composite",
        "name": "Weather Radar Composite",
        "description": "Weather radar composite imagery"
    },
    {
        "key": "sea_surface_temperature_map",
        "name": "Sea Surface Temperature Map",
        "description": "Sea surface temperature from satellite"
    },
    {
        "key": "cloud_analysis_composite",
        "name": "Cloud Analysis Composite",
        "description": "Cloud analysis from multi-spectral satellite data"
    },
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up satellite camera entities for Enhanced Japan Weather."""
    entities = [
        SatelliteCameraEntity(camera["key"], camera["name"], camera["description"]) for camera in SATELLITE_CAMERAS
    ]
    async_add_entities(entities)

class SatelliteCameraEntity(Camera):
    def __init__(self, key: str, name: str, description: str):
        super().__init__()
        self._attr_name = name
        self._attr_unique_id = f"enhanced_japan_weather_{key}_camera"
        self._key = key
        self._description = description
        self._attr_supported_features = CameraEntityFeature.ON_OFF
        self._attr_is_streaming = False
        self._attr_is_on = True

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "enhanced_japan_weather")},
            name="Enhanced Japan Weather",
            manufacturer="Enhanced Weather Team",
            model="Satellite Camera",
            sw_version="2.1.0",
        )

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return a real JMA Himawari image for each type, else a simulated PNG image."""
        import aiohttp
        from datetime import datetime
        # Mapping of camera key to JMA endpoint
        jma_urls = {
            "himawari_japan_region": "https://www.data.jma.go.jp/mscweb/data/himawari/img/japan/b03/latest.jpg",  # Visible
            "himawari_full_disk": "https://www.data.jma.go.jp/mscweb/data/himawari/img/fd/b03/latest.jpg",  # Visible
            "himawari_true_color": "https://www.data.jma.go.jp/mscweb/data/himawari/img/japan/tcr/latest.jpg",  # True Color
            "himawari_infrared": "https://www.data.jma.go.jp/mscweb/data/himawari/img/japan/b13/latest.jpg",  # Infrared
            "himawari_water_vapor": "https://www.data.jma.go.jp/mscweb/data/himawari/img/japan/b08/latest.jpg",  # Water Vapor
            "cloud_analysis_composite": "https://www.data.jma.go.jp/mscweb/data/himawari/img/japan/cth/latest.jpg",  # Cloud Top Height
            # The following are not direct JMA images, fallback to simulated:
            # "weather_radar_composite": "https://www.jma.go.jp/bosai/himawari/data/satimg/target-timeseries/target-00.png",
            # "sea_surface_temperature_map": "",
        }
        url = jma_urls.get(self._key)
        if url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            return await resp.read()
            except Exception as e:
                _LOGGER.warning(f"Failed to fetch JMA Himawari image for {self._key}: {e}")
        # Simulated image for all other cameras (and fallback)
        if Image is None:
            _LOGGER.warning("Pillow is not installed, cannot generate camera image.")
            return None
        img_width = width or 480
        img_height = height or 320
        img = Image.new("RGB", (img_width, img_height), color=(30, 60, 120))
        draw = ImageDraw.Draw(img)
        text = self._attr_name
        font = None
        if ImageFont is not None:
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except Exception:
                font = ImageFont.load_default()
        text_width, text_height = draw.textsize(text, font=font)
        draw.text(
            ((img_width - text_width) / 2, (img_height - text_height) / 2),
            text,
            fill=(255, 255, 255),
            font=font,
        )
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @property
    def brand(self) -> str:
        return "JMA Himawari (Simulated)"

    @property
    def model(self) -> str:
        return self._attr_name

    @property
    def is_on(self) -> bool:
        return True

    @property
    def is_streaming(self) -> bool:
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "description": self._description,
            "camera_key": self._key,
        } 