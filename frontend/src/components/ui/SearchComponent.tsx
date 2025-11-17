import { AnimatePresence, motion } from "framer-motion"
import { useArticles } from "@/contexts/ArticlesContext";
import { ArticleList } from "./ArticleList";
import { AdvancedSearchForm } from "./AdvancedSearchForm";

export const SearchComponent = () => {
  const { isSearching, articles, loading, searchParams } = useArticles();

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
            <div className="font-primary bg-[var(--np-background)] px-4 overflow-auto min-h-[500px] border-l">
              {/* Loading State */}
              {(isSearching && articles.length === 0) && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="loading loading-spinner loading-lg mb-4"></div>
                    <p className="text-lg font-helvetica">Searching articles...</p>
                  </div>
                </div>
              )}
              
              {/* Results State */}
              {isSearching && searchParams && articles.length > 0 && (
                <AnimatePresence>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5, ease: 'easeInOut' }}
                  >
                    <ArticleList/>
                  </motion.div>
                </AnimatePresence>
              )}
              
              {/* No Results State */}
              {!loading && !isSearching && articles.length === 0 && searchParams && (
                <div className="flex items-center justify-center h-full min-h-[400px]">
                  <div className="text-center">
                    <div className="text-4xl mb-4">🔍</div>
                    <p className="text-lg font-semibold mb-2">No articles found</p>
                    <p className="text-sm opacity-70">Try different search terms or filters</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}