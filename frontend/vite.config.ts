import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      '/api': {
        target: 'https://api-editais.gofuture.cc',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      },
      '/webhook': {
        target: 'https://n8n.gofuture.unifacisa.edu.br',
        changeOrigin: true,
        secure: true,
      }
    }
  },
  preview: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'https://api-editais.gofuture.cc',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      },
      '/webhook': {
        target: 'https://n8n.gofuture.unifacisa.edu.br',
        changeOrigin: true,
        secure: true,
      }
    }
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
