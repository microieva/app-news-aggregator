import type { AppProps } from 'next/app';
import { PageProvider } from '@/contexts/PageContext';
import { HeaderProvider } from '@/contexts/HeaderContext';

import { Footer } from '@/components/ui/Footer';
import { Header } from '@/components/ui/Header';
import { Topic } from '@/types/topic';
import { SourcesData, TopicsData } from '@/types/api';
import '../styles/globals.css'

interface MyAppProps extends AppProps {
  initialSources: string[];
  initialTopics: Topic[];
}

function App({ Component, pageProps, initialSources, initialTopics }: MyAppProps) {
  return (
    <HeaderProvider initialSources={initialSources} initialTopics={initialTopics}>
      <PageProvider>
        <div className="min-h-screen bg-[var(--np-background)]'">
          <Header/>
          <main className='bg-[var(--np-background)]'>
            <Component {...pageProps} />
          </main>
          <Footer/>
        </div>
      </PageProvider>
    </HeaderProvider>
  );
}

App.getInitialProps = async (appContext: any) => {
  const [sources, topics] = await Promise.all([
    import('@/services/articlesService').then(module =>
      module.articlesService.getUsedSources().catch(() => ([]))
    ),
    import('@/services/topicsService').then(module =>
      module.topicsService.getUsedTopics().catch(() => ({ topics: [] }))
    ),
  ]);

  let pageProps = {};
  if (appContext.Component.getInitialProps) {
    pageProps = await appContext.Component.getInitialProps(appContext.ctx);
  }

  const initialSources: string[] = sources as string[];
  const initialTopics: Topic[] = topics.topics;

  return {
    ...pageProps,
    initialSources,
    initialTopics,
  };
};
export default App;
