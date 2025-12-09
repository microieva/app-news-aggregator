import { Article } from "@/types/article"
import { ArticleTitle } from "./ArticleTitlte";

export const ArticleBlockSide = ({ article }: { article: Article }) => {
  
  return (
    <div 
      className="relative rounded-tl-md rounded-bl-md shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full bg-background p-4"
    >
      <div className="grid grid-cols-1 grid-rows-1 bg-background border-b border-[var(--np-color-primary)] pb-2 text-md">
        <ArticleTitle article={article}/>
      </div>
      {article?.image_url && (
        <div className="bg-background">
          <img 
            src={article.image_url} 
            alt={article.title} 
            className="w-full h-50 object-center mt-4 opacity-70"
          />
        </div>
      )}
      {article?.summary && <div className="p-4">
        <div className="flex flex-col gap-2">
          
          <p className="text-gray-700 mb-4">
            {article.summary?.content}
          </p>

        </div>
      </div>}
    </div>
  )
}