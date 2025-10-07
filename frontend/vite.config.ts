import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    // PROXY DESABILITADO - Usando backend local (Docker) na porta 8002
    // O proxy estava interceptando as chamadas /api e redirecionando para servidor externo
    // Para usar API externa novamente, descomente o bloco abaixo
    /*
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
    */
  },
  preview: {
    port: 8080,
    // PROXY DESABILITADO - Usando backend local
    /*
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
    */
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
