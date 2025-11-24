import { createContext, useContext, ReactNode } from 'react';
import { weatherService } from '@/services/weatherService';
import { ApiError } from '@/types/api';
import { WeatherResponse, WeeklyForecastResponse } from '@/types/weather';
import useSWR from 'swr';

interface WeatherContextType {
  forecast: WeeklyForecastResponse | null;
  weather: WeatherResponse | null;
  loading: boolean;
  error: ApiError | null;
  refreshData: () => void;
  refreshWeather: () => void;
  refreshForecast: () => void;
  getWeatherForLocation: (location: string) => Promise<void>;
  currentLocation: string | null;
}

const WeatherContext = createContext<WeatherContextType | undefined>(undefined);

interface WeatherProviderProps {
  children: ReactNode;
  initialWeather?: WeatherResponse | null;
  initialForecast?: WeeklyForecastResponse | null;
}

const fetchers = {
  getCurrentWeather: async (): Promise<WeatherResponse | null> => {
    try {
      return await weatherService.getCurrentWeather();
    } catch (error) {
      console.error('Failed to fetch current weather:', error);
      return null;
    }
  },
  
  getWeatherByLocation: async (location: string): Promise<WeatherResponse | null> => {
    try {
      return await weatherService.getWeatherByLocation(location);
    } catch (error) {
      console.error('Failed to fetch weather for location:', error);
      return null;
    }
  },
  
  getWeeklyForecast: async (): Promise<WeeklyForecastResponse | null> => {
    try {
      return await weatherService.getWeeklyForecast();
    } catch (error) {
      console.error('Failed to fetch weekly forecast:', error);
      return null;
    }
  },
};

export function WeatherProvider({ 
  children, 
  initialWeather = null,
  initialForecast = null 
}: WeatherProviderProps) {
  
  const {
    data: forecast,
    error: forecastError,
    mutate: mutateForecast,
    isLoading: forecastLoading,
  } = useSWR<WeeklyForecastResponse | null>(
    'weekly-forecast',
    fetchers.getWeeklyForecast,
    {
      fallbackData: initialForecast, 
      revalidateOnFocus: false,
      dedupingInterval: 3600000, // 1 hour for forecast
      refreshInterval: 3600000,
      onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
        if (error.status === 404 || error.status === 500) return;
        setTimeout(() => revalidate({ retryCount }), 5000);
      },
    }
  );

  const {
    data: weather,
    error: weatherError,
    mutate: mutateWeather,
    isLoading: weatherLoading,
  } = useSWR<WeatherResponse | null>(
    'current-weather',
    fetchers.getCurrentWeather,
    {
      fallbackData: initialWeather,
      revalidateOnFocus: false,
      // dedupingInterval: 300000, // 5 minutes
      // refreshInterval: 300000,
      onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
        if (error.status === 404 || error.status === 500) return;
        setTimeout(() => revalidate({ retryCount }), 5000);
      },
    }
  );

  const refreshWeather = () => {
    mutateWeather();
  };

  const refreshForecast = () => {
    mutateForecast();
  };

  const refreshData = () => {
    mutateWeather();
    mutateForecast();
  };

  const getWeatherForLocation = async (location: string) => {
    try {
      const locationWeather = await fetchers.getWeatherByLocation(location);
      if (locationWeather) {
        mutateWeather(locationWeather, false);
      }
    } catch (error) {
      console.error('Failed to fetch weather for location:', location, error);
      throw error;
    }
  };

  const value: WeatherContextType = {
    forecast: forecast || null,
    weather: weather || null,
    loading: weatherLoading || forecastLoading,
    error: weatherError || forecastError || null,
    refreshWeather,
    refreshForecast,
    refreshData,
    getWeatherForLocation,
    currentLocation: weather?.location?.name || null, 
  };

  return (
    <WeatherContext.Provider value={value}>
      {children}
    </WeatherContext.Provider>
  );
}

export function useWeather() {
  const context = useContext(WeatherContext);

  if (context === undefined) {
    throw new Error('useWeather must be used within a WeatherProvider');
  }
  return context;
}