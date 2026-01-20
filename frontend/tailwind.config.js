/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'jira-blue': '#0052CC',
        'jira-blue-dark': '#0065FF',
        'jira-gray': '#42526E',
        'jira-gray-light': '#F4F5F7',
        'jira-border': '#DFE1E6',
      },
    },
  },
  plugins: [],
}

