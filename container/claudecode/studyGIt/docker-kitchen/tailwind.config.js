/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'docker-blue': '#0db7ed',
        'kitchen-orange': '#FF9800',
        'kitchen-red': '#F44336',
        'kitchen-green': '#4CAF50',
      },
    },
  },
  plugins: [],
}