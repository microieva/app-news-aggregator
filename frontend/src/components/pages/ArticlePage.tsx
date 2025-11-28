import { useRouter } from "next/router";
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

const GridArticlePage = ({article}: { article:Article}) => {
    const { data } = useArticles();
    return (
      <>
        <div className="grid-item-article-page-block">
          <ArticleBlockTop article={article}/>
        </div>
        <div className="grid-item-article-list bg-article-list">
          {data && <ArticleList articles={data.articles} title="Other Top Stories"/>}
        </div>
        <div className="col-span-2 row-span-1 col-start-9 row-start-5 bg-[var(--np-foreground)] border-t">
          <p>More details about source</p>
          <p>link to original</p>
          <p>content</p>
          <p>-</p>
          <p>-</p>
        </div>
      </>
    )
  }

export default function ArticlePage({ id }: ArticlePageProps) {
  const router = useRouter();
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

 

  if (router.isFallback || isLoading) {
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