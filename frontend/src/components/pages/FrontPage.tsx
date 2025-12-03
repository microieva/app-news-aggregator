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
    <>
      <div className="grid-item-article-block-side">
        <ArticleBlockSide article={articles[2]}/>
      </div>
      <div className="grid-item-article-list bg-article-list">
        <ArticleList title="Other Top Stories" /> 
      </div>
      <div className="grid-item-article-block-top">
        <ArticleBlockTop article={articles.find(article => article.image_url !== article.url) || articles[0]}/>
      </div>
      <div className="grid-item-article-block-bottom">
        <ArticleBlockBottom article={articles[3]}/>
      </div>
      <div className="grid-item-article-block">
        <ArticleBlockTop article={articles[1]}/>
      </div>
      <div className="grid-item-foreground-block row-start-9">
        <WeatherBlock/>
      </div>
      <div className="footer footer-front-page row-start-11 border-t-8">
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
              //className="overflow-hidden"
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
              //className="overflow-hidden"
            >
              <div className="grid-search-view">
                {!isSearchOpen && data &&
                <>
                  <div className="grid-item-article-list bg-article-list border-l">
                    <ArticleList title={`Search results: ${data.articles.length}`} /> 
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
              //className="overflow-hidden"
            >
              {data && 
                <div className="grid-front-page">
                  <GridFrontPage articles={data.articles}/>
                </div>}
            </motion.div>
          )}
        </AnimatePresence>
      </>
  );
}