import { ApiError } from '@/types/api';
import { DateTime } from 'luxon';
import _ from 'lodash';

export const handleApiError = (error: unknown): ApiError => {
  if (typeof error === 'object' && error !== null && 'message' in error) {
    return error as ApiError;
  }
  return {
    message: 'An unexpected error occurred',
    statusCode: 500,
  };
};

export const isApiError = (error: unknown): error is ApiError => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'statusCode' in error
  );
};

export const formatDate = (date:string):string => {
  const str = DateTime.fromISO(date)
  return str.toFormat('d MMM')
}

export const getWeekday = (date:string):string => {
  const str = DateTime.fromISO(date)
  return str.toFormat('ccc')
}

export const getWeatherIcon = (conditionCode: number, isDay: boolean): string => {
  
  const iconMap: { [key: number]: string } = {
    1000: isDay ? "clear-day" : "clear-night", 
    1003: isDay ? "cloud-sun" : "partly-cloudy-night", 

    1153: "drizzle", 
    1183: "drizzle",
    1006: "cloudy", // Cloudy
    1009: "cloud-sun", // Overcast
    1030: "mist", // Mist
    1189: "rain", // Moderate rain
    1243: "rain", // Moderate/heavy rain shower
    1192: "cloud-rain-wind", // Heavy rain
    1195: "cloud-rain-wind", // Torrential rain
    1213: "snow", // Light snow
    1219: "snow", // Moderate snow
    1222: "heavy-snow", // Heavy snow
    1225: "heavy-snow", // Heavy snow
    1237: "hail", // Ice pellets
    1255: "snow", // Light snow showers
    1258: "snow", // Moderate/heavy snow showers
    1261: "hail", // Light showers of ice pellets
    1264: "hail", // Moderate/heavy showers of ice pellets
    1273: "thunderstorm", // Patchy light rain with thunder
    1276: "thunderstorm", // Moderate/heavy rain with thunder
    1240: "cloud-sun-rain", // Light rain shower
    1246: "cloud-rain-wind", // Torrential rain shower

    1279: "thunderstorm", // Patchy light snow with thunder
    1282: "thunderstorm", // Moderate/heavy snow with thunder
    
    1063: isDay ? "cloud-sun-rain" : "cloud-moon-rain", 
    
    1249: "snow", // Light sleet showers /sleet
    1252: "snow", // Moderate/heavy sleet showers/sleet
    1201: "snow", // Moderate or heavy sleet NOT FOUND/sleet
  };

  const iconName = iconMap[conditionCode] //|| "not-available";
  return iconName ? `/${iconName}.svg` : "/placeholder_.svg";
};

export const isFormEmpty = (formValues:Object):boolean => _.isEmpty(_.pickBy(formValues, _.identity));
