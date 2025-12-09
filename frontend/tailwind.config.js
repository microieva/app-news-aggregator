/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    screens: {
      'xs': '320px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },
    extend: {
      colors: {
        bg: 'var(--np-bg-background)',
        primary: 'var(--np-color-primary)',
        secondary: 'var(--np-color-secondary)',
        tertiary: 'var(--np-color-tertiary)',
        accent: 'var(--np-color-accent)',
        background: 'var(--np-background)',
        foreground: 'var(--np-foreground)'
      },

      fontFamily: {
        primary: ['var(--np-font-primary)', 'serif'],
        secondary: ['var(--np-font-secondary)', 'sans-serif']
      },
      fontSize: {
        'sm': 'var(--np-text-sm)',
        'md': 'var(--np-text-md)',
        'xm': 'var(--np-text-xm)',
        'lg': 'var(--np-text-lg)',
        'xl': 'var(--np-text-xl)',
        '2xl': 'var(--np-text-2xl)',
      }
    },
  },
  plugins: [
    require('daisyui')
  ],

  daisyui: {
    themes: ["light", "dark"],
    darkTheme: "dark", 
    base: true, 
    styled: true, 
    utils: true, 
    prefix: "", 
    logs: true,
    themeRoot: ":root", 
  },
}