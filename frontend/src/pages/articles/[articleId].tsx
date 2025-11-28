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

export async function getStaticProps({ params }: { params: { articleId: string } }) {
  return {
    props: {
      id: params.articleId,
    }
  };
}

interface ArticleRouteProps {
  id: any;
}

export default function ArticleRoute({ id }: ArticleRouteProps) {
  const router = useRouter();

  if (router.isFallback) {
    return (
      <div className="wrapper content-center">
        <div className="text-center text-[var(--np-foreground)]">
          <p>Loading article...</p>
        </div>
      </div>
    );
  }

  return <ArticlePage id={id} />
}