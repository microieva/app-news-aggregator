import { useRouter } from 'next/router';
import { topicsService } from '@/services/topicsService';
import { TopicsData } from '@/types/api';
import { Topic } from '@/types';
import { memo, useEffect } from 'react';
import CategoryPage from '@/components/pages/CategoryPage';

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
      // 'technology',
      // 'business',
      // 'science',
      // 'health',
      // 'environment'
      "fallback"
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

// const CategoryRoute = memo(function CategoryRoute({ category }: { category: string }) {
//   const router = useRouter();
  
//   if (router.isFallback) {
//     return (
//       <div className="container mx-auto px-4 py-8">
//         <div className="text-center">Loading category...</div>
//       </div>
//     );
//   }

//   return <CategoryPage category={category} />;
// });

// Remove memo - it's not helping and might be confusing the issue
function CategoryRoute({ category }: { category: string }) {
  const router = useRouter();
     console.log(' CategoryPage MOUNTED', category);
    useEffect(() => {
    return () => {
      console.log('💥 CategoryPage UNMOUNTED', category);
    };
  }, [category]);
  
  if (router.isFallback) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading category...</div>
      </div>
    );
  }

  return <CategoryPage category={category} />;
}

export default CategoryRoute;



// CategoryRoute.displayName = 'CategoryRoute';

// export default CategoryRoute;