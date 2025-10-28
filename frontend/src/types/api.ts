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
  articles: any;
  total: number;
  topic_name?: string;
}