/**
 * Configuração central da API
 * Define URLs base, versão e todos os endpoints disponíveis
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';
const API_VERSION = '/api/v1'; // ✅ Backend usa /api/v1 para todas as rotas

/**
 * Endpoints da API organizados por recurso
 * ✅ CORRIGIDO: Alinhado com rotas reais do backend
 */
export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: `${API_VERSION}/users`,  // ✅ POST /api/v1/users
    LOGIN: `/login`,                    // ✅ POST /login (sem /api/v1)
    // ❌ Recuperação de senha não existe no backend ainda
    // REQUEST_PASSWORD_RESET: '/api/reset-password',
    // RESET_PASSWORD: '/api/reset-password/confirm',
  },

  USERS: {
    ME: `${API_VERSION}/users/me`,     // ✅ GET /api/v1/users/me
    DETAIL: (id: string) => `${API_VERSION}/users/${id}`,
  },

  EDITAIS: {
    LIST: `${API_VERSION}/editais`,
    CREATE: `${API_VERSION}/editais`,
    DETAIL: (uuid: string) => `${API_VERSION}/editais/${uuid}`,
    UPDATE: (uuid: string) => `${API_VERSION}/editais/${uuid}`,
    DELETE: (uuid: string) => `${API_VERSION}/editais/${uuid}`,
  },

  PROJECTS: {
    LIST: `${API_VERSION}/projects`,
    CREATE: `${API_VERSION}/projects`,
    ME: `${API_VERSION}/projects/me`,
    DETAIL: (id: string) => `${API_VERSION}/projects/${id}`,
    UPDATE: (id: string) => `${API_VERSION}/projects/${id}`,
    DELETE: (id: string) => `${API_VERSION}/projects/${id}`,
  },

  CHROMA: {
    SEARCH: `/api/chroma/search`,        // ✅ POST /api/chroma/search
    STATS: `/api/chroma/stats`,          // ✅ GET /api/chroma/stats
    DOCUMENTS: `/api/chroma/documents`,  // ✅ GET /api/chroma/documents
    EDITAIS: `/api/chroma/editais`,      // ✅ POST /api/chroma/editais
    CLEAR: `/api/chroma/clear`,          // ✅ DELETE /api/chroma/clear
  },

  JOBS: {
    LIST: `${API_VERSION}/jobs`,
    DETAIL: (id: string) => `${API_VERSION}/jobs/${id}`,
    EXECUTE_CNPQ: `${API_VERSION}/jobs/cnpq/execute`,
    EXECUTE_FAPESQ: `${API_VERSION}/jobs/fapesq/execute`,
  },

  MATCH: {
    PROJECT: `${API_VERSION}/match/project`,  // ✅ POST /api/v1/match/project
    HEALTH: `${API_VERSION}/match/health`,    // ✅ GET /api/v1/match/health
  },

  HEALTH: {
    CHECK: `/health`,  // ✅ GET /health (sem /api/v1)
  },

  ROOT: `/`,  // ✅ GET / (raiz)
};/**
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
