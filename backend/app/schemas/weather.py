from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class WeatherCondition(BaseModel):
    text: str
    icon: str
    code: int

class Location(BaseModel):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime: str

class AirQuality(BaseModel):
    co: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    us_epa_index: Optional[int] = None
    gb_defra_index: Optional[int] = None

class CurrentWeather(BaseModel):
    temp_c: float
    temp_f: float
    is_day: bool
    condition: WeatherCondition
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    precip_mm: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    vis_km: float
    uv: float
    gust_kph: float
    air_quality: Optional[AirQuality] = None

class WeatherResponse(BaseModel):
    location: Location
    current: CurrentWeather



class ForecastDay(BaseModel):
    date: str
    date_epoch: int
    day: Dict[str, Any]  # Contains max/min temp, condition, etc.
    astro: Dict[str, Any]
    hour: List[Dict[str, Any]]

class ForecastResponse(BaseModel):
    location: Location
    current: CurrentWeather
    forecast: Dict[str, List[ForecastDay]]

# Simplified forecast for frontend
class DailyForecast(BaseModel):
    date: str
    max_temp_c: float
    min_temp_c: float
    condition: WeatherCondition
    chance_of_rain: int
    uv: float

class WeeklyForecastResponse(BaseModel):
    location: Location
    current: CurrentWeather
    forecast: List[DailyForecast]