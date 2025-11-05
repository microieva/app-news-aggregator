import { useRouter } from 'next/router';
import ArticlePage from '@/components/pages/ArticlePage';

export async function getStaticPaths() {
  try {

    return {
      paths: [], 
      fallback: true, 
    };
  } catch (error) {
    console.error('Error generating static paths:', error);
    return {
      paths: [],
      fallback: true,
    };
  }
}

export async function getStaticProps({ params }: { params: { id: string } }) {
  return {
    props: {
      id: params.id,
    },
    revalidate: 3600, 
  };
}

interface ArticleRouteProps {
  id: any;
}

export default function ArticleRoute({ id }: ArticleRouteProps) {
  const router = useRouter();

  if (router.isFallback) {
    return (
      <div className="mx-auto px-4 py-8">
        <div className="text-center">Loading article...</div>
      </div>
    );
  }

  return <ArticlePage id={id} />
}