import clsx from "clsx";
import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion"
import { useArticles } from "@/contexts/ArticlesContext";
import { ArticleList } from "./ArticleList";
import { AdvancedSearchForm } from "./AdvancedSearchForm";


export const SearchComponent = () => {
  const { isSearching, data, loading, searchParams, error, clearSearch } = useArticles();
  
  useEffect(() => {
    const el = document.getElementById('search-results');
    const mediaQuery = window.matchMedia('(max-width: 767px)');
    
    if (mediaQuery.matches && (loading || searchParams)) {
      if (el) {
        setTimeout(() => {
          el.scrollIntoView({behavior:'smooth'});
        }, 300); 
      }
    }
  }, [loading, searchParams]); 

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
      >
        <div className="border-b border-t-2">
          <div className={
            clsx("grid grid-cols-1 md:grid-cols-2 grid-rows-2 md:grid-rows-1 gap-0 bg-primary ",
              {"xs:grid-rows-1":!loading && !searchParams}
            )
          }>
            {/* Search Form Side */}
            <div className="bg-background p-6 rounded-tr-lg h-full">
              <div className="p-4 rounded-lg border mb-4">
                 <p className="font-semibold mb-2">Search Tips:</p>
                 <ul className="text-xs space-y-1">
                   <li>• Use quotes for exact phrases: "artificial intelligence"</li>
                   <li>• Combine content and title searches for better results</li>
                   <li>• Use date range to filter recent or historical articles</li>
                 </ul>
              </div>
              <AdvancedSearchForm/> 
            </div>
            
            {/* Results Side */}
            <div id="search-results" className={
              clsx(
                "font-primary bg-background px-4 overflow-y-scroll border-t md:border-l", 
                {"content-center" : isSearching},
                {"xs:h-0 md:h-full": !loading && !searchParams}
              )}>
              {/* Loading State */}
              {(isSearching && !loading && !error) && (
                <div className="text-center text-foreground">
                  <div className="loading loading-spinner loading-lg mb-4"></div>
                  <p className="text-sm font-secondary">Searching articles..</p>
                </div>
              )}
              
              {/* Results State */}
              {!isSearching && searchParams && data && data.total > 0 && (
                <AnimatePresence>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5, ease: 'easeInOut' }}
                    className="max-h-0"
                  >
                    <ArticleList title={`Search results: ${data.total}`} articles={!error ? data.articles : []}/>
                  </motion.div>
                </AnimatePresence>
              )}
              
              {/* No Results State */}
              {error && error.statusCode===204 && searchParams && (
                <AnimatePresence>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5, ease: 'easeInOut' }}
                    className="content-center h-full"
                  >
                    <div className="text-center flex flex-col gap-2 font-secondary">
                      <div className="text-sm text-foreground font-bold">No results found</div>
                      <div className="text-xs text-foreground">Try modifying your filters</div>
                    </div>
                  </motion.div>
                </AnimatePresence>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}