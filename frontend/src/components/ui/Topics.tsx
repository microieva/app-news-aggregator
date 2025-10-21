import { useTopics } from '@/hooks/useTopics';
import { useEffect, useState } from 'react';
import { Topic } from '@/types/topic';

export const TopicsList = () => {
  const { getTopics, loading, error } = useTopics();
  const [topics, setTopics] = useState<Topic[]>([]);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const topicsData = await getTopics();
        setTopics(topicsData);
      } catch (err) {
        console.error('Failed to fetch topics:', err);
      }
    };

    fetchTopics();
  }, [getTopics]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {topics.map(topic => (
        <div key={topic.id}>{topic.name}</div>
      ))}
    </div>
  );
}