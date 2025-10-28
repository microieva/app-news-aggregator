import topicsService from "@/services/topicsService";
import { ApiError } from "@/types/api";
import { Topic } from "@/types/topic";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function FrontPage(){
  const [error, setError] = useState<ApiError>();
  const [topics, setTopics] = useState<Topic[]>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
      const fetchArticles = async () => {
        try {
          setLoading(true);
          const data = await topicsService.getUsedTopics()
          setTopics(data.topics || []);
        } catch (error) {
          setError(error as ApiError)
        } finally {
          setLoading(false);
        }
      };

      fetchArticles();
    }, []);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading topics...</div>
      </div>
    );
  }

   if (error) return <div>
      <p>Error: {error.statusCode} - {error.message}</p>
      <p><em>{error.detail}</em></p>
    </div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">News Aggregator</h1>
      
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Browse Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {topics?.map((topic: Topic) => {
            const route = topic.name.replace(/ /g, '-');
            return (
              <Link
                key={topic.name}
                href={`/${route}`}
                className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-200"
              >
                <h3 className="text-xl font-semibold text-gray-800">{topic.name}</h3>
                <p className="text-gray-600 mt-2">View articles about {topic.name}</p>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}