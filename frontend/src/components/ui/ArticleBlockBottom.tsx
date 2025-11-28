import { Article } from "@/types/article";
import { ArticleTitle } from "./ArticleTitlte";

export const ArticleBlockBottom = ({ article }: { article: Article }) => {

  return (
    <>
      {article && 
        <div 
          key={article.id }
          className="relative rounded-tl-md shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full bg-[var(--np-background)] p-4"
        >
          <div className="grid grid-cols-1 grid-rows-1 bg-[var(--np-background)] border-b border-[var(--np-color-primary)] pb-2 mb-4 text-2xl">
            <ArticleTitle article={article}/>
          </div>
          <div className="flex flex-row gap-8">
            {article.image_url && (
              <div className="bg-[var(--np-background)] flex-1">
                <img 
                  src={article.image_url} 
                  alt={article.title} 
                  className="w-full h-50 object-center opacity-70"
                />
              </div>
            )}    
            <p className="text-gray-700 flex-1">
              {article.summary?.content}
            </p>
          </div>
        </div>
      }
    </>
    
  )
}