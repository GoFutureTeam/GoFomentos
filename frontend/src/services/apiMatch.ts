import TokenService from './tokenService';
import logger from '@/utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

/**
 * Interface para requisição de match
 */
export interface MatchProjectRequest {
  titulo_projeto: string;
  objetivo_principal: string;
  nome_empresa: string;
  resumo_atividades: string;
  cnae: string;
  user_id?: string; // Opcional - será preenchido automaticamente se usuário autenticado
}

/**
 * Resultado de match de um edital específico
 */
export interface EditalMatchResult {
  edital_uuid: string;
  edital_name: string;
  match_score: number; // 0-100
  match_percentage: number; // Valor numérico 0-100
  reasoning: string;
  compatibility_factors: string[]; // Array de fatores de compatibilidade
  edital_details?: {
    orgao_responsavel?: string;
    financiador_1?: string;
    link?: string;
    valor_min_R?: number;
    valor_max_R?: number;
    data_inicial_submissao?: string;
    data_final_submissao?: string;
    area_foco?: string;
    tipo_proponente?: string;
    [key: string]: string | number | undefined;
  };
  chunks_found: number;
}

/**
 * Resposta completa do match
 */
export interface MatchResponse {
  success: boolean;
  total_matches: number;
  keywords_used: string[];
  matches: EditalMatchResult[];
  execution_time_seconds: number;
}

/**
 * Health check do serviço de match
 */
export interface MatchHealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  chromadb: {
    status: string;
    total_chunks: number;
    total_editais: number;
  };
  openai: {
    status: string;
    model: string;
  };
  error?: string;
}

/**
 * Serviço de Match API
 * Integração com algoritmo de match inteligente (ChromaDB + GPT-4o)
 */
class ApiMatch {
  private getHeaders() {
    const token = TokenService.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  /**
   * Match projeto com editais usando ChromaDB + GPT-4o
   * 
   * Algoritmo em 6 etapas:
   * 1. GPT-4o gera 3 frases-chave do projeto
   * 2. Busca vetorial no ChromaDB (top 10 chunks por frase)
   * 3. Agrupa chunks por edital
   * 4. GPT-4o analisa compatibilidade de cada edital
   * 5. Gera score 0-100 + justificativa
   * 6. Retorna top 10 editais ranqueados
   * 
   * @param projectData Dados do projeto para match
   * @returns Promise com resultado do match
   */
  async matchProject(projectData: MatchProjectRequest): Promise<MatchResponse> {
    try {
      const url = `${API_BASE_URL}/api/v1/match/project`;
      
      logger.log('🎯 Iniciando match de projeto...', {
        projeto: projectData.titulo_projeto,
        empresa: projectData.nome_empresa
      });

      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(projectData),
      });

      // Verificar sessão expirada
      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      // Verificar erro na resposta
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `Erro HTTP ${response.status}`;
        logger.error('❌ Erro no match:', errorMessage);
        throw new Error(errorMessage);
      }

      const result: MatchResponse = await response.json();
      
      logger.log('✅ Match concluído com sucesso!', {
        total: result.total_matches,
        tempo: `${result.execution_time_seconds.toFixed(2)}s`,
        keywords: result.keywords_used.length
      });

      return result;

    } catch (error) {
      logger.error('❌ Erro ao processar match:', error);
      
      // Re-throw com mensagem mais amigável
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Erro ao processar match. Tente novamente.');
    }
  }

  /**
   * Health check do serviço de match
   * Verifica se ChromaDB e OpenAI estão funcionando
   * 
   * @returns Promise com status dos serviços
   */
  async healthCheck(): Promise<MatchHealthResponse> {
    try {
      const url = `${API_BASE_URL}/api/v1/match/health`;
      const response = await fetch(url);
      return await response.json();
    } catch (error) {
      logger.error('❌ Erro no health check:', error);
      return {
        status: 'unhealthy',
        service: 'match',
        chromadb: {
          status: 'error',
          total_chunks: 0,
          total_editais: 0
        },
        openai: {
          status: 'error',
          model: 'unknown'
        },
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }
}

export default new ApiMatch();
