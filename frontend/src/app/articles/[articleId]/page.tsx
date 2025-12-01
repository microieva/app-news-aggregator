import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import ArticlePage from '@/components/pages/ArticlePage';
import ArticleLoading from './loading';

interface ArticlePageProps {
  params: {
    articleId: string;
  };
}

// This runs on the server for each request
export default async function ArticleRoute({ params }: ArticlePageProps) {
  const { articleId } = params;

  // Validate articleId - you can add more validation logic here
  if (!articleId || typeof articleId !== 'string') {
    notFound();
  }

  return (
    <Suspense fallback={<ArticleLoading />}>
      <ArticlePage id={articleId} />
    </Suspense>
  );
}

// Generate metadata for SEO (optional but recommended)
export async function generateMetadata({ params }: ArticlePageProps) {
  const { articleId } = params;
  
  // You can fetch article data here for metadata if needed
  // const article = await getArticleById(articleId);
  
  return {
    title: `Article - ${articleId}`,
    description: `Read the full article: ${articleId}`,
    // openGraph: {
    //   title: article?.title,
    //   description: article?.summary,
    //   images: [article?.image],
    // },
  };
}

// Optional: Generate static params for SSG
export async function generateStaticParams() {
  // If you want to pre-generate some popular articles
  // This replaces getStaticPaths
  try {
    // Example: Fetch recent article IDs for static generation
    // const articles = await getRecentArticles();
    // return articles.map((article) => ({
    //   articleId: article.id.toString(),
    // }));
    
    // For now, return empty array (same as your current fallback: true)
    return [];
  } catch (error) {
    console.error('Error generating static params:', error);
    return [];
  }
}

// Configure the page behavior
export const dynamic = 'force-dynamic'; // Equivalent to getStaticProps with fallback: true
// export const revalidate = 3600; // Optional: Revalidate every hour if using ISR