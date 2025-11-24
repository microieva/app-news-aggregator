import { useEffect } from 'react';
import { AnimatePresence, motion } from "framer-motion";
import { ArticleList } from '../ui/ArticleList';
import { ArticleBlockSide } from '../ui/ArticleBlockSide';
import { ArticleBlockTop } from '../ui/ArticleBlockTop';
import { ArticleBlockBottom } from '../ui/ArticleBlockBottom';
import { usePage } from '@/contexts/PageContext';
import { useArticles } from '@/contexts/ArticlesContext';
import { Article } from '@/types/article';
import { ErrorPage } from './ErrorPage';
import { SearchComponent } from '../ui/SearchComponent';
import { WeatherBlock } from '../ui/WeatherBlock';
import { PageFooter } from '../ui/PageFooter';


export default function CategoryPage() {
  const { source, topic } = usePage();
  const {loading, error, articles, refreshArticles, isSearchOpen, isSearching, searchParams} = useArticles();

  const CategoryPageGrid = ({ articles }: { articles: Article[] }) => {
    const pageArticles = articles.slice(0, 6);

    return (
      <>
        <div className="grid-item-article-block-side" >
          {pageArticles[2] && <ArticleBlockSide article={pageArticles[2]}/>}
        </div>
        <div className="grid-item-article-list bg-article-list">
          <ArticleList title="Other Top News" articles={articles}/> 
        </div>
        <div className="grid-item-article-block-top">
          <ArticleBlockTop article={pageArticles.find(article => article.image_url !== article.url) || pageArticles[0]}/>
        </div>

        <div className="grid-item-article-block-bottom">
          {pageArticles[3] && <ArticleBlockBottom article={pageArticles[3]}/>}
        </div>
        <div className="grid-item-article-block">
          {pageArticles[1] && <ArticleBlockTop article={pageArticles[1]}/>}
        </div>
        <div className="grid-item-foreground-block row-start-9">
          show used sources & IF at least 4 more articles, then button to load more stories
        </div>
      </>
    )
  }

   useEffect(() => {
      refreshArticles({topic:topic || null, source});
  }, [source, topic]);


  if (loading) {
    return (
      <div className="mx-auto wrapper">
        <div className="text-center mx-auto">Loading articles for {topic?.name}...</div>
      </div>
    );
  }
  if (error && error.statusCode !==204) {
      return (
        <ErrorPage error={error} />
      );
    }

  return (
  <div className="mx-auto bg-[var(--np-background)]">
    {/* Search Component */}
    <AnimatePresence>
      {isSearchOpen && (
        <motion.div
          key="search-component"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.4, ease: 'easeInOut' }}
          className="overflow-hidden"
        >
          <SearchComponent /> 
        </motion.div>
      )}
    </AnimatePresence>

    {/* Category Content */}
    <AnimatePresence>
      {!error && (isSearching || searchParams) ? (
        <motion.div
          key="search-results"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0 , height:0}}
          transition={{ duration: 0.4, ease: 'easeInOut' }}
          className="overflow-hidden"
        >
          <div className="grid-search-view">
            {!isSearchOpen && 
            <>
              <div className="grid-item-article-list bg-article-list border-l">
                <ArticleList title={`Search results: ${articles.length}`} articles={!error ? articles : []}/> 
              </div>
              <div className="grid-item-foreground-block row-start-9">
                <WeatherBlock/>
              </div>
            </>}
            <div className="footer footer-front-page row-start-11 border-t-8">
              <PageFooter/>
            </div>
          </div>
        </motion.div>
      ) : (
        <motion.div
          key="front-page"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4, ease: 'easeInOut' }}
          className="overflow-hidden"
        >
            <div className="grid-category-page min-h-[calc(100vh - 10rem)]">
              <CategoryPageGrid articles={articles}/>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  </div>   
);
}