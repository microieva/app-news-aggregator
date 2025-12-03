import { ReactNode} from 'react';
import { WeatherProvider } from '@/contexts/WeatherContext';
import { HeaderProvider } from '@/contexts/HeaderContext';
import { PageProvider } from '@/contexts/PageContext';
import { Header } from '@/components/ui/Header';
import { Footer } from '@/components/ui/Footer';
import { ArticlesProvider } from '@/contexts/ArticlesContext';
import '@/app/styles/globals.css';
import { HeadlinesProvider } from '@/contexts/HeadlinesContext';

interface RootLayoutProps {
  children: ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {

  return (
    <html lang="en" data-theme="light">
      <body>
        <WeatherProvider>
          <PageProvider>
            <HeaderProvider>
              <ArticlesProvider>
                <HeadlinesProvider>
                  <div className="app">
                    <Header />
                    <main>
                      {children}
                    </main>
                    <Footer />
                  </div>
                </HeadlinesProvider>
              </ArticlesProvider>
            </HeaderProvider>
          </PageProvider>
        </WeatherProvider>
      </body>
    </html>
  );
}