import clsx from "clsx";
import { AnimatePresence, motion } from "framer-motion";
import { useRouter } from 'next/router';
import { DateTime } from "luxon";
import { useCallback, useEffect, useState } from "react";
import { usePage } from "@/contexts/PageContext";
import { useHeader } from "@/contexts/HeaderContext";
import { useArticles } from "@/contexts/ArticlesContext";
import { useDebounce } from "@/utils/hooks";
import { Dropdown } from "./Dropdown";
import { Topic } from "@/types/topic";


export const Header = () => { 
  const { sources, topics, loading: loadingHeader, error, refreshTopicsWithSource } = useHeader();
  const { source, topic, setTopic, setHomePage } = usePage();
  const { 
    loading: loadingArticles,
    error: err, 
    performSearch, 
    isSearching, 
    clearSearch, 
    articles, 
    setIsSearchOpen, 
    searchParams, 
    isSearchOpen } = useArticles();
  const router = useRouter();
  const date = DateTime.now();
  const [localSearchValue, setLocalSearchValue] = useState(searchParams?.title || '');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    setLocalSearchValue(searchParams?.title || '');
  }, [searchParams?.title]);

  const [debouncedSearch, cancelDebouncedSearch] = useDebounce((query: string) => {
    setIsTyping(false);
    if (query.trim()) {
      performSearch({title: query.trim(), source: source || '', topic: topic})
    }
  }, 200);

  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsTyping(true);
    const value = e.target.value;
    if (value === '') clearSearch();
    setLocalSearchValue(value);
    debouncedSearch(value);
  };

  const handleCancelSearch = useCallback(() => {
    setLocalSearchValue('');
    setIsTyping(false);
    cancelDebouncedSearch();
    clearSearch();
  }, [cancelDebouncedSearch, clearSearch]);

  useEffect(()=> {
    if (source) refreshTopicsWithSource(source);
  }, [source ])

  const handlePageChange = (topic:Topic, route:string) => {
    setTopic(topic);
    setIsSearchOpen(false);
    router.push(`/${route}`);
  }

  const toggle = ()=> {
    setIsSearchOpen(!isSearchOpen)
  }

  const goHome = () => {
    router.push('/');
    setHomePage();
  }

  const GridHeaderTop = () => {
    return (
      <div className="grid-header-top">
        <div className="grid-gap grid grid-cols-[1fr_5fr_1fr] grid-rows-1 items-center bg-[var(--np-color-primary)] w-full border-b border-[var(--np-color-primary)]-100">
            <div className="flex flex-row bg-[var(--np-foreground)] rounded-br-md h-full items-center pl-4">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-6">
                  <path d="M16.555 5.412a8.028 8.028 0 0 0-3.503-2.81 14.899 14.899 0 0 1 1.663 4.472 8.547 8.547 0 0 0 1.84-1.662ZM13.326 7.825a13.43 13.43 0 0 0-2.413-5.773 8.087 8.087 0 0 0-1.826 0 13.43 13.43 0 0 0-2.413 5.773A8.473 8.473 0 0 0 10 8.5c1.18 0 2.304-.24 3.326-.675ZM6.514 9.376A9.98 9.98 0 0 0 10 10c1.226 0 2.4-.22 3.486-.624a13.54 13.54 0 0 1-.351 3.759A13.54 13.54 0 0 1 10 13.5c-1.079 0-2.128-.127-3.134-.366a13.538 13.538 0 0 1-.352-3.758ZM5.285 7.074a14.9 14.9 0 0 1 1.663-4.471 8.028 8.028 0 0 0-3.503 2.81c.529.638 1.149 1.199 1.84 1.66ZM17.334 6.798a7.973 7.973 0 0 1 .614 4.115 13.47 13.47 0 0 1-3.178 1.72 15.093 15.093 0 0 0 .174-3.939 10.043 10.043 0 0 0 2.39-1.896ZM2.666 6.798a10.042 10.042 0 0 0 2.39 1.896 15.196 15.196 0 0 0 .174 3.94 13.472 13.472 0 0 1-3.178-1.72 7.973 7.973 0 0 1 .615-4.115ZM10 15c.898 0 1.778-.079 2.633-.23a13.473 13.473 0 0 1-1.72 3.178 8.099 8.099 0 0 1-1.826 0 13.47 13.47 0 0 1-1.72-3.178c.855.151 1.735.23 2.633.23ZM14.357 14.357a14.912 14.912 0 0 1-1.305 3.04 8.027 8.027 0 0 0 4.345-4.345c-.953.542-1.971.981-3.04 1.305ZM6.948 17.397a8.027 8.027 0 0 1-4.345-4.345c.953.542 1.971.981 3.04 1.305a14.912 14.912 0 0 0 1.305 3.04Z" />
                </svg>
              <div className="flex flex-col px-4">
                <p className="font-bold text-extrasmall"> 
                  {date.toFormat('d MMM, yyyy')}
                </p>
                <p className="text-gray-600 text-extrasmall">{date.toFormat('HH:mm a, cccc')}</p>

              </div>
            </div>
            
            <div className="rounded-bl-md rounded-br-md bg-[var(--np-background)] py-8 text-center">
              <a 
                href="/"
                className="text-7xl font-bold hover:text-gray-600"
              >
                <h1 className="font-primary h-full">News Aggregator</h1>
              </a>
            </div>
            
            <div className="flex justify-end rounded-bl-md bg-[var(--np-background)] h-full">
              <button 
                onClick={() => goHome()}
                className="text-gray-600 hover:text-gray-900"
              >
                
              </button>
            </div>
        </div>
      </div>
    )
  }

  if (error) return (
    <header className="bg-[var(--np-background)] border-b-2">
      <GridHeaderTop />
    </header>
  );

  if (loadingHeader) {
    return (
      <header className="bg-[var(--np-background)] border-b-2">
        <div className="container m-auto">
          <div className="text-center">Loading header...</div>
        </div>
      </header>
    );
  } else {
    return (
    <div className="pb-1 border-b-2 bg-[var(--np-background)] relative">
      <header className="border-b">
        <GridHeaderTop />
        <div className="grid-header-bottom">
          <div className="row-start-1 col-start-1 flex items-center bg-[var(--np-background)] rounded-br-md z-50">
            <Dropdown options={sources} />
          </div>
          <div className="row-start-1 col-start-2 rounded-bl-md rounded-tr-md bg-[var(--np-background)] overflow-hidden">
            <div className="group/tablist relative overflow-x-auto scrollbar-hide h-full">
                <div 
                  role="tablist" 
                  className={clsx(
                    'tabs tabs-lift tabs-lg flex whitespace-nowrap min-w-max space-x-[1px] tabs-no-border h-full transition-colors duration-200 hover:tab-active',
                    {
                      'text-[var(--np-color-primary)] ': !topic,
                      'group-hover/tablist:bg-[var(--np-color-primary)] group-hover/tablist:text-[var(--np-background)]': true
                    }
                  )}
                >
                  {topics?.map((t: Topic, i) => {
                    const route = t.name.replace(/ /g, '-');
                    const isActive = router.asPath.endsWith(`/${route}/`);
                    return (
                      <button 
                        key={t.id}
                        role="tab" 
                        onClick={() => handlePageChange(t, route)}
                        className={clsx(
                          'tab tab-lifted h-full flex-shrink-0 transition-colors hover:tab-active focus:tab-active',
                          {
                            'tab-active bg-[var(--np-color-primary)] text-[var(--np-background)] active:tab-active': isActive,
                            'group-hover/tablist:text-[var(--np-background)]': !isActive,
                            'text-[var(--np-color-primary)] hover:bg-[var(--np-color-primary)] hover:text-[var(--np-background)]': !isActive && !topic
                          }
                        )}
                      >
                        {t.name}
                      </button>  
                    );
                  })}
                </div> 
                
            </div>
          </div>          
          {/* Search Section */}
          <div className="px-4 row-start-1 col-start-3 rounded-bl-md rounded-tr-md bg-[var(--np-background)] flex relative">
            {/* Search button with its own group */}
            <div className="group relative">
              {/* Expanding input - now scoped to this group only */}
              <div className={clsx(
                "absolute right-0 top-0 h-full flex items-center transition-all duration-300 ease-in-out w-6",
                {
                  "group-hover:w-[20rem] group-hover:-translate-x-42": !isSearchOpen
                }
              )}>
                <form className="w-full h-full">
                  <input
                    type="text"
                    value={localSearchValue} 
                    onChange={handleSearchInputChange}
                    placeholder="Search in all titles..."
                    className={clsx(
                      "placeholder:text-gray-400 w-full h-full px-3 py-2 bg-[var(--np-background)] rounded-bl-md rounded-tr-md transition-all duration-200 focus:outline-none",
                      {
                        "opacity-0 group-hover:opacity-100 border-l border-b-[0.8px] border-transparent group-hover:border-[var(--np-color-primary)] transition-opacity duration-200 transition-border delay-75": 
                          !isSearchOpen
                      }
                    )}
                  />
                </form>
              </div>

              {/* Search button content */}
              <div className={clsx(
                "h-full w-6 flex items-center justify-center z-50",
                {
                  "hover:opacity-70 transition-opacity": !isSearchOpen
                }
              )}>
                {(isTyping || searchParams || isSearchOpen) ? (
                  <>
                    {isSearching && <div className="loading loading-spinner loading-xs group-hover:hidden"></div>}
                    <button
                      onClick={handleCancelSearch}
                      className=" group-hover:block p-1 rounded transition-colors z-10"
                      title="Clear search"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </>
                ) : (
                  <button className="z-10">
                    <img 
                      src="/search-dark.svg"
                      alt="Search articles"
                      className="w-6 h-6"
                    />
                  </button>
                )}
              </div>
            </div>
            {/* Advanced search button */}
            <button 
              className="mx-auto z-20" 
              title="Open advanced search" 
              onClick={() => toggle()}
            >
              <img 
                src="/text-search.svg"
                alt="Open advanced search"
                className="w-6 h-6"
              />
            </button>
          </div>
        </div>
        
        {/* Search status bar */}
        {((searchParams || isTyping) && !isSearchOpen) && (
          <AnimatePresence>
            <motion.div
              key="search-status"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height:!isSearchOpen ? 'auto': 0}}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.5, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="px-4 py-2 text-sm border-t bg-[var(--np-color-primary)] text-[var(--np-background)]">
                {isTyping && <span>Typing...</span>}
                {isSearching && !isTyping && <span>Searching for "{localSearchValue}"...</span>}
                {searchParams && err && err.statusCode ===204 && !isTyping && <span>No articles found</span>}
                {searchParams && !err && !isTyping && <span>Found articles: {articles.length}</span>}
              </div>
            </motion.div>
          </AnimatePresence>
        )}
      </header>
      {loadingArticles && <progress className="progress w-full bottom-0 absolute"></progress>}
    </div>
  );
  }    
}