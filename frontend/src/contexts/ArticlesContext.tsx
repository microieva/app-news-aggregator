import useSWR from 'swr';
import { createContext, useContext, ReactNode, useState } from 'react';
import { articlesService } from '@/services/articlesService';
import { ApiError, ArticlesData } from '@/types/api';
import { Article, SearchParams } from '@/types/article';
import { Topic } from '@/types';

interface ArticlesContextType {
  articles: Article[];
  loading: boolean;
  error: ApiError | null;
  isSearching: boolean;
  searchParams: SearchParams | undefined;
  isSearchOpen: boolean;
  refreshArticles: (args: { source: string | null; topic: Topic | null }) => Promise<void>;
  performSearch: (params: SearchParams) => Promise<void>;
  clearSearch: () => void;
  setIsSearchOpen: (bool:boolean) => void;
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
  
  getArticles: async (source: string | null, topic: Topic | null): Promise<Article[]> => {
    let data: ArticlesData;
    
    if (topic) {
      data = await articlesService.getArticlesByTopicName(topic.name, source || undefined);
    } else {
      data = await articlesService.getArticles(source || undefined);
    } 
    
    return data.articles;
  },

  searchArticles: async (searchParams: SearchParams): Promise<Article[]> => {
    const data: ArticlesData = await articlesService.searchArticles(searchParams);
    return data.articles;
  },
};

export function ArticlesProvider({ 
  children, 
  initialArticles = [], 
}: ArticlesProviderProps) {
  const [manualError, setManualError] = useState<ApiError | null>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [searchParams, setSearchParams] = useState<SearchParams>();
  const [isSearchOpen, setIsSearchOpen] = useState(false);

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

  const refreshArticles = async ({ source, topic }: { source: string | null; topic: Topic | null }) => {
    setManualError(null);
    setIsSearching(false);
    setSearchParams(undefined);
    
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
        mutateArticles([], false); 
        setManualError(apiError);
      } else {
        throw error;
      }
    }
  };

  const performSearch = async (params: SearchParams) => {
    setManualError(null);
    setIsSearching(true);
    mutateArticles([], false);
    if (params) setSearchParams(params);

    try {
      const searchResults = await fetchers.searchArticles(params);
      mutateArticles(searchResults, false);
    } catch (error) {
      const apiError = error as ApiError;
      
      if (apiError.statusCode === 404) {
        console.warn(`No articles found for search: "${JSON.stringify(params)}"`);
        mutateArticles([], false);
        setManualError(apiError);
      } else {
        console.error('Search failed:', error);
        setManualError(apiError);
      }
    }
  };

  const clearSearch = () => {
    setIsSearching(false);
    setIsSearchOpen(false);
    setSearchParams(undefined);
    setManualError(null);
    mutateArticles(); 
  };

  const error = manualError || swrError;

  const value: ArticlesContextType = {
    articles: articlesData || [],
    loading: !articlesData && !error,
    error: error || null,
    isSearching,
    searchParams: searchParams || undefined,
    setIsSearchOpen,
    isSearchOpen,
    refreshArticles,
    performSearch,
    clearSearch,
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
