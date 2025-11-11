import type { AppProps } from 'next/app';
import { HeaderProvider } from '@/contexts/HeaderContext';
import { ArticlesProvider } from '@/contexts/ArticlesContext';
import { PageProvider } from '@/contexts/PageContext';
import { Footer } from '@/components/ui/Footer';
import { Header } from '@/components/ui/Header';
import { Topic } from '@/types/topic';
import { Article } from '@/types/article';
import '../styles/globals.css'
import { WeatherProvider } from '@/contexts/WeatherContext';

interface MyAppProps extends AppProps {
  initialSources: string[];
  initialTopics: Topic[];
  initialArticles: Article[];
}

function App({ Component, pageProps, initialSources, initialTopics, initialArticles }: MyAppProps) {
  return (
    <WeatherProvider>
      <HeaderProvider initialSources={initialSources} initialTopics={initialTopics}>
        <PageProvider>
          <ArticlesProvider initialArticles={initialArticles}>
            <div className="min-h-screen bg-[var(--np-background)]'">
              <Header/>
              <main className='bg-[var(--np-background)]'>
                <Component {...pageProps} />
              </main>
              <Footer/>
            </div>
          </ArticlesProvider>
        </PageProvider>
      </HeaderProvider>
    </WeatherProvider>
  );
}

App.getInitialProps = async (appContext: any) => {
  const [sources, topics, articles] = await Promise.all([
    import('@/services/articlesService').then(module =>
      module.articlesService.getUsedSources().catch(() => ([]))
    ),
    import('@/services/topicsService').then(module =>
      module.topicsService.getUsedTopics().catch(() => ({ topics: [] }))
    ),
    import('@/services/articlesService').then(module => 
      module.articlesService.getFrontPageArticles().catch(() => ({articles:[]}))
    )
  ]);

  let pageProps = {};
  if (appContext.Component.getInitialProps) {
    pageProps = await appContext.Component.getInitialProps(appContext.ctx);
  }

  const initialSources: string[] = sources as string[];
  const initialTopics: Topic[] = topics.topics;
  const initialArticles: Article[] = articles.articles;

  return {
    ...pageProps,
    initialSources,
    initialTopics,
    initialArticles
  };
};
export default App;
