import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  devIndicators: false,
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
    turbopack: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
  },
  reactStrictMode: true,
}

export default nextConfig