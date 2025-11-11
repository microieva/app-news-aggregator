import React from 'react';
import { useWeather } from '@/contexts/WeatherContext';
import { WeeklyForecast } from './WeeklyForecast';
import { CurrentWeather } from './CurrentWeather';

interface WeatherBlockProps {
  location?: string;
}

export const WeatherBlock: React.FC<WeatherBlockProps> = () => {
  const { error, loading } = useWeather();

  if (loading) {
    return (
      <div className="card">
        <p className="text-gray-600">Loading..</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
          <p className="text-gray-600">Weather data unavailable</p>
      </div>
    );
  }

  return (
    <div className="flex flex-row items-start gap-2 p-4 h-full">
      <div className='border w-full h-full bg-[var(--np-color-primary)]'>
        <CurrentWeather/>
      </div>

      <div className='w-full h-full'>
        <WeeklyForecast/>
      </div>
    </div>
  );
};
