'use client';

import clsx from 'clsx';
import { useRouter, useSearchParams } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef, useState} from 'react';
import { useArticles } from '@/contexts/ArticlesContext';
import { usePage } from '@/contexts/PageContext';
import { ArticleList } from '../ui/ArticleList';
import { PageFooter } from '../ui/PageFooter';
import { SearchComponent } from '../ui/SearchComponent';
import { WeatherBlock } from '../ui/WeatherBlock';
import { ErrorPage } from './ErrorPage';
import { ArticleBlockBottom } from '../ui/ArticleBlockBottom';
import { ArticleBlockSide } from '../ui/ArticleBlockSide';
import { ArticleBlockTop } from '../ui/ArticleBlockTop';
import { Article } from '@/types';



const CategoryPageGrid = ({ loadMore }:{ loadMore:()=>void }) => {
  const { data, loading } = useArticles();
  const articles = data?.articles || [];
  const total = data?.total || 0;
  const hasMore = articles.length < total;
  const [gridChunks, setGridChunks] = useState<Article[][]>([]);
  const gridRefs = useRef<(HTMLDivElement | null)[]>([]);


   useEffect(() => {
    const articlesPerGrid = 4;
    const newChunks = [];
    for (let i = 0; i < articles.length; i += articlesPerGrid) {
      newChunks.push(articles.slice(i, i + articlesPerGrid));
    }
    setGridChunks(newChunks);
  }, [articles]); 


  const handleScrollUp = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    }); 
  };

  const remainingArticles = Math.max(0, total - articles.length);
  const GridLayout = ({chunkArticles, gridIndex}:{chunkArticles:Article[], gridIndex:number}) => {
    return (
      <>
        <div className="grid-item-article-block-side">
          {chunkArticles[2] && <ArticleBlockSide article={chunkArticles[2]}/>}
        </div>
        
        {gridIndex === 0 && <div className="grid-item-article-list bg-article-list">
          <div className='max-h-0'>
            <ArticleList title="Other Top Stories"/> 
          </div>
        </div>}
        
        <div className="col-span-5 row-span-1 col-start-4 row-start-1">
          <ArticleBlockTop article={chunkArticles[0]}/>
        </div>
        
        <div className="grid-item-article-block-bottom">
          {chunkArticles[3] && <ArticleBlockBottom article={chunkArticles[3]}/>}
        </div>
        
        <div className="grid-item-article-block">
          {chunkArticles[1] && <ArticleBlockTop article={chunkArticles[1]}/>}
        </div>
        
        <div className="grid-item-foreground-block text-center content-center">
          {gridIndex === gridChunks.length - 1 && hasMore && remainingArticles > 0 ? 
            <button
                onClick={loadMore}
                className="border-b border-[var(--np-color-primary)] py-2 mx-auto font-bold mb-4 w-[50%] hover:text-secondary hover:border-secondary transition-colors inline-block"
              >
                {loading ? 'Loading...' : 'View More Stories'}
              </button>
              :
              <div className="content-center h-full">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="m-auto h-16 text-background">
                  <path d="M16.555 5.412a8.028 8.028 0 0 0-3.503-2.81 14.899 14.899 0 0 1 1.663 4.472 8.547 8.547 0 0 0 1.84-1.662ZM13.326 7.825a13.43 13.43 0 0 0-2.413-5.773 8.087 8.087 0 0 0-1.826 0 13.43 13.43 0 0 0-2.413 5.773A8.473 8.473 0 0 0 10 8.5c1.18 0 2.304-.24 3.326-.675ZM6.514 9.376A9.98 9.98 0 0 0 10 10c1.226 0 2.4-.22 3.486-.624a13.54 13.54 0 0 1-.351 3.759A13.54 13.54 0 0 1 10 13.5c-1.079 0-2.128-.127-3.134-.366a13.538 13.538 0 0 1-.352-3.758ZM5.285 7.074a14.9 14.9 0 0 1 1.663-4.471 8.028 8.028 0 0 0-3.503 2.81c.529.638 1.149 1.199 1.84 1.66ZM17.334 6.798a7.973 7.973 0 0 1 .614 4.115 13.47 13.47 0 0 1-3.178 1.72 15.093 15.093 0 0 0 .174-3.939 10.043 10.043 0 0 0 2.39-1.896ZM2.666 6.798a10.042 10.042 0 0 0 2.39 1.896 15.196 15.196 0 0 0 .174 3.94 13.472 13.472 0 0 1-3.178-1.72 7.973 7.973 0 0 1 .615-4.115ZM10 15c.898 0 1.778-.079 2.633-.23a13.473 13.473 0 0 1-1.72 3.178 8.099 8.099 0 0 1-1.826 0 13.47 13.47 0 0 1-1.72-3.178c.855.151 1.735.23 2.633.23ZM14.357 14.357a14.912 14.912 0 0 1-1.305 3.04 8.027 8.027 0 0 0 4.345-4.345c-.953.542-1.971.981-3.04 1.305ZM6.948 17.397a8.027 8.027 0 0 1-4.345-4.345c.953.542 1.971.981 3.04 1.305a14.912 14.912 0 0 0 1.305 3.04Z" />
                </svg>
                <button onClick={handleScrollUp}>Scroll to Top</button>
              </div>
          }
        </div>
      </>
    )
  }

  const GridLayoutAlt = ({chunkArticles, gridIndex}:{chunkArticles:Article[], gridIndex:number}) => {
        return (
      <>
        <div className="grid-item-article-block-top-alt">
          <ArticleBlockTop article={chunkArticles[0]}/>
        </div>
        <div className= "col-span-10 md:col-span-4 row-span-1 col-start-1 md:col-start-7 row-start-2 md:row-start-1">
          {chunkArticles[2] && <ArticleBlockSide article={chunkArticles[2]}/>}
        </div>

        <div className="col-span-10 md:col-span-4 row-span-1 row-start-4 md:row-start-2 ">
          {chunkArticles[3] && <ArticleBlockBottom article={chunkArticles[3]}/>}
        </div>
        
        <div className="col-span-10 md:col-span-6 row-span-1 md:row-span-2 col-start-1 row-start-3 md:col-start-5 md:row-start-2">
          {chunkArticles[1] && <ArticleBlockTop article={chunkArticles[1]}/>}
        </div>
        
        <div className="grid-item-foreground-block row-start-5 md:row-start-3 text-center content-center">
          {gridIndex === gridChunks.length - 1 && hasMore && remainingArticles > 0 ? 
            <button
                onClick={loadMore}
                className="border-b border-[var(--np-color-primary)] py-2 mx-auto font-bold mb-4 w-[50%] hover:text-secondary hover:border-secondary transition-colors inline-block"
              >
                {loading ? 'Loading...' : 'View More Stories'}
              </button>
              :
              <div className="content-center h-full">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="m-auto h-16 text-background">
                  <path d="M16.555 5.412a8.028 8.028 0 0 0-3.503-2.81 14.899 14.899 0 0 1 1.663 4.472 8.547 8.547 0 0 0 1.84-1.662ZM13.326 7.825a13.43 13.43 0 0 0-2.413-5.773 8.087 8.087 0 0 0-1.826 0 13.43 13.43 0 0 0-2.413 5.773A8.473 8.473 0 0 0 10 8.5c1.18 0 2.304-.24 3.326-.675ZM6.514 9.376A9.98 9.98 0 0 0 10 10c1.226 0 2.4-.22 3.486-.624a13.54 13.54 0 0 1-.351 3.759A13.54 13.54 0 0 1 10 13.5c-1.079 0-2.128-.127-3.134-.366a13.538 13.538 0 0 1-.352-3.758ZM5.285 7.074a14.9 14.9 0 0 1 1.663-4.471 8.028 8.028 0 0 0-3.503 2.81c.529.638 1.149 1.199 1.84 1.66ZM17.334 6.798a7.973 7.973 0 0 1 .614 4.115 13.47 13.47 0 0 1-3.178 1.72 15.093 15.093 0 0 0 .174-3.939 10.043 10.043 0 0 0 2.39-1.896ZM2.666 6.798a10.042 10.042 0 0 0 2.39 1.896 15.196 15.196 0 0 0 .174 3.94 13.472 13.472 0 0 1-3.178-1.72 7.973 7.973 0 0 1 .615-4.115ZM10 15c.898 0 1.778-.079 2.633-.23a13.473 13.473 0 0 1-1.72 3.178 8.099 8.099 0 0 1-1.826 0 13.47 13.47 0 0 1-1.72-3.178c.855.151 1.735.23 2.633.23ZM14.357 14.357a14.912 14.912 0 0 1-1.305 3.04 8.027 8.027 0 0 0 4.345-4.345c-.953.542-1.971.981-3.04 1.305ZM6.948 17.397a8.027 8.027 0 0 1-4.345-4.345c.953.542 1.971.981 3.04 1.305a14.912 14.912 0 0 0 1.305 3.04Z" />
                </svg>
                <button onClick={handleScrollUp}>Scroll to Top</button>
              </div>
          }
        </div>
      </>
    )
  }

  return (
    <>
      {gridChunks.map((chunkArticles, gridIndex) => (
        <>
          <div className='hidden lg:block overflow-hidden'>
             <div 
                key={`grid-${gridIndex}`}   
                className='grid-category-page'
                ref={el => { gridRefs.current[gridIndex] = el; }}
              >
                <GridLayout chunkArticles={chunkArticles} gridIndex={gridIndex}/>
              </div>
          </div>
          <div className='lg:hidden'>
            <div 
                key={`grid-${gridIndex}`}   
                className='grid-category-page'
                ref={el => { gridRefs.current[gridIndex] = el; }}
              >
                <GridLayoutAlt chunkArticles={chunkArticles} gridIndex={gridIndex}/>
              </div>
          </div>
        </>
      ))}
    </>
  );
};


CategoryPageGrid.displayName = 'CategoryPageGrid';


export const CategoryPageClient = ({ category }: {category:string}) => {

  const { error, data, isSearchOpen, isSearching, searchParams, refreshArticles } = useArticles();
  const { source, topic } = usePage();
  const urlParams = useSearchParams();
  const router = useRouter();
  const currentPage = parseInt(urlParams.get('page') || '1');
  const pageSize = 4;
  
  const [isLoading, setIsLoading] = useState(false);


  const loadMore = () => {
    if (isLoading) return;
    setIsLoading(true);
    const skip = (currentPage) * pageSize;
    refreshArticles({ source, topic, skip }).then(() => {
      router.push(`/${category.replace(/ /g, '-')}/?page=${currentPage + 1}`, {scroll: false});
    }).finally(() => {
      setIsLoading(false);
      scrollView();
    });
  }

  const scrollView = () => {
    const gridElements = document.getElementsByClassName('grid-category-page');
    if (gridElements.length > 0) {
      const lastGridElement = gridElements[gridElements.length - 1] as HTMLElement;
      lastGridElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  if (error && error.statusCode !== 204) {
    return <ErrorPage error={error} />;
  }

  return (
    <div className="mx-auto bg-background">
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
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
          {!isSearchOpen && data && (
            <div className="grid-search-view">
              <div className="grid-item-article-list bg-hoverborder-l">
                <div className="max-h-0">
                  <ArticleList 
                    title={`Search results: ${data.articles.length}`} 
                  /> 
                </div>
              </div>
              <div className="grid-item-foreground-block row-start-9">
                <WeatherBlock/>
              </div>
            </div>
          )}
            <div className="footer-front-page border-t-8">
              <PageFooter/>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="search-results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4, ease: 'easeInOut' }}
          >
            {data && data.total > 0 && 
              <CategoryPageGrid loadMore={loadMore}/>
            }
            {isLoading && <progress className="progress w-full bottom-0 absolute"></progress>}
          </motion.div>
        )}
      </AnimatePresence>
    </div>   
  );
};
