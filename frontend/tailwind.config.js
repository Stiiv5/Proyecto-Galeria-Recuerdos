/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'pink-love': '#ff69b4',
        'soft-pink': '#fff5f7',
      }
    },
  },
  plugins: [],
}