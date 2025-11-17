import { useEffect } from 'react';
import { Article } from '@/types/article';
import { ArticleList } from '../ui/ArticleList';
import { ArticleBlockSide } from '../ui/ArticleBlockSide';
import { ArticleBlockTop } from '../ui/ArticleBlockTop';
import { ArticleBlockBottom } from '../ui/ArticleBlockBottom';
import { usePage } from '@/contexts/PageContext';
import { useArticles } from '@/contexts/ArticlesContext';


export default function CategoryPage() {
  const { source, topic } = usePage();
  const {loading, error, articles, refreshArticles} = useArticles();

  useEffect(() => {
    refreshArticles({topic: topic || null, source:source});
  }, [topic]);

  useEffect(() => {
    refreshArticles({topic:topic || null, source});
  }, [source ]);


  const CategoryPageGrid = ({ articles }: { articles: Article[] }) => {
    const pageArticles = articles.slice(0, 6);

    return (
      <>
        <div className="grid-item-article-block-side" >
          {pageArticles[2] && <ArticleBlockSide article={pageArticles[2]}/>}
        </div>
        <div className="grid-item-article-list bg-article-list">
          <ArticleList /> 
        </div>
        <div className="grid-item-article-block-top">
          <ArticleBlockTop article={pageArticles.find(article => article.image_url !== article.url) || pageArticles[0]}/>
        </div>
  
        <div className="grid-item-article-block-bottom">
          {pageArticles[3] && <ArticleBlockBottom article={pageArticles[3]}/>}
        </div>
        <div className="grid-item-article-block">
          {pageArticles[1] && <ArticleBlockTop article={pageArticles[1]}/>}
        </div>
        <div className="grid-item-foreground-block row-start-9 ">
          something ? instead of weather
        </div>
      </>
    )
  }

  if (loading) {
    return (
      <div className="mx-auto wrapper">
        <div className="text-center mx-auto">Loading articles for {topic?.name}...</div>
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
    <div className=" mx-auto bg-[var(--np-background)] min-h-screen">
      <div className="grid-category-page min-h-[calc(100vh - 10rem)]">
        <CategoryPageGrid articles={articles}/>
      </div>
    </div>
  );
}