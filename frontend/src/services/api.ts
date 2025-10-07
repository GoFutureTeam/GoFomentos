/**
 * Configuração central da API
 * Define URLs base, versão e todos os endpoints disponíveis
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';
const API_VERSION = '/api/v1'; // ✅ Backend usa /api/v1 para todas as rotas

/**
 * Endpoints da API organizados por recurso
 * IMPORTANTE: Backend usa /api/v1/* para todas as rotas
 */
export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: `${API_VERSION}/auth/register`,
    LOGIN: `${API_VERSION}/auth/login`,
    // ❌ Recuperação de senha não existe no backend ainda
    // REQUEST_PASSWORD_RESET: '/api/reset-password',
    // RESET_PASSWORD: '/api/reset-password/confirm',
  },
  
  EDITAIS: {
    LIST: `${API_VERSION}/editais`,
    CREATE: `${API_VERSION}/editais`,
    DETAIL: (id: string | number) => `${API_VERSION}/editais/${id}`,
    UPDATE: (id: string | number) => `${API_VERSION}/editais/${id}`,
    DELETE: (id: string | number) => `${API_VERSION}/editais/${id}`,
  },
  
  PROJECTS: {
    LIST: `${API_VERSION}/projects`,
    CREATE: `${API_VERSION}/projects`,
    DETAIL: (id: string | number) => `${API_VERSION}/projects/${id}`,
    UPDATE: (id: string | number) => `${API_VERSION}/projects/${id}`,
    DELETE: (id: string | number) => `${API_VERSION}/projects/${id}`,
  },
  
  HEALTH: {
    CHECK: `${API_VERSION}/health`,
  },
};

/**
 * Retorna a URL base da API
 */
export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

/**
 * Retorna a versão da API
 */
export function getApiVersion(): string {
  return API_VERSION;
}

/**
 * Constrói URL completa para um endpoint
 */
export function buildApiUrl(endpoint: string): string {
  return `${API_BASE_URL}${endpoint}`;
}

/**
 * Configuração padrão de timeout para requisições (em ms)
 */
export const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 30000;

/**
 * Headers padrão para requisições
 */
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

/**
 * Exporta a URL base para compatibilidade com código existente
 */
export { API_BASE_URL };
export default API_BASE_URL;
