import httpx
from typing import Optional, Dict, Any
from app.core import settings
from tenacity import retry, stop_after_attempt, wait_exponential

class WeatherService:
    def __init__(self):
        self.base_url = settings.WEATHER_API_URL
        self.api_key = settings.WEATHER_API_KEY
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/current.json",
                params={
                    "key": self.api_key,
                    "q": location,
                    "aqi": "yes"  # Include air quality data
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_forecast(self, location: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """Get weather forecast for specified number of days (max 14)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/forecast.json",
                params={
                    "key": self.api_key,
                    "q": location,
                    "days": min(days, 14),  # API limit
                    "aqi": "no",
                    "alerts": "no"
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_weather_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get weather for user's location based on IP"""
        return await self.get_current_weather(ip_address)

weather_service = WeatherService()