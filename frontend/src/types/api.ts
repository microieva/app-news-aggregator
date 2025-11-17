import { Article } from "./article";
import { Topic } from "./topic";

export interface ApiResponse<T> {
  data: T
  message?: string
  success?: boolean
}

export interface ApiError {
  message?: string;
  statusCode?: number;
  error?:any;
  detail?:string
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface ArticlesData {
  articles: Article[]
  total: number;
  topic_name?: string;
}

export interface SourcesData {
  sources:string[];
  topic_name?: string;
}

export interface TopicsData {
  topics: Topic[];
  total: number;
}

export interface SearchData {
  articles: Article[]
  total: number;
  topic_name?: string;
}