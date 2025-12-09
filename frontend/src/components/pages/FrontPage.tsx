'use client'; 

import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { usePage } from "@/contexts/PageContext";
import { useArticles } from "@/contexts/ArticlesContext";
import { ArticleList } from "../ui/ArticleList";
import { ArticleBlockTop } from "../ui/ArticleBlockTop";
import { ArticleBlockSide } from "../ui/ArticleBlockSide";
import { ArticleBlockBottom } from "../ui/ArticleBlockBottom";
import { PageFooter } from "../ui/PageFooter";
import { WeatherBlock } from "../ui/WeatherBlock";
import { SearchComponent } from "../ui/SearchComponent";
import { ErrorPage } from "./ErrorPage";
import { Article } from "@/types";

const GridFrontPage = ({articles}: {articles:Article[]}) => {
  return (
    <div className="overflow-hidden bg-primary">
      <div className="grid-front-page">
        <div className="grid-item-article-block-side">
          <ArticleBlockSide article={articles[2]}/>
        </div>
        <div className="grid-item-article-list bg-article-list">
          <div className="max-h-0">
            <ArticleList title="Other Top Stories" /> 
          </div>
        </div>
        <div className="grid-item-article-block-top">
          <ArticleBlockTop article={articles.find(article => article.image_url !== article.url) || articles[0]}/>
        </div>
        <div className="grid-item-article-block-bottom">
          <ArticleBlockBottom article={articles[3]}/>
        </div>
        <div className="grid-item-article-block row-start-2">
          <ArticleBlockTop article={articles[1]}/>
        </div>
        <div className="grid-item-foreground-block">
          <WeatherBlock/>
        </div>
      </div>
      <div className="footer-front-page border-t-8">
        <PageFooter/>
      </div>
    </div>
  )
}

const GridFrontPageAlt = ({articles}: {articles:Article[]}) => {
  return (
    <>
      <div className="grid-front-page">
        <div className="col-span-10 md:col-span-6 row-span-1 col-start-1 row-start-1">
          <ArticleBlockTop article={articles.find(article => article.image_url !== article.url) || articles[0]}/>
        </div>
        <div className="hidden md:block col-span-4 row-span-1 col-start-7 row-start-1 overflow-scroll rounded-tl-md max-h-[60vh] bg-article-list">
          <ArticleList title="Other Top Stories" />
        </div>
        <div className="grid-item-article-block-side-alt">
          <ArticleBlockSide article={articles[2]}/>
        </div>
        <div className="col-span-10 md:col-span-6 row-span-1 col-start-1 md:col-start-5 row-start-3 md:row-start-2 ">
          <ArticleBlockTop article={articles[1]}/>
        </div>
        <div className="col-span-10 md:col-span-6 row-span-1 bg-foreground">
          <WeatherBlock/>
        </div>
        <div className="col-span-10 md:col-span-4 row-span-1 col-start-1 md:col-start-7 row-start-4 md:row-start-3">
          <ArticleBlockSide article={articles[3]}/>
        </div>
      </div>
      <div className="footer-front-page border-t-8">
        <PageFooter/>
      </div>
    </>
  )
}

export default function FrontPage(){
  const {error, data, refreshArticles, isSearching, searchParams, isSearchOpen} = useArticles();
  const { source } = usePage();
  
  useEffect(() => {
    if (source) refreshArticles({source, topic:null});
  }, [source]);

  if (error && error.statusCode !== 204) {
    return (
      <ErrorPage error={error}/>
    );
  }

  return (
      <>
        {/* Search Component */}
        <AnimatePresence>
          {isSearchOpen && (
            <motion.div
              key="search-component"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.4, ease: 'easeInOut' }}
            >
              <SearchComponent /> 
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
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
              {!isSearchOpen && data &&
                <div className="grid-search-view"> 
                  <div className="grid-item-article-list bg-hoverborder-l">
                    <div className="max-h-0">
                      <ArticleList title={`Search results: ${data.articles.length}`} /> 
                    </div>
                  </div>
                  <div className="grid-item-foreground-block">
                    <WeatherBlock/>
                  </div>
                </div>}
              <div className="footer-front-page border-t-8">
                <PageFooter/>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="front-page"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4, ease: 'easeInOut' }}
            >
              {data && 
              <>
                <div className="hidden lg:block">
                  <GridFrontPage articles={data.articles}/>
                </div>
                <div className="lg:hidden">
                  <GridFrontPageAlt articles={data.articles}/>
                </div>
              </>
              }
            </motion.div>
          )}
        </AnimatePresence>
      </>
  );
}