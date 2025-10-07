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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';

/**
 * Classe de serviço para gerenciar projetos na API
 */
class ServicoApiProjeto {
  private getHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }
  
  /**
   * Busca todos os projetos do usuário autenticado
   */
  async listarProjetos(): Promise<RespostaApi<DadosProjeto[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects`, {
        headers: this.getHeaders(),
      });

      if (response.status === 401) {
        localStorage.removeItem('auth_token');
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (!response.ok) {
        throw new Error('Erro ao listar projetos');
      }

      const dados = await response.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: 'Projetos carregados com sucesso'
      };
    } catch (erro) {
      console.error('Erro ao listar projetos:', erro);
      return {
        dados: [],
        sucesso: false,
        mensagem: `Erro ao carregar projetos: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
  
  /**
   * Busca um projeto específico pelo ID
   */
  async obterProjeto(id: string): Promise<RespostaApi<DadosProjeto>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Erro ao buscar projeto');
      }

      const dados = await response.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: 'Projeto encontrado com sucesso'
      };
    } catch (erro) {
      console.error(`Erro ao buscar projeto ${id}:`, erro);
      return {
        dados: {} as DadosProjeto,
        sucesso: false,
        mensagem: `Erro ao buscar projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
  
  /**
   * Salva um projeto (cria novo ou atualiza existente)
   */
  async salvarProjeto(dadosProjeto: DadosProjeto): Promise<RespostaApi<DadosProjeto>> {
    try {
      const url = dadosProjeto.id 
        ? `${API_BASE_URL}/api/projects/${dadosProjeto.id}`
        : `${API_BASE_URL}/api/projects`;
      
      const method = dadosProjeto.id ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: this.getHeaders(),
        body: JSON.stringify(dadosProjeto),
      });

      if (response.status === 401) {
        localStorage.removeItem('auth_token');
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao salvar projeto');
      }

      const dados = await response.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: dadosProjeto.id ? 'Projeto atualizado com sucesso' : 'Projeto criado com sucesso'
      };
    } catch (erro) {
      console.error('Erro ao salvar projeto:', erro);
      return {
        dados: dadosProjeto,
        sucesso: false,
        mensagem: `Erro ao salvar projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
  
  /**
   * Exclui um projeto pelo ID
   */
  async excluirProjeto(id: string): Promise<RespostaApi<void>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Erro ao excluir projeto');
      }

      return {
        dados: undefined,
        sucesso: true,
        mensagem: 'Projeto excluído com sucesso'
      };
    } catch (erro) {
      console.error(`Erro ao excluir projeto ${id}:`, erro);
      return {
        dados: undefined,
        sucesso: false,
        mensagem: `Erro ao excluir projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
}

// Exportar uma instância única do serviço
export const apiProjeto = new ServicoApiProjeto();
