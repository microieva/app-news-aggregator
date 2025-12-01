import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  //output: 'export',
  devIndicators: false,
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  // React 19 and Turbopack configuration
    turbopack: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
  },
  // Enable React 19 features
  reactStrictMode: true,
  // Optional: Add basePath if deploying to subdirectory
  // basePath: '/news-aggregator',
}

export default nextConfig