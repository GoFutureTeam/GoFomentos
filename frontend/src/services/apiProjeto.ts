// Interface para os dados do projeto
export interface DadosProjeto {
  id?: string;
  nomeProjeto: string;
  descricao: string;
  objetivoPrincipal?: string;
  areaProjeto?: string;
  orcamento?: number;
  dataInicio?: string;
  dataFim?: string;
  usuarioId?: string;
  dataCriacao?: string;
  dataAtualizacao?: string;
}

// Interface para resposta da API
interface RespostaApi<T> {
  dados: T;
  sucesso: boolean;
  mensagem: string;
}

/**
 * Classe de serviço para gerenciar projetos na API
 */
class ServicoApiProjeto {
  private urlBase = '/api/v1';
  private projetosLocais: DadosProjeto[] = [];
  
  constructor() {
    // Carregar projetos do localStorage ao inicializar
    const projetosSalvos = localStorage.getItem('projetos');
    if (projetosSalvos) {
      this.projetosLocais = JSON.parse(projetosSalvos);
    }
  }
  
  private salvarNoLocalStorage() {
    localStorage.setItem('projetos', JSON.stringify(this.projetosLocais));
  }
  
  /**
   * Busca todos os projetos do usuário autenticado
   */
  async listarProjetos(): Promise<RespostaApi<DadosProjeto[]>> {
    try {
      // Em uma implementação real, isso seria uma chamada à API
      // const resposta = await apiCliente.get(`${this.urlBase}/projetos`);
      // return resposta.data;
      
      // Simulação de resposta da API
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Retornar apenas projetos salvos localmente
      return {
        dados: this.projetosLocais,
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
      // Em uma implementação real, isso seria uma chamada à API
      // const resposta = await apiCliente.get(`${this.urlBase}/projetos/${id}`);
      // return resposta.data;
      
      // Simulação de resposta da API
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Simular projeto encontrado
      const projeto = {
        id,
        nomeProjeto: 'Projeto de Educação Ambiental',
        descricao: 'Iniciativa para conscientização sobre preservação ambiental em escolas públicas',
        objetivoPrincipal: 'Conscientizar estudantes sobre a importância da preservação ambiental',
        areaProjeto: 'Educação Ambiental',
        orcamento: 50000,
        dataCriacao: '2023-10-15'
      };
      
      return {
        dados: projeto,
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
      let projetoSalvo: DadosProjeto;
      
      // Em uma implementação real, isso seria uma chamada à API
      if (dadosProjeto.id) {
        // Atualiza um projeto existente
        // resposta = await apiCliente.put(`${this.urlBase}/projetos/${dadosProjeto.id}`, dadosProjeto);
        
        // Simulação de resposta da API para atualização
        await new Promise(resolve => setTimeout(resolve, 400));
        
        const index = this.projetosLocais.findIndex(p => p.id === dadosProjeto.id);
        if (index !== -1) {
          this.projetosLocais[index] = {
            ...dadosProjeto,
            dataAtualizacao: new Date().toISOString()
          };
          projetoSalvo = this.projetosLocais[index];
        } else {
          projetoSalvo = {
            ...dadosProjeto,
            dataAtualizacao: new Date().toISOString()
          };
        }
      } else {
        // Cria um novo projeto
        // resposta = await apiCliente.post(`${this.urlBase}/projetos`, dadosProjeto);
        
        // Simulação de resposta da API para criação
        await new Promise(resolve => setTimeout(resolve, 400));
        
        projetoSalvo = {
          ...dadosProjeto,
          id: Math.random().toString(36).substring(2, 15),
          dataCriacao: new Date().toISOString(),
          dataAtualizacao: new Date().toISOString()
        };
        
        this.projetosLocais.push(projetoSalvo);
      }
      
      // Salvar no localStorage
      this.salvarNoLocalStorage();
      
      return {
        dados: projetoSalvo,
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
      // Em uma implementação real, isso seria uma chamada à API
      // await apiCliente.delete(`${this.urlBase}/projetos/${id}`);
      
      // Simulação de resposta da API
      await new Promise(resolve => setTimeout(resolve, 300));
      
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
