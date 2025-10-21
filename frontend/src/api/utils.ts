import { ApiError } from '@/types/api';

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