import { useEffect, useState } from 'react';
import { ArticlesData } from '@/types/api';
import articlesService from '@/services/articlesService';
import { Article } from '@/types/article';
import { ArticleList } from '../ui/ArticleList';
import { ArticleBlockSide } from '../ui/ArticleBlockSide';
import { ArticleBlockTop } from '../ui/ArticleBlockTop';
import { ArticleBlockBottom } from '../ui/ArticleBlockBottom';
import { usePage } from '@/contexts/PageContext';


export default function CategoryPage() {
  const { source, topic, setSource, setTopic, setHomePage, clearFilters, hasActiveFilters } = usePage();

  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const config = {topic: topic!.name, source:source || undefined}
        const data: ArticlesData = await articlesService.getArticlesByTopicName(config)
        setArticles(data.articles || []);
      } catch (error) {
        console.error('Error fetching articles:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, [topic]);

  const CategoryPageGrid = ({ articles }: { articles: Article[] }) => {
    const pageArticles = articles.slice(0, 6);

    return (
      <>
        <div className="grid-item-article-block-side" >
          <ArticleBlockSide article={pageArticles[2]}/>
        </div>
        <div className="grid-item-article-list bg-article-list">
          <ArticleList /> 
        </div>
        <div className="grid-item-article-block-top">
          <ArticleBlockTop article={pageArticles.find(article => article.image_url !== article.url) || pageArticles[0]}/>
        </div>
  
        <div className="grid-item-article-block-bottom">
          <ArticleBlockBottom article={pageArticles[3]}/>
        </div>
        <div className="grid-item-article-block">
          <ArticleBlockTop article={pageArticles[1]}/>
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

  return (
    <div className=" mx-auto bg-[var(--np-background)] min-h-screen">
      <div className="grid-category-page">
        {articles.length > 0 ? 
          <CategoryPageGrid articles={articles}/>
         : (
          <div className="text-center py-8">
            <p className="text-gray-500">No articles found for {topic?.name}</p>
          </div>
        )}
      </div>
    </div>
  );
}