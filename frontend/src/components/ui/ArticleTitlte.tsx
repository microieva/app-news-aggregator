import { Article } from "@/types/article"
import { formatDate } from "@/utils/utils";
import { Diamond } from "lucide-react";
import { useRouter } from "next/router";

export const ArticleTitle = ({ article }: { article: Article }) => {
  const router = useRouter();
  const route = router.pathname;
  const date = new Date(article.published_at).toISOString()
  return (
    <>
      <h2 className="font-semibold text-center">{article.title}</h2>
      <div className="flex flex-row justify-between mt-8">
        <div className="flex flex-row justify-start text-sm">
          <p 
            onClick={() => router.push(`/${route}`)}
            rel="noopener noreferrer"
            className="hover:underline font-helvetica cursor-pointer text-gray-600 border-r-2 pr-3 border-gray-400 mb-2"
          >
            {article.topic?.name} 
          </p>
          <p className=" text-gray-600 border-r-2 px-3 mb-2 border-gray-400">
            {article.author}
          </p>
          <p className="pl-3 text-gray-600">
            {formatDate(date)}
          </p>
        </div>
        <div className="hover:cursor-pointer hover:text-gray-600" onClick={()=> router.push(`/articles/${article.id}`)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="lucide lucide-redo-icon lucide-redo"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"/></svg>
        </div>
      </div>
    </>
  )
}