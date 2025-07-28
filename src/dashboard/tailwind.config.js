/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#2c5282',      // Głęboki niebieski
        'secondary': '#4fd1c5',   // Turkus
        'accent': '#f6ad55',       // Pomarańcz
        'background': '#f7fafc', // Jasnoszary
        'surface': '#ffffff',      // Biały
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
