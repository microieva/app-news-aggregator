import { ApiError } from '@/types/api';
import { DateTime } from 'luxon';

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
