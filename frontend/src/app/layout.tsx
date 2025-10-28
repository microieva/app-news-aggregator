import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'

const geistSans = Geist({
  subsets: ['latin'],
  display: 'swap',
})

const geistMono = Geist_Mono({
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'News Aggregator',
    template: '%s | News Aggregator'
  },
  description: 'A modern news aggregator and summarizer application built with Next.js 15',
  keywords: ['news', 'aggregator', 'summarizer', 'articles'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${geistSans.className} ${geistMono.className}`}>
      <body className="antialiased bg-background text-foreground">
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  )
}