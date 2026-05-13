/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        warm: {
          100: '#e8e6e1',
          200: '#d4d2cd',
          400: '#9b9894',
          600: '#6b6765',
        },
        gold: {
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        },
        emerald: {
          // Tailwind has emerald built-in; these aliases keep it explicit
          400: '#34d399',
          500: '#10b981',
        },
      },
    },
  },
  plugins: [],
}
