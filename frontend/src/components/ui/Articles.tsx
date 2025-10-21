import { useArticles } from '@/hooks/useArticles';
import { useEffect, useState } from 'react';
//import { Articles } from '@/types/article';

export const ArticlesList = () => {
  const { getArticles, loading, error } = useArticles();
  const [articles, setArticles] = useState<any[]>([]);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const articlesData = await getArticles();
        setArticles(articlesData);
      } catch (err) {
        console.error('Failed to fetch Articles:', err);
      }
    };

    fetchArticles();
  }, [getArticles]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {articles.map(article => (
        <div key={article.id}>{article.name}</div>
      ))}
    </div>
  );
}