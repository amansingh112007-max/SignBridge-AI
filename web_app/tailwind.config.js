/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
      },
      colors: {
        ink: '#05070d',
        panel: '#0b101c',
        accent: '#34d399',
      },
      animation: {
        'pulse-soft': 'pulseSoft 2.4s ease-in-out infinite',
      },
      keyframes: {
        pulseSoft: { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.45 } },
      },
    },
  },
  plugins: [],
}