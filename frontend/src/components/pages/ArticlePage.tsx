import { articlesService } from "@/services/articlesService";
import { Article } from "@/types/article";
import { ArticlePageProps } from "@/types/pages";
import { Link } from "lucide-react";
import { useRouter } from "next/router";
import { useState, useEffect } from "react";
import { ArticleBlockTop } from "../ui/ArticleBlockTop";
import { ArticleList } from "../ui/ArticleList";

 export const ArticlePageGrid = ({article}: { article:Article}) => {

    return (
      <>
        <div className="grid-item-article-page-block">
          <ArticleBlockTop article={article}/>
        </div>
        <div className="grid-item-article-list bg-article-list">
          <ArticleList/>
        </div>
        <div className="col-span-2 row-span-1 col-start-9 row-start-5 bg-[var(--np-foreground)] border-t">
          something
          <p>more content</p>
          <p>more content</p>
          <p>more content</p>
          <p>more content</p>
          <p>more content</p>
        </div>
      </>
    )
  }

export default function ArticlePage({ id }: ArticlePageProps) {
  const router = useRouter();

  const [articleData, setArticleData] = useState<Article>();
  const [loading, setLoading] = useState(!id);

  useEffect(() => {
      const fetchArticle = async () => {
        try {
          setLoading(true);
          const article:Article = await articlesService.getArticleById(id);
          setArticleData(article);
        } catch (error) {
          console.error('Error fetching article:', error);
        } finally {
          setLoading(false);
        }
      };
      if (id) fetchArticle();
  }, [id]);

 

  if (router.isFallback || loading) {
    return (
      <div className="mx-auto wrapper">
        <div className="text-center">Loading article...</div>
      </div>
    );
  }

  if (!articleData) {
    return (
      <div className=" mx-auto wrapper">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Article Not Found</h1>
          <Link href="/" className="hover:underline">
            ← Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="grid-article-page">
      <ArticlePageGrid article={articleData}/>
    </div>
  );
}