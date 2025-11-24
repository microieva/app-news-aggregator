import httpx
from fastapi import APIRouter, HTTPException, Request
from app.schemas import DailyForecast, WeatherCondition, WeatherResponse, WeeklyForecastResponse
from app.services.weather_service import weather_service
from typing import Optional

router = APIRouter()

@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    request: Request,
    location: Optional[str] = None
):
    """
    Get current weather for a location.
    If no location provided, uses client IP for location detection.
    """
    try:
        if not location:
            client_ip = request.client.host
            # For dev
            if client_ip in ["127.0.0.1", "::1"]:
                location = "auto:ip"  # auto IP detection
            else:
                location = client_ip
        
        weather_data = await weather_service.get_current_weather(location)
        
        if not weather_data:
            raise HTTPException(status_code=404, detail="Weather data not found")
            
        return weather_data
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail="Weather service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/location/{location}")
async def get_weather_by_location(location: str):
    """Get weather for a specific location (city, zipcode, etc.)"""
    try:
        weather_data = await weather_service.get_current_weather(location)
        return weather_data
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Weather service unavailable")
    


@router.get("/forecast", response_model=WeeklyForecastResponse)
async def get_weekly_forecast(
    request: Request,
    location: Optional[str] = None,
    days: int = 7
):
    """
    Get weekly weather forecast for a location.
    If no location provided, uses client IP for location detection.
    """
    try:
        # Use provided location or fall back to client IP
        if not location:
            client_ip = request.client.host
            if client_ip in ["127.0.0.1", "::1"]:
                location = "auto:ip"
            else:
                location = client_ip
        
        forecast_data = await weather_service.get_forecast(location, days)
        
        if not forecast_data:
            raise HTTPException(status_code=404, detail="Forecast data not found")
        
        simplified_forecast = []
        for day_data in forecast_data["forecast"]["forecastday"]:
            simplified_forecast.append(DailyForecast(
                date=day_data["date"],
                max_temp_c=day_data["day"]["maxtemp_c"],
                min_temp_c=day_data["day"]["mintemp_c"],
                condition=WeatherCondition(
                    text=day_data["day"]["condition"]["text"],
                    icon=day_data["day"]["condition"]["icon"],
                    code=day_data["day"]["condition"]["code"]
                ),
                chance_of_rain=day_data["day"]["daily_chance_of_rain"],
                uv=day_data["day"]["uv"]
            ))
        
        return WeeklyForecastResponse(
            location=forecast_data["location"],
            current=forecast_data["current"],
            forecast=simplified_forecast
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail="Weather service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")