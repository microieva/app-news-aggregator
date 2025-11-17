import { useRouter } from 'next/router';
import CategoryPage from '@/components/pages/CategoryPage';
import { topicsService } from '@/services/topicsService';
import { TopicsData } from '@/types/api';

interface Topic {
  id: string;
  name: string;
}

export async function getStaticPaths() {
  try {
    const data: TopicsData = await topicsService.getUsedTopics();
    
    const paths = data.topics.map((topic: Topic) => ({
      params: { 
        category: topic.name.toLowerCase().replace(/ /g, '-')
      },
    }));

    return {
      paths,
      fallback: true, // Generate pages on-demand for new categories
    };
  } catch (error) {
    console.error('Error generating static paths:', error);
    
    const fallbackPaths = [
      'technology',
      'business',
      'science',
      'health',
      'environment'
    ].map(category => ({ params: { category } }));

    return {
      paths: fallbackPaths,
      fallback: true,
    };
  }
}

export async function getStaticProps({ params }: { params: { category: string } }) {
  try {
    const categoryName = params.category.replace(/-/g, ' ');
    
    return {
      props: {
        category: categoryName,
      }
    };
  } catch (error) {
    return {
      props: {
        category: params.category.replace(/-/g, ' '),
      }
    };
  }
}

export default function CategoryRoute() {
  const router = useRouter();

  if (router.isFallback) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading category...</div>
      </div>
    );
  }

  return <CategoryPage />;
}