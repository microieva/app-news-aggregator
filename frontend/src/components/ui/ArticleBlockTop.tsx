'use client'; 

import { Article } from "@/types/article";
import { ArticleTitle } from "./ArticleTitlte";
import { ImageWrapper } from "../wrappers/ImageWrapper";
import { useParams } from "next/navigation";

export const ArticleBlockTop = ({ article }: { article: Article }) => {
  const params = useParams(); 
  const isArticleRoute = !!params.articleId;

  return (
    <>
      {article && 
        <div 
          className="relative rounded-tl-md shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full bg-[var(--np-background)] p-4"
        >
          <div className="grid grid-cols-1 grid-rows-1 bg-[var(--np-color-primary)]">
            <div className="rounded-tr-xl bg-[var(--np-background)] border border-[var(--np-color-primary)] p-4 row-start-1 col-start-1 z-10 text-4xl">
              <ArticleTitle article={article}/>
            </div>
          </div>
          {article.image_url && (
            <ImageWrapper url={article.image_url} title={article.title} classNames={["max-w-[55rem] mx-auto"]}/>
          )}
          <div className="p-4">
            <div className="flex flex-col gap-2">  
              {isArticleRoute ? <p className="text-gray-700 mb-4">
                {article.content}
              </p> :
              <p className="text-gray-700 mb-4">
                {article.summary?.content}
              </p>
              }
            </div>
          </div>
        </div>
      }
    </> 
  )
}