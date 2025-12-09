import { formatDate } from "@/utils/utils";
import { Article } from "@/types/article";
import { useHeadlines } from "@/contexts/HeadlinesContext";
import { useEffect, useState } from "react";
import Link from "next/link";

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
      <div className="grid grid-cols-[20%_80%] grid-rows-[auto_auto] gap-y-0">
        <p style={{lineHeight:'initial'}} className="text-secondary italic font-secondary text-lg">{index<10 && '0'}{index}</p>
        <div className="pl-4 text-sm" style={{lineHeight:'initial'}}>
          <Link href={`/articles/${article.id}`} className="font-semibold hover:underline ">
            {article.title}
          </Link>
        </div>
        <div className="divider w-full before:bg-secondary after:bg-secondary h-0"></div>
        <div className="flex flex-row gap-2 ml-4">
          <p className="content-center text-secondary text-xs">{formatDate(date, false)}</p>
          <p className="content-center text-accent font-bold">|</p>
          <p className="content-center text-gray-700 text-xs">{article.author}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-2 bg-background">
      {headlines.length>0 ? 
      <>
        <p className="border-b border-primary py-2 font-bold text-md mb-4">{title}</p>
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