import type { AppProps } from 'next/app';
import { Header } from '@/components/ui/Header';
import { Footer } from '@/components/ui/Footer';
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {

  return (
    <div className="min-h-screen bg-[var(--np-background)]'">
      <Header/>
      <main className='bg-[var(--np-background)]'>
        <Component {...pageProps} />
      </main>
      <Footer/>
    </div>
  );
}