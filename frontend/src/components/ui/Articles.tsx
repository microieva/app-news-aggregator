"use client"

import { useArticles } from '@/hooks/useArticles';
import { useEffect, useState } from 'react';
import { ApiError, ArticlesData } from '@/types/api';

export const Articles = () => {
  const { getArticles, loading, error } = useArticles();
  const [articles, setArticles] = useState<any>([]);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const articlesData: ArticlesData = await getArticles();
        setArticles(articlesData.articles);
      } catch (err) {
        console.error('Failed to fetch Articles:', (err as ApiError).message);
      }
    };

    fetchArticles();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>
      <p>Error: {error.statusCode} - {error.message}</p>
      <p><em>{error.detail}</em></p>
    </div>;

  return (
    <div>
      {articles && articles.map((article:any) => (
        <li key={article.id} className='text-start'>{article.title}</li>
      ))}
    </div>
  );
}