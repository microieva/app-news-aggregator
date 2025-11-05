import articlesService from "@/services/articlesService";
import { ApiError, ArticlesData } from "@/types/api";
import { Article } from "@/types/article";
import { useEffect, useState } from "react";
import { ArticleList } from "../ui/ArticleList";
import { ArticleBlockTop } from "../ui/ArticleBlockTop";
import { ArticleBlockSide } from "../ui/ArticleBlockSide";
import { ArticleBlockBottom } from "../ui/ArticleBlockBottom";
import { FrontPageFooter } from "../ui/FrontPageFooter";
import { WeatherBlock } from "../ui/WeatherBlock";

export default function FrontPage(){
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<ApiError>();
  
    useEffect(() => {
      const fetchArticles = async () => {
        try {
          setLoading(true);
          const data: ArticlesData = await articlesService.getArticles()
          setArticles(data.articles || []);
        } catch (error) {
          setError(error as ApiError);
        } finally {
          setLoading(false);
        }
      };
  
        fetchArticles();
    }, []);
  
    if (loading) {
      return (
        <div className="wrapper">
          <div className="text-center mx-auto">Loading top stories...</div>
        </div>
      );
    }
    if (error) {
      return (
        <div className="mx-auto wrapper">
          <div className="mt-40 m-auto text-center">
            <p>Error: {error.statusCode} - {error.message}</p>
            <p><em>{error.detail}</em></p>
          </div>
        </div>
      );
    }
  
  return (
    <div className="grid-front-page">
      <div className="grid-item-article-block-side" >
        <ArticleBlockSide article={articles[2]}/>
      </div>
      <div className="grid-item-article-list bg-article-list">
        <ArticleList /> 
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
        <FrontPageFooter/>
      </div>
    </div>
  );
}