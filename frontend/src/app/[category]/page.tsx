import { Suspense } from "react";
import { CategoryPageClient } from "@/components/pages/CategoryPage";
import { LoadingPage } from "@/components/pages/LoadingPage";
import { topicsService } from "@/services/topicsService";


interface CategoryPageProps {
  params: Promise<{ category: string }>;
}

export default async function CategoryPage({ params }: CategoryPageProps) {
  const [categoryParams] = await Promise.all([params]);
  const category = categoryParams.category.replace(/-/g, ' ');
  
  return (
     <Suspense fallback={<LoadingPage />}>
      <CategoryPageClient category={category} />
    </Suspense>
  )
}

export async function generateStaticParams() {
  try {
    const data = await topicsService.getUsedTopics();
    return data.topics.map((topic) => ({
      category: topic.name.toLowerCase().replace(/ /g, '-'),
    }));
  } catch (error) {
    console.error('Error generating static params for categories:', error);
    
    const fallbackCategories = [
      'technology',
      'politics', 
      'business',
      'entertainment',
      'science'
    ];
    
    return fallbackCategories.map((category) => ({
      category: category,
    }));
  }
}

// SEO
export async function generateMetadata({ params }: CategoryPageProps) {
  const { category } = await params;
  const categoryName = category.replace(/-/g, ' ');
  
  return {
    title: `${categoryName.charAt(0).toUpperCase() + categoryName.slice(1)} News`,
    description: `Latest news and articles about ${categoryName}`,
  };
}