'use client';

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { articlesService } from "@/services/articlesService";
import { useArticles } from "@/contexts/ArticlesContext";
import { ArticlePageProps } from "@/types/pages";
import { ArticleBlockTop } from "../ui/ArticleBlockTop";
import { ArticleList } from "../ui/ArticleList";
import { PageFooter } from "../ui/PageFooter";
import { Article, ApiError } from "@/types";
import { ErrorPage } from "./ErrorPage";
import { AnimatePresence, motion } from "framer-motion";
import { SearchComponent } from "../ui/SearchComponent";
import { WeatherBlock } from "../ui/WeatherBlock";
import { LoadingPage } from "./LoadingPage";
import { formatDate } from "@/utils/utils";

const GridArticlePage = ({article}: { article:Article}) => {

  return (
    <>
      <div className="grid-item-article-page-block">
        <ArticleBlockTop article={article}/>
      </div>
      <div className="grid-item-article-list bg-article-list">
        <ArticleList title="Other Top Stories"/>
      </div>
      <div className="col-span-2 row-span-1 col-start-9 row-start-5 bg-[var(--np-foreground)] border-t flex flex-col font-secondary px-4 py-8 gap-8">
        <div className="flex-1 flex flex-row w-full justify-center gap-12">
          <div className="flex flex-row gap-3">
            <div className="content-center">
              <img src="/accent.png" className="h-[11px]"/>
            </div>
            <div>
              <div className="font-bold text-xs text-gray-600">Source</div>
              <div style={{lineHeight:'12px'}}>{article.source}</div>
            </div>
          </div>
          <div className="flex flex-row gap-3">
            <div className="content-center">
              <img src="/accent.png" className="h-[11px]"/>
            </div>
            <div>
              <div className="font-bold text-xs text-gray-600">Published</div>
              <div style={{lineHeight:'12px'}}>{formatDate(article.published_at)}</div>
            </div>
          </div>
        </div>
        <div className="divider w-full before:bg-gray-600 after:bg-gray-600 my-0 before:h-[1px] after:h-[1px]"></div>
        <div className="flex-1 font-bold text-xs text-gray-600 hover:cursor-pointer hover:opacity-70 w-full flex flex-row gap-2 justify-center">
          <p className="self-center">Read Original Article</p>
          <a className="text-gray-600 hover:cursor-pointer" href={article.url}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-redo-icon lucide-redo"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"/></svg>
          </a>
        </div>
      </div>
    </>
  )
}

export default function ArticlePage({ id }: ArticlePageProps) {
  const {error, data, isSearchOpen, isSearching, searchParams} = useArticles();
  const [articleData, setArticleData] = useState<Article>();
  const [isLoading, setIsLoading] = useState(!id);
  const [isError, setIsError] = useState<ApiError>();

  useEffect(() => {
      const fetchArticle = async () => {
        try {
          setIsLoading(true);
          const article:Article = await articlesService.getArticleById(id);
          setArticleData(article);
        } catch (error) {
          setIsError(isError as ApiError)
          console.error('Error fetching article:', error);
        } finally {
          setIsLoading(false);
        }
      };
      if (id) fetchArticle();
  }, [id]);

 

  if (isLoading) {
    return (
      <LoadingPage text="Loading article.."/>
    );
  }

  if (isError) {
    return (
      <ErrorPage error={isError}/>
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
            className="overflow-hidden"
          >
            <SearchComponent /> 
          </motion.div>
        )}
      </AnimatePresence>

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
              {!isSearchOpen && data &&
              <>
                <div className="grid-item-article-list bg-article-list border-l">
                  <ArticleList title={`Search results: ${data.articles.length}`} articles={!error ? data.articles : []}/> 
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
            <div className="grid-article-page border-t-2">
              {articleData && <GridArticlePage article={articleData}/>}
              <div className="footer footer-front-page row-start-11 border-t-8">
                <PageFooter/>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}