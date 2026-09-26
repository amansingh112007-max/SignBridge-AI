import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Simple Vite config for our student project
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // default Vite port
  },
})