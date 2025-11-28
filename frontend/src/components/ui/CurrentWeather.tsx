import { useWeather } from "@/contexts/WeatherContext";
import { getWeatherIcon } from "@/utils/utils";
import { useEffect } from "react";

export const CurrentWeather = ()=> {
  const { weather, refreshWeather } = useWeather();

  useEffect(()=>{
    refreshWeather();
  }, [weather])
  
  
  return (
    <div className='w-full h-[28rem] flex flex-col justify-between px-4 bg-[var(--np-foreground)] rounded-tr-xl rounded-bl-xl'>
      <div className='mt-4'>
        <h3 className="card-title text-2xl font-bold">{weather?.location.name}</h3>
        <p className="text-xs font-bold text-gray-600">{weather?.location.region}, {weather?.location.country}</p>
      </div>
      {weather && 
      <>
        <div>
        <img 
          src={getWeatherIcon(weather.current.condition.code, weather.current.is_day)}
          alt={weather.current.condition.text}
          className="w-32 h-32 mx-auto"
        /> 
        <p className="text-xs mt-1 text-center">{weather.current.condition.text}</p>
      </div>
      <div>
        <h1 className="text-7xl font-bold text-center">{weather.current.temp_c}°C</h1>
        <p className="text-sm font-bold text-center text-gray-600">Feels like {weather.current.feelslike_c}°C</p> 
      </div>
      <div className='mx-auto mb-4'>
        <div className="flex flex-row items-center space-x-1 text-xs ">
          <img 
            src="/wind.svg"
            alt={weather.current.condition.text}
            className="w-4 h-4"
          />
          <p className="font-bold text-gray-600">Wind speed</p>
          <p>{weather.current.wind_kph} km/h</p>
        </div>
        <div className="flex flex-row items-center space-x-1 text-xs ">
          <img 
            src="/eye.svg"
            alt={weather.current.condition.text}
            className="w-4 h-4"
          />
          <p className="font-bold text-gray-600">Visibility</p>
          <p>{weather.current.vis_km} km</p>
        </div>
        <div className="flex flex-row items-center space-x-1 text-xs ">
          <img 
            src="/droplets.svg"
            alt={weather.current.condition.text}
            className="w-4 h-4"
          />
          <p className="font-bold text-gray-600">Humidity</p>
          <p>{weather.current.humidity}%</p>
        </div>
      </div>
      </>}     
    </div>
  )
}