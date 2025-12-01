import { ReactNode} from 'react';
import { WeatherProvider } from '@/contexts/WeatherContext';
import { HeaderProvider } from '@/contexts/HeaderContext';
import { PageProvider } from '@/contexts/PageContext';
import { Header } from '@/components/ui/Header';
import { Footer } from '@/components/ui/Footer';
import { ArticlesProvider } from '@/contexts/ArticlesContext';
import '@/app/styles/globals.css';

interface RootLayoutProps {
  children: ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {

  return (
    <html lang="en" data-theme="light">
      <body>
        <WeatherProvider>
          <HeaderProvider >
            <PageProvider>
              <ArticlesProvider>
                <div className="app">
                  <Header />
                  <main>
                    {children}
                  </main>
                  <Footer />
                </div>
              </ArticlesProvider>
            </PageProvider>
          </HeaderProvider>
        </WeatherProvider>
      </body>
    </html>
  );
}