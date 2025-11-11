export interface WeatherCondition {
  text: string;
  icon: string;
  code: number;
}

export interface Location {
  name: string;
  region: string;
  country: string;
  lat: number;
  lon: number;
  tz_id: string;
  localtime: string;
}

export interface AirQuality {
  co?: number;
  no2?: number;
  o3?: number;
  so2?: number;
  pm2_5?: number;
  pm10?: number;
  us_epa_index?: number;
  gb_defra_index?: number;
}

export interface CurrentWeather {
  temp_c: number;
  temp_f: number;
  is_day: boolean;
  condition: WeatherCondition;
  wind_kph: number;
  wind_degree: number;
  wind_dir: string;
  pressure_mb: number;
  precip_mm: number;
  humidity: number;
  cloud: number;
  feelslike_c: number;
  feelslike_f: number;
  vis_km: number;
  uv: number;
  gust_kph: number;
  air_quality?: AirQuality;
}

export interface WeatherResponse {
  location: Location;
  current: CurrentWeather;
}

export interface DailyForecast {
  date: string;
  max_temp_c: number;
  min_temp_c: number;
  condition: WeatherCondition;
  chance_of_rain: number;
  uv: number;
}

export interface WeeklyForecastResponse {
  location: Location;
  current: CurrentWeather;
  forecast: DailyForecast[];
}