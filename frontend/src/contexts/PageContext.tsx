import { createContext, useContext, ReactNode, useReducer } from 'react';
import { Topic } from '@/types/topic';

interface PageState {
  source: string | null;
  topic: Topic | null;
}

type PageAction =
  | { type: 'SET_SOURCE'; payload: string | null }
  | { type: 'SET_TOPIC'; payload: Topic | null }
  | { type: 'CLEAR_FILTERS' }
  | { type: 'SET_HOME_PAGE' };

interface PageContextType extends PageState {
  setSource: (source: string | null) => void;
  setTopic: (topic: Topic | null) => void;
  clearFilters: () => void;
  setHomePage: () => void;
  hasActiveFilters: boolean;
  activeFiltersCount: number;
}

const PageContext = createContext<PageContextType | undefined>(undefined);

const initialState: PageState = {
  source: null,
  topic: null,
};

function pageReducer(state: PageState, action: PageAction): PageState {
  switch (action.type) {
    case 'SET_SOURCE':
      return {
        ...state,
        source: action.payload,
      };
    case 'SET_TOPIC':
      return {
        ...state,
        topic: action.payload,
      };
    case 'CLEAR_FILTERS':
      return {
        source: null,
        topic: null,
      };
    case 'SET_HOME_PAGE':
      return {
        source: null,
        topic: null,
      };
    default:
      return state;
  }
}

interface PageProviderProps {
  children: ReactNode;
}

export function PageProvider({ children }: PageProviderProps) {
  const [state, dispatch] = useReducer(pageReducer, initialState);

  const actions = {
    setSource: (source: string | null) => 
      dispatch({ type: 'SET_SOURCE', payload: source }),
    
    setTopic: (topic: Topic | null) => 
      dispatch({ type: 'SET_TOPIC', payload: topic }),
    
    clearFilters: () => 
      dispatch({ type: 'CLEAR_FILTERS' }),
    
    setHomePage: () => 
      dispatch({ type: 'SET_HOME_PAGE' }),
  };

  const hasActiveFilters = !!state.source || !!state.topic;
  const activeFiltersCount = [state.source, state.topic].filter(Boolean).length;

  const value: PageContextType = {
    ...state,
    ...actions,
    hasActiveFilters,
    activeFiltersCount,
  };

  return (
    <PageContext.Provider value={value}>
      {children}
    </PageContext.Provider>
  );
}

export function usePage() {
  const context = useContext(PageContext);
  if (context === undefined) {
    throw new Error('usePage must be used within a PageProvider');
  }
  return context;
}