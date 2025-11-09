import { createContext, useContext, ReactNode, useState } from 'react';
import useSWR from 'swr';
import articlesService from '@/services/articlesService';
import { ApiError, ArticlesData } from '@/types/api';
import { Article } from '@/types/article';

interface ArticlesContextType {
  articles: Article[];
  loading: boolean;
  error: ApiError | null;
  refreshArticles: (args: { source: string | null; topic: string | null }) => Promise<void>;
}

const ArticlesContext = createContext<ArticlesContextType | undefined>(undefined);

interface ArticlesProviderProps {
  children: ReactNode;
  initialArticles?: Article[];
}

const fetchers = {
  getFrontPageArticles: async (): Promise<Article[]> => {
    const data: ArticlesData = await articlesService.getFrontPageArticles();
    return data.articles;
  },
  
  getArticles: async (source: string | null, topic: string | null): Promise<Article[]> => {
    let data: ArticlesData;
    
    if (topic) {
      data = await articlesService.getArticlesByTopicName(topic, source || undefined);
    } else {
      data = await articlesService.getArticles(source || undefined);
    } 
    
    return data.articles;
  },
};

export function ArticlesProvider({ 
  children, 
  initialArticles = [], 
}: ArticlesProviderProps) {
  const [manualError, setManualError] = useState<ApiError | null>(null);

  const {
    data: articlesData,
    error: swrError,
    mutate: mutateArticles,
  } = useSWR<Article[], ApiError>(
    'front-page-articles',
    fetchers.getFrontPageArticles,
    {
      fallbackData: initialArticles,
      revalidateOnFocus: false,
      dedupingInterval: 60000,
      refreshInterval: 300000,
      shouldRetryOnError: (error) => error.statusCode !== 404,
    }
  );

  const refreshArticles = async ({ source, topic }: { source: string | null; topic: string | null }) => {
    setManualError(null); 
    
    try {
      if (source || topic) {
        const filteredData = await fetchers.getArticles(source, topic);
        mutateArticles(filteredData, false);
      } else {
        mutateArticles();
      }
    } catch (error) {
      const apiError = error as ApiError;
      
      if (apiError.statusCode === 404) {
        console.warn(`No articles found for ${topic ? `topic: ${topic}` : 'filters'}`);
        mutateArticles([], false); 
        setManualError(apiError);
      } else {
        throw error;
      }
    }
  };

  const error = manualError || swrError;

  const value: ArticlesContextType = {
    articles: articlesData || [],
    loading: !articlesData && !error,
    error: error || null,
    refreshArticles,
  };

  return (
    <ArticlesContext.Provider value={value}>
      {children}
    </ArticlesContext.Provider>
  );
}

export function useArticles() {
  const context = useContext(ArticlesContext);

  if (context === undefined) {
    throw new Error('useArticles must be used within an ArticlesProvider');
  }
  return context;
}
