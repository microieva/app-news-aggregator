import { createContext, useContext, ReactNode } from 'react';
import useSWR from 'swr';
import { articlesService } from '@/services/articlesService';
import { topicsService } from '@/services/topicsService';
import { ApiError, SourcesData, TopicsData } from '@/types/api';
import { Topic } from '@/types/topic';

interface HeaderContextType {
  sources: string[];
  topics: Topic[];
  loading: boolean;
  error: ApiError | null;
  refreshHeaderData: () => void;
  refreshTopicsWithSource: (source:string) => void;
}

const HeaderContext = createContext<HeaderContextType | undefined>(undefined);

interface HeaderProviderProps {
  children: ReactNode;
  initialSources?: string[];
  initialTopics?: Topic[];
}

const fetchers = {
  getSources: async (): Promise<string[]> => {
    const data: SourcesData = await articlesService.getUsedSources();
    return data.sources;
  },
  getTopics: async (): Promise<Topic[]> => {
    const data: TopicsData = await topicsService.getUsedTopics();
    return data.topics;
  },
  getTopicsBySource: async (source: string): Promise<Topic[]> => {
    const data: TopicsData = await topicsService.getUsedTopics(source);
    return data.topics;
  },
};

export function HeaderProvider({ 
  children, 
  initialSources = [], 
  initialTopics = [] 
}: HeaderProviderProps) {

  const {
    data: sources,
    error: sourcesError,
    mutate: mutateSources,
  } = useSWR<string[]>(
    'header-sources',
    fetchers.getSources,
    {
      fallbackData: initialSources,
      revalidateOnFocus: false,
      dedupingInterval: 300000, // 5 minutes
      refreshInterval: 3600000, // 1 hour
    }
  );

  const {
    data: topics,
    error: topicsError,
    mutate: mutateTopics,
  } = useSWR<Topic[]>(
    'header-topics',
    fetchers.getTopics,
    {
      fallbackData: initialTopics,
      revalidateOnFocus: false,
      dedupingInterval: 300000, // 5 minutes
      refreshInterval: 1800000, // 30 minutes
    }
  );

  const refreshHeaderData = () => {
    mutateSources();
    mutateTopics();
  };
   const refreshTopicsWithSource = async (source: string | null) => {
    if (source) {
      const filteredTopics = await fetchers.getTopicsBySource(source);
      mutateTopics(filteredTopics, false); // don't revalidate
    } else {
      mutateTopics();
    }
  };

  const value: HeaderContextType = {
    sources: sources || [],
    topics: topics || [],
    loading: !sources && !topics && !sourcesError && !topicsError,
    error: sourcesError || topicsError || null,
    refreshHeaderData,
    refreshTopicsWithSource
  };

  return (
    <HeaderContext.Provider value={value}>
      {children}
    </HeaderContext.Provider>
  );
}

export function useHeader() {
  const context = useContext(HeaderContext);

  if (context === undefined) {
    throw new Error('useHeader must be used within a HeaderProvider');
  }
  return context;
}