'use client';

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
import { LoadingPage } from "./LoadingPage";
import { formatDate } from "@/utils/utils";
import Link from "next/link";

const GridArticlePage = ({article}: { article:Article}) => {
  return (
    <>
      <div className="grid-item-article-page-block">
        <ArticleBlockTop article={article}/>
      </div>
      <div className="grid-item-article-list bg-hoverhidden lg:block">
        <div className="h-[60vh] min-h-0">
          <ArticleList title="Other Top Stories"/>
        </div>
      </div>

      <div 
        className="
          lg:col-span-2 
          col-span-10 
          row-span-1 
          col-start-1 
          lg:col-start-9 
          row-start-2 
          bg-foreground 
          border-t 
          flex 
          flex-row 
          lg:flex-col 
          font-secondary 
          px-4 py-8 gap-8"
        >
        <div className="flex-1 flex flex-row w-full justify-center gap-4 md:gap-12">
          <div className="flex flex-row gap-2 md:gap-3">
            <div className="content-center">
              <img src="/accent.png" className="h-4 w-auto md:h-8 lg:h-[11px]"/>
            </div>
            <div className="content-center text-xs md:text-sm flex-shrink-0">
              <p className="font-bold text-secondary lg:text-xs">Source</p>
              <p className="lg:pt-2">{article.source}</p>
            </div>
          </div>
          <div className="flex flex-row gap-2 md:gap-3">
            <div className="content-center">
              <img src="/accent.png" className="h-4 w-auto md:h-8 lg:h-[11px]"/>
            </div>
            <div className="content-center text-xs md:text-sm flex-shrink-0">
              <p className="font-bold text-secondary lg:text-xs">Published</p>
              <p className="lg:pt-2">{formatDate(article.published_at)}</p>
            </div>
          </div>
        </div>
        <div className="hidden lg:block">
          <div className="divider before:bg-secondary after:bg-secondary my-0 before:h-[1px] after:h-[1px]"></div>
        </div>
        <div className="lg:hidden self-center">
          <div className="divider divider-vertical before:bg-secondary after:bg-secondary before:h-[3rem] after:h-[3rem] before:w-[1px] after:w-[1px]"></div>
        </div>
        {article.url && 
        <div className="flex-1 font-bold text-xs text-secondary hover:cursor-pointer hover:opacity-70 w-full content-center">
          <Link 
            className="text-secondary hover:cursor-pointer flex gap-4 justify-center" 
            href={article.url} 
            target="_blank"
          >
            <p className="self-center">Read Original Article</p>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-redo-icon lucide-redo"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"/></svg>
          </Link>
        </div>}
      </div>
    </>
  )
}

export default function ArticlePage({ id }: ArticlePageProps) {
  const {isSearchOpen} = useArticles();
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
      <motion.div
        key="article-page"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.4, ease: 'easeInOut' }}
        className="overflow-hidden bg-primary"
      >
        {articleData && 
          <div className="grid-article-page border-t-2">
            <GridArticlePage article={articleData}/>
          </div> 
        }
        <div className="footer-front-page border-t-8">
          <PageFooter/>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}