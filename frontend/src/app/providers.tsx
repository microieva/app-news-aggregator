'use client';

import { ReactNode } from 'react';
import { WeatherProvider } from '@/contexts/WeatherContext';
import { PageProvider } from '@/contexts/PageContext';
import { HeaderProvider } from '@/contexts/HeaderContext';
import { ArticlesProvider } from '@/contexts/ArticlesContext';
import { HeadlinesProvider } from '@/contexts/HeadlinesContext';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <WeatherProvider>
      <PageProvider>
        <HeaderProvider>
          <ArticlesProvider>
            <HeadlinesProvider>
              {children}
            </HeadlinesProvider>
          </ArticlesProvider>
        </HeaderProvider>
      </PageProvider>
    </WeatherProvider>
  );
}