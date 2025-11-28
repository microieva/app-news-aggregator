import useSWR from 'swr';
import { createContext, useContext, ReactNode, useState, useMemo } from 'react';
import { articlesService } from '@/services/articlesService';
import { ApiError, ArticlesData, RequestArgs } from '@/types/api';
import { Article, SearchParams } from '@/types/article';
import { Topic } from '@/types';

interface ArticlesContextType {
  data: ArticlesData | null;
  loading: boolean;
  error: ApiError | null;
  isSearching: boolean;
  searchParams: SearchParams | undefined;
  isSearchOpen: boolean;
  refreshArticles: (args: RequestArgs) => Promise<void>;
  performSearch: (params: SearchParams) => Promise<void>;
  clearSearch: () => void;
  setIsSearchOpen: (bool:boolean) => void;
}

const ArticlesContext = createContext<ArticlesContextType | undefined>(undefined);

interface ArticlesProviderProps {
  children: ReactNode;
  initialData?: ArticlesData;
}

const fetchers = {
  getFrontPageArticles: async (): Promise<ArticlesData> => {
    return await articlesService.getFrontPageArticles();
  },
  
  getArticles: async (source: string | null, topic: Topic | null, skip?:number): Promise<ArticlesData> => {
    let data: ArticlesData;
    
    if (topic) {
      data = await articlesService.getArticlesByTopicId(topic.id, source as string, skip);
    } else {
      data = await articlesService.getArticles(source);
    } 
    return data;
    
  },

  searchArticles: async (searchParams: SearchParams): Promise<ArticlesData> => {
    return await articlesService.searchArticles(searchParams);
  },
};

export function ArticlesProvider({ 
  children, 
  //initialArticles = [], 
  initialData
}: ArticlesProviderProps) {
  const [manualError, setManualError] = useState<ApiError | null>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [searchParams, setSearchParams] = useState<SearchParams>();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const {
    data: articlesData,
    error: swrError,
    mutate: mutateData,
  } = useSWR<ArticlesData, ApiError>(
    'front-page-articles',
    fetchers.getFrontPageArticles,
    {
      fallbackData: initialData,
      revalidateOnFocus: false,
      shouldRetryOnError: (error) => error.statusCode !== 204,
    }
  );

  const refreshArticles = async ({ source, topic, skip }: { source: string | null; topic: Topic | null, skip?:number }) => {
    setManualError(null);
    setIsSearching(false);
    setLoading(true);
    setSearchParams(undefined);
    try {
      if (source || topic || skip) {
        const filteredData = await fetchers.getArticles(source, topic, skip);
        if (skip) {
          const data = {...filteredData, articles: [...articlesData!.articles, ...filteredData.articles]}
          mutateData(data, false)
        } else {
          mutateData(filteredData, false);
        }
      } else {
        mutateData();
      }
      
    } catch (error) {
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
  };

  const performSearch = async (params: SearchParams) => {
    setManualError(null);
    setIsSearching(true);

    if (params) setSearchParams(params);

    try {
      const searchData = await fetchers.searchArticles(params);
      setIsSearching(false);
      if (searchData.total === 0) {
        const apiError = {
          statusCode: 204,
          detail: "No results found"
        }
        setManualError(apiError);
      } else {
        mutateData(searchData, false);
      }
    } catch (error) {
      const apiError = error as ApiError;
      setIsSearching(false);
      if (apiError) {
        mutateData(undefined, false);
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
  };

  const error = manualError || swrError;

  const value: ArticlesContextType = useMemo(() => ({
    data: articlesData || null,
    loading,
    error: error || null,
    isSearching,
    searchParams: searchParams || undefined,
    setIsSearchOpen,
    isSearchOpen,
    refreshArticles,
    performSearch,
    clearSearch
  }), [articlesData, loading, error]);

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
