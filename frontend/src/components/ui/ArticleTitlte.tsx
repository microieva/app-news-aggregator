'use client'; 

import { Article } from "@/types/article"
import { formatDate } from "@/utils/utils";
import { useParams, usePathname, useRouter } from "next/navigation";

export const ArticleTitle = ({ article }: { article: Article }) => {
  const router = useRouter();
  const date = article?.published_at || new Date().toISOString();
  const pathname = usePathname(); 
  const params = useParams(); 

  const route = pathname;
  const isArticleRoute = !!params.articleId;

  const ArticleInfo = () => {
    return (
    <div className="flex flex-row justify-start text-sm gap-2 h-min">
        <p 
          onClick={() => router.push(`/${route}`)}
          rel="noopener noreferrer"
          className="hover:underline cursor-pointer text-gray-600"
        >
          {article.topic?.name} 
        </p>
        <img src="/accent.png" className="h-[11px] m-auto"/>
        <p className=" text-gray-600">
          {article.author || '-'}
        </p>
        <img src="/accent.png" className="h-[11px] m-auto"/>
        <p className=" text-gray-600">
          {formatDate(date) || '-'}
        </p>
      </div>
    )
  }
  return (
    <>
    {article && <>
      <h1 className="font-semibold text-center">{article.title}</h1>
      <div className="flex flex-row justify-between mt-8">
        <ArticleInfo/>
        <a className="text-gray-600 hover:cursor-pointer" href={isArticleRoute ? article.url : `/articles/${article.id}`} >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-redo-icon lucide-redo"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"/></svg>
        </a>
      </div>
    </>}
    </>
  )
}