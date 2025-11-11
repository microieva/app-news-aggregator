import React, { useEffect } from 'react';
import { useWeather } from '@/contexts/WeatherContext';
import { DailyForecast } from '@/types/weather';
import { formatDate, getWeatherIcon, getWeekday } from '@/utils/utils';

export const WeeklyForecast = () => {
  const { forecast, refreshForecast} = useWeather();
  
  useEffect(()=>{
    if (!forecast) refreshForecast();
  }, [forecast])

  return (
      <div className='pl-4'>
        <h3 className="text-lg mb-2">7-Day Forecast</h3>
        <div className="space-y-1">
          {forecast?.forecast?.map((day:DailyForecast, index:any) => (
              <div key={index} className="grid grid-cols-[20%_80%] grid-rows-[1rem]">
                <div className="text-sm">
                  <p className="text-gray-600">{index === 0 ? 'Today' : formatDate(day.date)}</p>
                  <p className="text-gray-600 text-xs">{getWeekday(day.date)}</p>
                </div>
                <div className="pl-4 font-bold">
                  {day.condition.text}
                </div>
                <div className="divider w-full before:bg-gray-600 after:bg-gray-600"></div>
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
                      <span className="text-sm">{Math.round(day.max_temp_c)}°</span>

                    </div>
                    <div className="flex items-center space-x-1">
                      <img 
                          src="/arrow.svg"
                          alt={day.condition.text}
                          className="w-3 h-3 rotate-180"
                        />
                      <span className="text-sm">{Math.round(day.min_temp_c)}°</span>
                      
                    </div>
                  </div>
                </div>
              </div>
          ))}
        </div>  
      </div>
  );
};
