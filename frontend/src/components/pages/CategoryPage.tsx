import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { ArticlesData } from '@/types/api';
import articlesService from '@/services/articlesService';

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

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading articles for {category}...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <button 
          onClick={() => router.back()}
          className="mb-4 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
        >
          ← Back
        </button>
        <h1 className="text-3xl font-bold">Category: {category}</h1>
        <p className="text-gray-600 mt-2">
          Browse the latest news and summaries about {category}
        </p>
      </div>

      <div className="grid gap-6">
        {articles.length > 0 ? (
          articles.map((article: any) => (
            <div key={article.title} className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <h2 className="text-xl font-semibold mb-2">{article.title}</h2>
              <p className="text-gray-700 mb-3">{article.summary.content}</p>
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>{article.source} | {(article.topic.name)}</span>
                <span>{new Date(article.published_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No articles found for {category}</p>
          </div>
        )}
      </div>
    </div>
  );
}