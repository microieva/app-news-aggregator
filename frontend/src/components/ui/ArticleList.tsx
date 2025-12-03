import { formatDate } from "@/utils/utils";
import { Article } from "@/types/article";
import { useHeadlines } from "@/contexts/HeadlinesContext";
import { useEffect, useState } from "react";

export const ArticleList = ({title, articles}: {title:string, articles?:Article[]}) => {
  const {data, loading, error} = useHeadlines();
  const [headlines, setHeadlines] = useState<Partial<Article>[]>([]);
  
  useEffect(() => {
    if (articles) {
      setHeadlines(articles);
    } else if (data && data.headlines) {
      setHeadlines(data.headlines);
    }
  }, [data, articles]);

  const ArticleListItem = ({ article, index }: { article: Partial<Article> , index:number}) => {
    const date = new Date(article.published_at!).toISOString();

    return (
      <div className="grid grid-cols-[20%_80%] grid-rows-[auto_auto] gap-1">
        <div className="text-5xl">
          <h1 className="text-gray-600 italic font-secondary">{index<10 && '0'}{index}</h1>
        </div>
        <div className="pl-4 text-md">
          <a href={`/articles/${article.id}`} className="font-semibold hover:underline">
            {article.title}
          </a>
        </div>
        <div className=""><div className="divider w-full before:bg-gray-600 after:bg-gray-600"></div></div>
        <div className="flex flex-row gap-2 ml-4">
          <p className="content-center text-gray-600 text-xs">{formatDate(date, false)}</p>
          <p className="content-center text-[var(--np-color-accent)] font-bold">|</p>
          <p className="content-center text-gray-700 text-xs">{article.author}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container flex flex-col gap-4 p-2 max-h-[40rem] min-h-[30rem]">
      {headlines.length>0 ? 
      <>
        <h1 className="border-b border-[var(--np-color-primary)] py-2 text-2xl font-bold mb-4">{title}</h1>
        {headlines.map((article: Partial<Article>, i:number) =>{ 
          return (
            <div key={i}>
              <ArticleListItem article={article} index={i+1}/>
            </div>
          )})
        }
      </>:<></>}
    </div>
  );
}