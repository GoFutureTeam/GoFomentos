import { API_ENDPOINTS } from './api';
import TokenService from './tokenService';

// Interface atualizada para corresponder ao backend
export interface DadosProjeto {
  id?: string;
  
  // Dados do Projeto
  titulo_projeto: string;
  objetivo_principal: string;
  
  // Dados da Empresa
  nome_empresa: string;
  resumo_atividades: string;
  cnae: string;
  
  // Documento opcional (backend tem, mas não vamos usar na v1)
  documento_url?: string;
  
  // Relacionamentos
  user_id?: string;
  edital_uuid?: string;
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}

// Interface para resposta da API
interface RespostaApi<T> {
  dados: T;
  sucesso: boolean;
  mensagem: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

/**
 * Classe de serviço para gerenciar projetos na API
 * ✅ CORRIGIDO: Usando API_ENDPOINTS centralizados
 */
class ServicoApiProjeto {
  /**
   * ✅ CORRIGIDO: Usar TokenService em vez de localStorage direto
   */
  private getHeaders() {
    const token = TokenService.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }
  
  
  /**
   * Busca MEUS projetos (do usuário autenticado)
   * ✅ CORRIGIDO: Usar /api/v1/projects/me em vez de /api/v1/projects
   */
  async listarProjetos(): Promise<RespostaApi<DadosProjeto[]>> {
    try {
      // ✅ CORRETO: /api/v1/projects/me (único endpoint GET disponível)
      const url = `${API_BASE_URL}${API_ENDPOINTS.PROJECTS.ME}`;
      console.log('🔗 Buscando MEUS projetos em:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao listar projetos');
      }

      const dados = await response.json();
      console.log('✅ Meus projetos carregados:', dados.length || 0);

      return {
        dados,
        sucesso: true,
        mensagem: 'Projetos carregados com sucesso'
      };
    } catch (erro) {
      console.error('❌ Erro ao listar projetos:', erro);
      return {
        dados: [],
        sucesso: false,
        mensagem: `Erro ao carregar projetos: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  /**
   * Busca um projeto específico pelo ID
   * ✅ CORRIGIDO: URL de /api/projects/{id} → /api/v1/projects/{id}
   */
  async obterProjeto(id: string): Promise<RespostaApi<DadosProjeto>> {
    try {
      const url = `${API_BASE_URL}${API_ENDPOINTS.PROJECTS.DETAIL(id)}`;  // ✅ /api/v1/projects/{id}
      console.log('🔗 Buscando projeto em:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao buscar projeto');
      }

      const dados = await response.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: 'Projeto encontrado com sucesso'
      };
    } catch (erro) {
      console.error(`❌ Erro ao buscar projeto ${id}:`, erro);
      return {
        dados: {} as DadosProjeto,
        sucesso: false,
        mensagem: `Erro ao buscar projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
  
  /**
   * Salva um projeto (cria novo ou atualiza existente)
   * ✅ CORRIGIDO: URLs de /api/projects → /api/v1/projects
   */
  async salvarProjeto(dadosProjeto: DadosProjeto): Promise<RespostaApi<DadosProjeto>> {
    try {
      const url = dadosProjeto.id 
        ? `${API_BASE_URL}${API_ENDPOINTS.PROJECTS.UPDATE(dadosProjeto.id)}`  // ✅ /api/v1/projects/{id}
        : `${API_BASE_URL}${API_ENDPOINTS.PROJECTS.CREATE}`;  // ✅ /api/v1/projects
      
      const method = dadosProjeto.id ? 'PUT' : 'POST';

      console.log(`💾 ${method} projeto em:`, url);
      console.log('📦 Dados:', dadosProjeto);

      const response = await fetch(url, {
        method,
        headers: this.getHeaders(),
        body: JSON.stringify(dadosProjeto),
      });

      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        console.error('❌ Erro do servidor:', error);
        throw new Error(error.detail || 'Erro ao salvar projeto');
      }

      const dados = await response.json();
      console.log('✅ Projeto salvo:', dados);
      
      return {
        dados,
        sucesso: true,
        mensagem: dadosProjeto.id ? 'Projeto atualizado com sucesso' : 'Projeto criado com sucesso'
      };
    } catch (erro) {
      console.error('❌ Erro ao salvar projeto:', erro);
      return {
        dados: dadosProjeto,
        sucesso: false,
        mensagem: `Erro ao salvar projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
  
  /**
   * Exclui um projeto pelo ID
   * ✅ CORRIGIDO: URL de /api/projects/{id} → /api/v1/projects/{id}
   */
  async excluirProjeto(id: string): Promise<RespostaApi<void>> {
    try {
      const url = `${API_BASE_URL}${API_ENDPOINTS.PROJECTS.DELETE(id)}`;  // ✅ /api/v1/projects/{id}
      console.log('🗑️ Excluindo projeto em:', url);

      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao excluir projeto');
      }

      console.log('✅ Projeto excluído');

      return {
        dados: undefined,
        sucesso: true,
        mensagem: 'Projeto excluído com sucesso'
      };
    } catch (erro) {
      console.error(`❌ Erro ao excluir projeto ${id}:`, erro);
      return {
        dados: undefined,
        sucesso: false,
        mensagem: `Erro ao excluir projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  /**
   * ✅ NOVO: Busca projetos do usuário logado (mesmo que listarProjetos)
   */
  async listarMeusProjetos(): Promise<RespostaApi<DadosProjeto[]>> {
    // Usa o mesmo método, já que ambos fazem a mesma coisa
    return this.listarProjetos();
  }
}

// Exportar uma instância única do serviço
export const apiProjeto = new ServicoApiProjeto();
