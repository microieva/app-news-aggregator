import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <button 
              onClick={() => router.push('/')}
              className="text-xl font-bold text-gray-800 hover:text-gray-600"
            >
              News Aggregator
            </button>
            <div className="flex space-x-4">
              <button 
                onClick={() => router.push('/')}
                className="text-gray-600 hover:text-gray-900"
              >
                Home
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main>
        <Component {...pageProps} />
      </main>
    </div>
  );
}