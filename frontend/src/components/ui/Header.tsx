'use client'; 

import clsx from "clsx";
import Link from 'next/link';
import { AnimatePresence, motion } from "framer-motion";
import { usePathname, useRouter } from 'next/navigation';
import { DateTime } from "luxon";
import { useCallback, useEffect, useState } from "react";
import { usePage } from "@/contexts/PageContext";
import { useHeader } from "@/contexts/HeaderContext";
import { useArticles } from "@/contexts/ArticlesContext";
import { useDebounce, useThrottle } from "@/utils/hooks";
import { Dropdown } from "./Dropdown";
import { Topic } from "@/types/topic";
import { DropdownNew } from "./DropdownNew";


export const Header = () => { 
  const { sources, topics, loading: loadingHeader, error, refreshTopicsWithSource } = useHeader();
  const { source, topic, setTopic, setHomePage, setSource } = usePage();

  const { 
    loading: loadingArticles,
    error: err, 
    performSearch, 
    isSearching, 
    clearSearch, 
    data, 
    setIsSearchOpen, 
    refreshArticles,
    searchParams, 
    isSearchOpen } = useArticles();

  const router = useRouter();
  const pathname = usePathname();
  const [currentDate, setCurrentDate] = useState<DateTime | null>(null);
  const [localSearchValue, setLocalSearchValue] = useState<string>(searchParams?.title || '');
  const [isTyping, setIsTyping] = useState<boolean>(false);
   const [open, setOpen] = useState<boolean>(false);

  const throttledSetDate = useThrottle((date: DateTime) => {
    setCurrentDate(date);
  }, 60000); 


  useEffect(() => {
    if (!loadingHeader) {
      const now = DateTime.now();
      setCurrentDate(now);
    }
    const interval = setInterval(() => {
      const updatedNow = DateTime.now();
      throttledSetDate(updatedNow);
    }, 60000);
    return () => clearInterval(interval);
  },[loadingHeader]);

  useEffect(() => {
    setLocalSearchValue(searchParams?.title || '');
  }, [searchParams]);

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
  }

  const handleCancelSearch = useCallback(() => {
    setLocalSearchValue('');
    setIsTyping(false);
    cancelDebouncedSearch();
    clearSearch();
  }, [cancelDebouncedSearch, clearSearch]);

  useEffect(()=> {
    if (source) refreshTopicsWithSource(source);
  }, [source]);

  const handlePageChange = async (topic: Topic) => {  
    setIsSearchOpen(false);
    setTopic(topic);
    refreshArticles({topic, source});
  }

  useEffect(()=> {
    if (!loadingArticles && topic) router.push(`/${topic.name}`);
  }, [loadingArticles]);

  const toggle = (e:MouseEvent)=> {
    setIsSearchOpen(!isSearchOpen);
  }

  const goHome = () => {
    router.push('/');
    setHomePage();
  }

  const GridHeaderTop = () => {
    return (
      <div className="grid-header-top">
        <div className="grid-gap grid grid-cols-[1fr_5fr_1fr] grid-rows-1 items-center bg-[var(--np-color-primary)] w-full border-b border-[var(--np-color-primary)]-100">
            <div className="flex flex-row bg-foreground rounded-br-md h-full items-center lg:pl-4">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-6 md:h-10 lg:h-6 lg:w-6 w-full">
                  <path d="M16.555 5.412a8.028 8.028 0 0 0-3.503-2.81 14.899 14.899 0 0 1 1.663 4.472 8.547 8.547 0 0 0 1.84-1.662ZM13.326 7.825a13.43 13.43 0 0 0-2.413-5.773 8.087 8.087 0 0 0-1.826 0 13.43 13.43 0 0 0-2.413 5.773A8.473 8.473 0 0 0 10 8.5c1.18 0 2.304-.24 3.326-.675ZM6.514 9.376A9.98 9.98 0 0 0 10 10c1.226 0 2.4-.22 3.486-.624a13.54 13.54 0 0 1-.351 3.759A13.54 13.54 0 0 1 10 13.5c-1.079 0-2.128-.127-3.134-.366a13.538 13.538 0 0 1-.352-3.758ZM5.285 7.074a14.9 14.9 0 0 1 1.663-4.471 8.028 8.028 0 0 0-3.503 2.81c.529.638 1.149 1.199 1.84 1.66ZM17.334 6.798a7.973 7.973 0 0 1 .614 4.115 13.47 13.47 0 0 1-3.178 1.72 15.093 15.093 0 0 0 .174-3.939 10.043 10.043 0 0 0 2.39-1.896ZM2.666 6.798a10.042 10.042 0 0 0 2.39 1.896 15.196 15.196 0 0 0 .174 3.94 13.472 13.472 0 0 1-3.178-1.72 7.973 7.973 0 0 1 .615-4.115ZM10 15c.898 0 1.778-.079 2.633-.23a13.473 13.473 0 0 1-1.72 3.178 8.099 8.099 0 0 1-1.826 0 13.47 13.47 0 0 1-1.72-3.178c.855.151 1.735.23 2.633.23ZM14.357 14.357a14.912 14.912 0 0 1-1.305 3.04 8.027 8.027 0 0 0 4.345-4.345c-.953.542-1.971.981-3.04 1.305ZM6.948 17.397a8.027 8.027 0 0 1-4.345-4.345c.953.542 1.971.981 3.04 1.305a14.912 14.912 0 0 0 1.305 3.04Z" />
                </svg>
              {!loadingHeader &&  currentDate ? 
               <div className="flex-col px-4 hidden lg:block">
                  <p className="font-bold text-extrasmall" suppressHydrationWarning>
                    {currentDate.toFormat('d MMM, yyyy')}
                  </p>
                  <p className="text-secondary text-extrasmall" suppressHydrationWarning>
                    {currentDate.toFormat('HH:mm a, cccc')}
                  </p>
                </div>
              : null}
            </div>
            
            <div className="rounded-bl-md rounded-br-md bg-background py-2 md:py-8 text-center">
              <a 
                href="/"
                className="text-xl font-bold hover:text-secondary"
              >
                <h1 className="font-primary h-full">News From Earth</h1>
              </a>
            </div>
            
            <div className="flex justify-end rounded-bl-md bg-background h-full">
              <button 
                onClick={() => goHome()}
                className="text-secondary hover:text-gray-900"
              >
                
              </button>
            </div>
        </div>
      </div>
    )
  }

  const GridHeaderBottom = () => {
    const hasActiveTab = topics?.some(t => {
      const route = t.name.replace(/ /g, '-');
      return pathname === `/${route}` || pathname.startsWith(`/${route}/`);
    }) || false;
    return (
      <div className="grid-header-bottom">
          <div className="row-start-1 col-start-1 flex items-center bg-background rounded-br-md relative z-50 h-full">
            <Dropdown options={sources} />
          </div>

          <div 
            className=" h-auto row-start-1 col-start-2 rounded-bl-md rounded-tr-md bg-transparent overflow-x-auto"
          >
            <div className={clsx("group/tablist relative overflow-x-auto scrollbar-hide h-full w-max min-w-full flex items-center bg-background hover:bg-primary", {"bg-primary": hasActiveTab})}>  
              <div 
                role="tablist" 
                className={clsx(
                  'tabs tabs-lift tabs-lg flex whitespace-nowrap h-full tabs-no-border',
                  {
                    'text-[var(--np-color-primary)]': !topic,
                    'group-hover/tablist:text-background': true
                  }
                )}
              >
                {topics?.map((t: Topic, i) => {
                  const route = t.name.replace(/ /g, '-');
                  const isActive = pathname === `/${route}` || pathname.startsWith(`/${route}/`);
                  return (
                    <Link 
                      key={t.id}
                      role="tab" 
                      href={`/${route}`}
                      onClick={() => handlePageChange(t)}
                      className={clsx(
                        'tab tab-lifted h-full flex-shrink-0 transition-colors hover:bg-background hover:z-50',
                        {
                          'tab-active bg-[var(--np-color-primary)] text-[var(--np-background) z-50': isActive,
                          'group-hover/tablist:text-background': !isActive,
                          'text-[var(--np-color-primary)] hover:bg-[var(--np-color-primary)] hover:tab-active': !isActive && !topic
                        }
                      )}
                    >
                      {t.name}
                    </Link>  
                  );
                })}
              </div>
            </div> 
          </div> 

          {/* Search Section */}
          <div className="h-auto px-4 row-start-1  col-start-3 rounded-bl-md rounded-tr-md bg-background flex relative">
            {/* Search button group */}
            <div className="group relative">
              {/* Expanding input */}
              <div className={clsx(
                "absolute right-0 top-0 h-full flex items-center transition-all duration-300 ease-in-out w-6",
                {
                  "group-hover:w-[20rem] group-hover:-translate-x-42": !isSearchOpen
                }
              )}>
                <form className="w-full h-full">
                  <input
                    name="title"
                    type="text"
                    value={localSearchValue} 
                    onChange={handleSearchInputChange}
                    placeholder="Search in all titles..."
                    className={clsx(
                      "placeholder:text-tertiary opacity-0 w-full h-full px-3 py-2 bg-background rounded-bl-md rounded-tr-md transition-all duration-200 focus:outline-none",
                      {
                        "group-hover:opacity-100 border-l border-b-[0.8px] border-transparent group-hover:border-[var(--np-color-primary)] transition-opacity duration-200 transition-border delay-100": 
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
                      className="group-hover:block p-1 rounded transition-colors z-10"
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
              className="mx-2 md:mx-auto z-20" 
              title="Open advanced search" 
              onClick={(e:any) => toggle(e)}
            >
              <img 
                src="/text-search.svg"
                alt="Open advanced search"
                className="w-6 h-6"
              />
            </button>
          </div>
      </div>

    )
  }

  const GridHeaderBottomMobile = () => {
    const handleSelect =(option:string)=> {
      const topic = topics.find(t=> t.name === option);
      if (topic) handlePageChange(topic);
      else setSource(option); refreshTopicsWithSource(option);
    };

    return (
      <div className="grid-header-bottom-mobile">
        <div className="row-start-1 col-start-1 flex items-center bg-background rounded-br-md relative z-50 h-full">
          <DropdownNew options={sources} handleSelect={handleSelect} selected={source || undefined}>
            <div className="flex content-center items-center justify-around flex-grow-0">
              {source ? <p className="text-sm">{source}</p> : <p className="text-sm">source</p>}
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-6">
                <path fillRule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z" clipRule="evenodd" />
              </svg>
            </div>
          </DropdownNew>
        </div>
        <div className="h-12 px-4 row-start-1 col-start-2 rounded-bl-md rounded-tr-md bg-background flex relative">
          <form className="w-full h-full">
            <input
              name="title"
              type="text"
              value={localSearchValue} 
              onChange={handleSearchInputChange}
              placeholder="Search in all titles..."
              className={clsx("placeholder:text-tertiary w-full h-full bg-background focus:outline-none", {"hidden":isSearchOpen})}
            />
          </form>
          <div className="flex flex-row gap-2 flex-shrink-0">
            {(isTyping || searchParams || isSearchOpen) ? (
              !isSearching ? (
                <button
                  onClick={handleCancelSearch}
                  className="rounded transition-colors"
                  title="Clear search"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              ) : (
                <div className="loading loading-spinner loading-xs"></div>
              )
            ) : (
              <button>
                <img 
                  src="/search-dark.svg"
                  alt="Search articles"
                  className="w-6 h-6" 
                />
              </button>
            )}
            <button 
              title="Open advanced search" 
              onClick={(e:any) => toggle(e)}
            >
              <img 
                src="/text-search.svg"
                alt="Open advanced search"
                className="w-6 h-6"
              />
            </button>
          </div>
        </div>

        <div className="flex-shrink-0 rounded-tr-md flex flex-row bg-background col-span-2 items-center">
          <div className="mx-4 h-full content-center items-center flex-shrink-0 "> 
            <DropdownNew options={topics.map(t=>t.name)} handleSelect={handleSelect} selected={topic?.name}>
              <img src="/menu.svg" alt="Select category" className="w-6 h-6 mt-2"/>
            </DropdownNew>
          </div>
          <div className="overflow-x-auto rounded-bl-md rounded-tr-md h-full">
            <div className="group/tablist relative overflow-x-auto scrollbar-hide h-full w-max min-w-full flex items-center">
              
              <div 
                role="tablist" 
                className={clsx(
                  'tabs tabs-lift tabs-lg flex whitespace-nowrap h-full transition-colors duration-200 tabs-no-border',
                  {
                    'text-[var(--np-color-primary)]': !topic,
                    'group-hover/tablist:bg-[var(--np-color-primary)] group-hover/tablist:text-background': true
                  }
                )}
              >
                {topics?.map((t: Topic, i) => {
                  const route = t.name.replace(/ /g, '-');
                  const isActive = pathname === `/${route}` || pathname.startsWith(`/${route}/`);
                  return (
                    <Link 
                      key={t.id}
                      role="tab" 
                      href={`/${route}`}
                      onClick={() => handlePageChange(t)}
                      className={clsx(
                        'tab tab-lifted h-full flex-shrink-0 transition-colors hover:bg-background hover:z-50',
                        {
                          'tab-active bg-[var(--np-color-primary)] text-[var(--np-background) z-50': isActive,
                          'group-hover/tablist:text-background': !isActive,
                          'text-[var(--np-color-primary)] hover:bg-[var(--np-color-primary)] hover:tab-active': !isActive && !topic
                        }
                      )}
                    >
                      {t.name}
                    </Link>  
                  );
                })}
              </div>
            </div> 
          </div>
        </div>
      </div>
    )
  }

  const SearchStatusBar = () => {
    return (
      <AnimatePresence>
        <motion.div
          key="search-status"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height:!isSearchOpen ? 'auto': 0}}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
          //className="overflow-hidden"
        >
          <div className="px-4 py-2 text-sm border-t bg-[var(--np-color-primary)] text-background">
            {isTyping && <span>Typing...</span>}
            {isSearching && !isTyping && <span>Searching for "{localSearchValue}"...</span>}
            {searchParams && err && err.statusCode ===204 && !isTyping && <span>No articles found</span>}
            {searchParams && !err && !isTyping && <span>Found articles: {data?.total}</span>}
          </div>
        </motion.div>
      </AnimatePresence>
    )
  }

  if (error) return (
    <header className="bg-background border-b-2">
      <GridHeaderTop />
    </header>
  );

  if (loadingHeader) {
    return (
      <header className="bg-background border-b-2">
        <div className="container m-auto">
          <div className="text-center">Loading header...</div>
        </div>
      </header>
    );
  } else {
    return (
      <div className="pb-1 border-b-2 bg-background relative">
        <header className="border-b">
          <GridHeaderTop />
          <div className="hidden md:block">
            <GridHeaderBottom />
          </div>
          <div className="md:hidden">
            <GridHeaderBottomMobile />
          </div>
          {((searchParams || isTyping) && !isSearchOpen) && (
            <SearchStatusBar />
          )}
        </header>
        {loadingArticles && <progress className="progress w-full bottom-0 absolute"></progress>} 
      </div>
      );
    }    
}