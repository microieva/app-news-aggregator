'use client'; 

import useSWR from 'swr';
import { createContext, useContext, ReactNode, useState, useMemo } from 'react';
import { ApiError, HeadlinesData} from '@/types/api';
import { articlesService } from '@/services/articlesService';

interface HeadlinesContextType {
  data: HeadlinesData | null;
  loading: boolean;
  error: ApiError | null;
  fetchHeadlines: () => Promise<void>;
}

const HeadlinesContext = createContext<HeadlinesContextType | undefined>(undefined);

interface HeadlinesProviderProps {
  children: ReactNode;
  initialData?: HeadlinesData;
}

const fetchers = { 
  getHeadlines: async (): Promise<HeadlinesData> => {
    return await articlesService.getHeadlines();  
  }
};

export function HeadlinesProvider({ 
  children, 
  initialData
}: HeadlinesProviderProps) {
  const [loading, setLoading] = useState(false);
  const [manualError, setManualError] = useState<ApiError | null>(null);

  const {
    data: headlinesData,
    error: swrError,
    mutate: mutateData,
  } = useSWR<HeadlinesData, ApiError>(
    'headlines',
    fetchers.getHeadlines,
    {
      fallbackData: initialData,
      revalidateOnFocus: false,
      shouldRetryOnError: (error) => error.statusCode !== 204,
    }
  );

  const fetchHeadlines = async () => {
    setManualError(null);
    setLoading(true);
    try {
      const headlines = await fetchers.getHeadlines();
      mutateData(headlines, false); 
    }  catch (error) {
      const apiError = error as ApiError;
      
      if (apiError) {
        mutateData(undefined, false); 
        setManualError(apiError);
      } else {
        throw error;
      }
    }  finally {
        setLoading(false)
    }
  }
  const error = manualError || swrError;

  const value = useMemo(() => ({
    data: headlinesData || null,
    loading,
    error: error || null,
    fetchHeadlines,
  }), [headlinesData, loading, error]);

  return (
    <HeadlinesContext.Provider value={value}>
      {children}
    </HeadlinesContext.Provider>
  );
}

export function useHeadlines() {
  const context = useContext(HeadlinesContext);
  if (context === undefined) {
    throw new Error('useHeadlines must be used within a HeadlinesProvider');
  }
  return context;
}

