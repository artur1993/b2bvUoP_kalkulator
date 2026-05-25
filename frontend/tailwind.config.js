/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb',
          dark: '#3b82f6',
        },
        secondary: {
          DEFAULT: '#64748b',
          dark: '#94a3b8',
        },
        surface: {
          DEFAULT: '#ffffff',
          dark: '#1e293b',
        },
        background: {
          DEFAULT: '#f8fafc',
          dark: '#0f172a',
        },
        accent: {
          DEFAULT: '#10b981',
          dark: '#34d399',
        }
      },
    },
  },
  plugins: [],
}
