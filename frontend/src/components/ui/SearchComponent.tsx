import { AnimatePresence, motion } from "framer-motion"
import { useArticles } from "@/contexts/ArticlesContext";
import { ArticleList } from "./ArticleList";
import { AdvancedSearchForm } from "./AdvancedSearchForm";
import clsx from "clsx";


export const SearchComponent = () => {
  const { isSearching, data, loading, searchParams, error } = useArticles();

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
        className="overflow-hidden"
      >
        <div className="border-b border-t-2 h-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-0 bg-[var(--np-color-primary)]">
            {/* Search Form Side */}
            <div className="bg-[var(--np-background)] p-6 rounded-tr-lg">
              <div className="p-4 rounded-lg border mb-4">
                 <h3 className="font-semibold text-sm mb-2">Search Tips:</h3>
                 <ul className="text-xs space-y-1">
                   <li>• Use quotes for exact phrases: "artificial intelligence"</li>
                   <li>• Combine content and title searches for better results</li>
                   <li>• Use date range to filter recent or historical articles</li>
                 </ul>
              </div>
              <AdvancedSearchForm/> 
            </div>
            
            {/* Results Side */}
            <div className={
              clsx(
                "font-primary bg-[var(--np-background)] px-4 overflow-auto min-h-[500px] border-l", 
                {"content-center" : isSearching}
              )}>
              {/* Loading State */}
              {(isSearching && !loading && !error) && (
                <div className="text-center text-[var(--np-foreground)]">
                  <div className="loading loading-spinner loading-lg mb-4"></div>
                  <p className="text-lg font-helvetica">Searching articles...</p>
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
                  >
                    <div className="text-center">
                      <p className="text-lg font-helvetica text-[var(--np-foreground)]">No results found</p>
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