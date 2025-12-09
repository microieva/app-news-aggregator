'use client'; 

import React, { useEffect } from 'react';
import { useWeather } from '@/contexts/WeatherContext';
import { DailyForecast } from '@/types/weather';
import { formatDate, getWeatherIcon, getWeekday } from '@/utils/utils';

export const WeeklyForecast = () => {
  const { forecast, refreshForecast} = useWeather();
  
  useEffect(()=>{
    refreshForecast();
  }, [forecast])

  return (
      <div className='pl-2 md:pl-4'>
        <h3 className="text-md mb-8 border-b">7-Day Forecast</h3>
        <div>
          {forecast?.forecast?.map((day:DailyForecast, index:any) => (
            <div key={index} className="grid grid-cols-[20%_80%] grid-rows-[0.8rem]">
              <div>
                <p className="text-secondary text-xs font-extrabold whitespace-nowrap">{index === 0 ? 'Today' : formatDate(day.date, false)}</p>
                <p className="text-secondary text-xs">{getWeekday(day.date)}</p>
              </div>
              <p className="pl-4 font-bold whitespace-nowrap">
                {day.condition.text}
              </p>
              <div className="divider w-full before:bg-secondary after:bg-secondary"></div>
              <div className="flex flex-row gap-2 ml-4 text-sm">
                <div className="flex items-center space-x-2">
                    <img 
                      src={getWeatherIcon(day.condition.code, forecast.current.is_day)}
                      alt={day.condition.text}
                      className="w-4 h-4"
                    />
                </div>

                <div className="flex items-center space-x-1">
                  <img 
                      src="/drop.svg"
                      alt={day.condition.text}
                      className="w-3 h-3"
                    />
                  <span className="text-xs">{day.chance_of_rain}%</span>
                </div>

                <div className="flex space-x-2 items-center">
                  <div className="flex items-center space-x-1">
                    <img 
                        src="/arrow.svg"
                        alt={day.condition.text}
                        className="w-3 h-3"
                      />
                    <p className="text-xs">{Math.round(day.max_temp_c)}°</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <img 
                        src="/arrow.svg"
                        alt={day.condition.text}
                        className="w-3 h-3 rotate-180"
                      />
                    <p className="text-xs">{Math.round(day.min_temp_c)}°</p> 
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>  
      </div>
  );
};
