'use client'; 

import { useWeather } from "@/contexts/WeatherContext";
import { getWeatherIcon } from "@/utils/utils";
import { useEffect } from "react";

export const CurrentWeather = ()=> {
  const { weather, refreshWeather } = useWeather();

  useEffect(()=>{
    refreshWeather();
  }, [weather])
  
  
  return (
    <div className='w-full h-[42vh] md:h-full flex flex-col justify-between md:justify-evenly lg:justify-between px-2 md:px-4 bg-foreground rounded-tr-xl rounded-bl-xl'>
      <div className='mt-4'>
        <h3 className="card-title font-bold">{weather?.location.name}</h3>
        <p className="text-xs font-bold text-secondary">{weather?.location.region}, {weather?.location.country}</p>
      </div>
      {weather && 
      <>
        <div>
          <img 
            src={getWeatherIcon(weather.current.condition.code, weather.current.is_day)}
            alt={weather.current.condition.text}
            className="w-24 h-24 md:w-32 md:h-32 mx-auto"
          /> 
          <p className="text-xs mt-1 text-center">{weather.current.condition.text}</p>
        </div>
        <div className="my-0 lg:my-8">
          <p className="text-xl font-bold text-center">{weather.current.temp_c}°C</p>
          <p className="text-sm font-bold text-center text-primary">Feels like {weather.current.feelslike_c}°C</p> 
        </div>
        <div className='mx-auto mb-4'>
          <div className="flex flex-row items-center space-x-1 text-xs ">
            <img 
              src="/wind.svg"
              alt={weather.current.condition.text}
              className="w-4 h-4"
            />
            <p className="font-bold text-secondary">Wind speed</p>
            <p>{weather.current.wind_kph} km/h</p>
          </div>
          <div className="flex flex-row items-center space-x-1 text-xs ">
            <img 
              src="/eye.svg"
              alt={weather.current.condition.text}
              className="w-4 h-4"
            />
            <p className="font-bold text-secondary">Visibility</p>
            <p>{weather.current.vis_km} km</p>
          </div>
          <div className="flex flex-row items-center space-x-1 text-xs ">
            <img 
              src="/droplets.svg"
              alt={weather.current.condition.text}
              className="w-4 h-4"
            />
            <p className="font-bold text-secondary">Humidity</p>
            <p>{weather.current.humidity}%</p>
          </div>
        </div>
      </>}     
    </div>
  )
}