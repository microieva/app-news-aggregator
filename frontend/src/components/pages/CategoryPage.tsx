import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { ArticlesData } from '@/types/api';
import articlesService from '@/services/articlesService';
import { Article } from '@/types/article';
import { ArticleList } from '../ui/ArticleList';
import { ArticleBlockSide } from '../ui/ArticleBlockSide';
import { ArticleBlockTop } from '../ui/ArticleBlockTop';
import { ArticleBlockBottom } from '../ui/ArticleBlockBottom';

interface CategoryPageProps {
  category: string;
}

export default function CategoryPage({ category }: CategoryPageProps) {
  const router = useRouter();
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const route = category.replace(/ /g, '-');
        const data: ArticlesData = await articlesService.getArticlesByTopicName(route)
        setArticles(data.articles || []);
      } catch (error) {
        console.error('Error fetching articles:', error);
      } finally {
        setLoading(false);
      }
    };

    if (category) {
      fetchArticles();
    }
  }, [category]);

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
        <div className="text-center mx-auto">Loading articles for {category}...</div>
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
            <p className="text-gray-500">No articles found for {category}</p>
          </div>
        )}
      </div>
    </div>
  );
}