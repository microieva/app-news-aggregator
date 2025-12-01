import { Suspense } from 'react';
import FrontPage from '@/components/pages/FrontPage';
import { LoadingPage } from '@/components/pages/LoadingPage';

export default async function HomePage() {
  
  return (
    <Suspense 
      fallback={<LoadingPage />}
    >
      <FrontPage />
    </Suspense>
  );
}

// SEO
export const metadata = {
  title: 'News Aggregator - Latest Headlines',
  description: 'Your personalized news aggregator and summarizer',
};