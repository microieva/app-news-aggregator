import { useEffect } from "react";
import { ArticleList } from "../ui/ArticleList";
import { ArticleBlockTop } from "../ui/ArticleBlockTop";
import { ArticleBlockSide } from "../ui/ArticleBlockSide";
import { ArticleBlockBottom } from "../ui/ArticleBlockBottom";
import { FrontPageFooter } from "../ui/FrontPageFooter";
import { WeatherBlock } from "../ui/WeatherBlock";
import { usePage } from "@/contexts/PageContext";
import { useArticles } from "@/contexts/ArticlesContext";

export default function FrontPage(){
  const {loading, error, articles, refreshArticles} = useArticles();
  const { source } = usePage();
  
    useEffect(() => {
      if (source) refreshArticles({source, topic:null});
    }, [source]);
  
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
          <div className="text-center h-full content-center">
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