import { ReactNode} from 'react';
import { Providers } from './providers';
import { Header } from '@/components/ui/Header';
import { Footer } from '@/components/ui/Footer';
import '@/app/styles/globals.css';

interface RootLayoutProps {
  children: ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {

   return (
    <html lang="en" data-theme="light" className='bg-[var(--np-body-background)]'>
      <body>
        <Providers>
          <div className="app">
            <Header />
            <main>
              {children}
            </main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}