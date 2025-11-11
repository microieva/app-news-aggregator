import {articlesService} from "@/services/articlesService";
import { ApiError, ArticlesData } from "@/types/api";
import { Article } from "@/types/article";
import { formatDate } from "@/utils/utils";
import { useState, useEffect } from "react";

export const ArticleList = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError>();
    
  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const data: ArticlesData = await articlesService.getArticles();
        setArticles(data.articles || []);
      } catch (error) {
        setError(error as ApiError);
      } finally {
        setLoading(false);
      }
    };

      fetchArticles();
  }, []);

  const ArticleListItem = ({ article, index }: { article: Article , index:number}) => {
    const date = new Date(article.published_at).toISOString();
    return (
      <div className="grid grid-cols-[20%_80%] grid-rows-[auto_auto] gap-1">
        <div className="text-5xl">
          <h1 className="text-gray-600">{index<10 && '0'}{index}</h1>
        </div>
        <div className="pl-4 text-md">
          <a href={`/articles/${article.id}`} className="font-semibold hover:underline">
            {article.title}
          </a>
        </div>
        <div className=""><div className="divider w-full before:bg-gray-600 after:bg-gray-600"></div></div>
        <div className="flex flex-row gap-2 ml-4 text-sm">
          <p className="content-center text-gray-600">{formatDate(date)}</p>
          <p className="content-center text-gray-700">{article.author}</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mx-auto wrapper">
        <div className="text-center mx-auto">Loading...</div>
      </div>
    );
  }

  if (error) {
      return (
        <div className="mx-auto wrapper border-t-2">
          <div className="text-center h-full content-center">
            <p>Error: {error.statusCode} - {error.message}</p>
            <p><em>{error.detail}</em></p>
          </div>
        </div>
      );
    }

  return (
    <div className="container flex flex-col gap-4 p-2 h-60">
      <h1 className="border-b border-[var(--np-color-primary)] py-2 text-2xl font-bold mb-4">Other Top News</h1>
      {articles.map((article: Article, i:number) =>{ 
        return (
          <div key={i}>
            <ArticleListItem article={article} index={i+1}/>
          </div>
        )})
      }
    </div>
  );
}