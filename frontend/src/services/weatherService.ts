import { WeatherResponse, WeeklyForecastResponse } from '@/types/weather';
import { apiClient } from '@/utils/client';

export const weatherService = {

  async getCurrentWeather(location?: string): Promise<WeatherResponse> {
    const params = new URLSearchParams();
    if (location) {
      params.append('location', location);
    }
    const response:WeatherResponse = await apiClient.get(`/weather/current?${params}`);
    return response;
  },

  async getWeatherByLocation(location: string): Promise<WeatherResponse> {
    const response:WeatherResponse = await apiClient.get(`/weather/location/${encodeURIComponent(location)}`);
    return response;
  },

  async getWeeklyForecast(location?: string, days: number = 7): Promise<WeeklyForecastResponse> {
    const params = new URLSearchParams();
    if (location) {
      params.append('location', location);
    }
    params.append('days', days.toString());
    
    const response:WeeklyForecastResponse = await apiClient.get(`/weather/forecast?${params}`);
    return response;
  },
};
