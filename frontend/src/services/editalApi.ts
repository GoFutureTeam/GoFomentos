import { Edital, EditalCreateData, EditalFilters, EditalEnums, ApiResponse, EditalUpdateData } from '../types/edital';
import { fixEncoding } from '../lib/utils';

// Configuração da API
const API_BASE_URL = 'https://fomentos-homologacao-api.gofuture.cc/api/v1';

// Interface para resposta da API
interface ApiEditaisResponse {
  editais: Edital[];
  total: number;
  skip: number;
  limit: number;
}

class EditalApiService {
  private baseUrl = '/api';

  /**
   * Corrige problemas de encoding em todos os campos string de um edital
   */
  private cleanEditalData(edital: Edital): Edital {
    const cleanedEdital = { ...edital };
    
    // Lista de campos que são strings e podem ter problemas de encoding
    const stringFields: (keyof Edital)[] = [
      'titulo', 'descricao', 'descricao_resumida', 'descricao_completa',
      'empresa', 'contrapartida', 'cooperacao', 'categoria', 'area_foco',
      'apelido', 'apelido_edital', 'tipo_proponente', 'tipo_contrapartida',
      'tipo_cooperacao', 'arquivo_nome', 'origem', 'financiador_1', 'financiador_2',
      'observacoes', 'empresas_elegiveis', 'link', 'tipo_recurso', 'recepcao_recursos'
    ];
    
    // Aplica a correção de encoding em todos os campos string
    stringFields.forEach(field => { 
      if (cleanedEdital[field] && typeof cleanedEdital[field] === 'string') {
        (cleanedEdital as Record<string, unknown>)[field] = fixEncoding(cleanedEdital[field] as string);
      }
    });
    
    return cleanedEdital;
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      // Verificar se a resposta é HTML (indica erro de proxy/404)
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('text/html')) {
        console.error(`API retornou HTML em vez de JSON para ${endpoint}. Status: ${response.status}`);
        return {
          data: null as T,
          success: false,
          status: response.status,
          message: `API indisponível: endpoint ${endpoint} não encontrado (Status: ${response.status})`
        };
      }

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        console.error('Erro ao parsear JSON da resposta:', parseError);
        return {
          data: null as T,
          success: false,
          status: response.status,
          message: `Resposta inválida da API: não é um JSON válido`
        };
      }

      if (!response.ok) {
        return {
          data: null as T,
          success: false,
          status: response.status,
          message: data.message || `Erro HTTP ${response.status}`
        };
      }

      return {
        data,
        success: true,
        status: response.status,
        message: data.message || 'Sucesso'
      };
    } catch (error) {
      console.error('Erro na requisição:', error);
      return {
        data: null as T,
        success: false,
        status: 500,
        message: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }

  async createEdital(data: EditalCreateData): Promise<ApiResponse<Edital>> {
    try {
      const response = await fetch(`${API_BASE_URL}/editais`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const newEdital: Edital = await response.json();

      return {
        data: newEdital,
        success: true,
        status: response.status,
        message: 'Edital criado com sucesso'
      };
    } catch (error) {
      console.error('❌ Erro ao criar edital:', error);

      return {
        data: null,
        success: false,
        status: 500,
        message: `Erro ao criar edital: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      };
    }
  }

  async listEditais(filters: EditalFilters = {}): Promise<ApiResponse<Edital[]>> {
    try {
      // Construir URL com parâmetros
      const params = new URLSearchParams({
        skip: '0',
        limit: '100'
      });

      // Adicionar filtros como parâmetros se existirem
      if (filters.search) {
        params.append('search', filters.search);
      }
      if (filters.categoria) {
        params.append('categoria', filters.categoria);
      }
      if (filters.empresa) {
        params.append('empresa', filters.empresa);
      }
      if (filters.contrapartida) {
        params.append('contrapartida', filters.contrapartida);
      }
      if (filters.financiador) {
        params.append('financiador', filters.financiador);
      }

      const url = `${API_BASE_URL}/editais`;
       console.log('🔗 Fazendo requisição para:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('📊 Dados brutos recebidos da API:', data);
      
      // A API retorna diretamente um array de editais, não um objeto com propriedade editais
      const editaisArray = Array.isArray(data) ? data : (data.editais || []);
      
      // Aplicar limpeza de encoding em todos os editais
      const cleanedEditais = editaisArray.map((edital: Edital) => this.cleanEditalData(edital));
      
      console.log('🔧 Array de editais processado:', cleanedEditais.length, 'editais');
      console.log('🔍 Exemplo do primeiro edital (original):', editaisArray[0]);
      console.log('✨ Exemplo do primeiro edital (limpo):', cleanedEditais[0]);

      return {
        data: cleanedEditais,
        success: true,
        status: response.status,
        message: `${cleanedEditais.length} editais carregados com sucesso`
      };
    } catch (error) {
      console.error('❌ Erro ao carregar editais da API:', error);

      console.warn('⚠️ Retornando array vazio devido ao erro na API');
      const filteredEditais: Edital[] = [];

      return {
        data: filteredEditais,
        success: false,
        status: 500,
        message: `Erro ao carregar da API. Usando dados locais: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      };
    }
  }

  async getEnums(): Promise<ApiResponse<EditalEnums>> {
    const enums: EditalEnums = {
      categorias: ['Tecnologia', 'Pesquisa', 'Ciência', 'Empreendedorismo', 'Inovação'],
      empresas: ['FINEP', 'FAPESP', 'CNPq', 'BNDES', 'SEBRAE', 'CAPES'],
      contrapartidas: ['Sim', 'Não'],
      cooperacoes: ['Nacional', 'Internacional', 'Estadual']
    };
    
    return {
      data: enums,
      success: true,
      status: 200,
      message: 'Enums carregados com sucesso'
    };
  }

  async getEdital(id: number): Promise<ApiResponse<Edital>> {
    try {
      console.log(`🔍 Buscando edital por ID: ${id}`);
      const url = `${API_BASE_URL}/editais/${id}`;
      console.log(`🌐 URL da requisição: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log(`📡 Status da resposta: ${response.status}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const edital: Edital = await response.json();
      console.log(`🎯 Edital encontrado (original):`, edital);
      
      // Aplicar limpeza de encoding
      const cleanedEdital = this.cleanEditalData(edital);
      
      console.log(`✨ Edital limpo:`, cleanedEdital);
      console.log(`📋 Títulos e descrições (limpos):`, {
        id: cleanedEdital.id,
        titulo: cleanedEdital.titulo,
        descricao: cleanedEdital.descricao,
        descricao_resumida: cleanedEdital.descricao_resumida,
        descricao_completa: cleanedEdital.descricao_completa
      });
      
      // Corrigindo o link do PDF para usar o caminho correto
      if (cleanedEdital && cleanedEdital.id) {
        cleanedEdital.pdfLink = `${API_BASE_URL}/edital/${cleanedEdital.id}`;
      }
      
      return {
        data: cleanedEdital,
        success: true,
        status: response.status,
        message: 'Edital encontrado'
      };
    } catch (error) {
      console.error('❌ Erro ao buscar edital:', error);
      
      return {
        data: null,
        success: false,
        status: 404,
        message: `Edital não encontrado: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      };
    }
  }

  async getEditalByApelido(apelido: string): Promise<ApiResponse<Edital>> {
    try {
      const response = await fetch(`${API_BASE_URL}/editais/apelido/${apelido}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const edital: Edital = await response.json();
      console.log('🎯 Edital encontrado por apelido (original):', apelido, edital);
      
      // Aplicar limpeza de encoding
      const cleanedEdital = this.cleanEditalData(edital);
      console.log('✨ Edital limpo por apelido:', cleanedEdital);
      
      return {
        data: cleanedEdital,
        success: true,
        status: response.status,
        message: 'Edital encontrado'
      };
    } catch (error) {
      console.error('❌ Erro ao buscar edital por apelido:', error);
      
      return {
        data: null,
        success: false,
        status: 404,
        message: `Edital não encontrado: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      };
    }
  }

  async updateEdital(id: number, data: EditalUpdateData): Promise<ApiResponse<Edital>> {
    try {
      const response = await fetch(`${API_BASE_URL}/editais/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const updatedEdital: Edital = await response.json();
      
      return {
        data: updatedEdital,
        success: true,
        status: response.status,
        message: 'Edital atualizado com sucesso'
      };
    } catch (error) {
      console.error('❌ Erro ao atualizar edital:', error);
      
      return {
        data: null,
        success: false,
        status: 500,
        message: `Erro ao atualizar edital: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      };
    }
  }

  async updatePdf(id: number, file: File): Promise<ApiResponse<Edital>> {
    try {
      const formData = new FormData();
      formData.append('pdf', file);
      
      const response = await fetch(`${API_BASE_URL}/editais/${id}/pdf`, {
        method: 'PUT',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const updatedEdital: Edital = await response.json();
      
      return {
        data: updatedEdital,
        success: true,
        status: response.status,
        message: 'PDF atualizado com sucesso'
      };
    } catch (error) {
      console.error('❌ Erro ao atualizar PDF:', error);
      
      return {
        data: null,
        success: false,
        status: 500,
        message: `Erro ao atualizar PDF: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      };
    }
  }

  async deleteEdital(id: number): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${API_BASE_URL}/editais/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return {
        data: undefined,
        success: true,
        status: response.status,
        message: 'Edital deletado com sucesso'
      };
    } catch (error) {
      console.error('❌ Erro ao deletar edital:', error);
      
      return {
        data: undefined,
        success: false,
        status: 500,
        message: `Erro ao deletar edital: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      };
    }
  }

  // Função para verificar se PDF existe antes de tentar baixar
  async checkPdfExists(pdfUrl: string): Promise<boolean> {
    try {
      const response = await fetch(pdfUrl, {
        method: 'HEAD' // Apenas verifica se existe, sem baixar
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  // Função para higienizar e extrair dados do HTML de download
  private parseDownloadResponse(htmlContent: string): { url: string; filename: string } | null {
    try {
      // Criar um elemento temporário para parsear o HTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = htmlContent;
      
      // Buscar pelo elemento <a> com atributo download
      const downloadLink = tempDiv.querySelector('a[download]') as HTMLAnchorElement;
      
      if (downloadLink) {
        const url = downloadLink.href;
        const filename = downloadLink.getAttribute('download') || '';
        
        console.log('Link extraído:', { url, filename });
        return { url, filename };
      }
      
      // Fallback: tentar regex se DOM parsing falhar
      const hrefMatch = htmlContent.match(/href\s*=\s*["']([^"']+)["']/i);
      const downloadMatch = htmlContent.match(/download\s*=\s*["']([^"']+)["']/i);
      
      if (hrefMatch) {
        const url = hrefMatch[1];
        const filename = downloadMatch ? downloadMatch[1] : 'download.pdf';
        
        console.log('Link extraído via regex:', { url, filename });
        return { url, filename };
      }
      
      return null;
    } catch (error) {
      console.error('Erro ao parsear resposta de download:', error);
      return null;
    }
  }

  async downloadPdf(pdfUrl: string, filename?: string): Promise<void> {
    try {
      console.log(`Tentando baixar PDF do link: ${pdfUrl}...`);
      const response = await fetch(pdfUrl);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`PDF não encontrado para este edital. Verifique se o arquivo foi anexado ao edital.`);
        }
        if (response.status === 500) {
          throw new Error(`Erro no servidor ao buscar PDF.`);
        }
        throw new Error(`Erro ao baixar PDF: ${response.status} - ${response.statusText}`);
      }

      // Verificar o content-type
      const contentType = response.headers.get('content-type');
      console.log('Content-Type recebido:', contentType);
      
      // Extrair nome do arquivo do content-disposition, se disponível
      let extractedFilename = '';
      const contentDisposition = response.headers.get('content-disposition');
      console.log('Content-Disposition:', contentDisposition);
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=["']?([^"']+)["']?/i);
        if (filenameMatch && filenameMatch[1]) {
          extractedFilename = filenameMatch[1];
          console.log('Nome de arquivo extraído:', extractedFilename);
        }
      }

      // Obter o blob da resposta
      const blob = await response.blob();
      
      if (blob.size === 0) {
        throw new Error('PDF está vazio ou corrompido');
      }

      // Usar o nome de arquivo da resposta, ou o fornecido, ou um padrão
      const finalFilename = filename || extractedFilename || `downloaded.pdf`;
      
      // Fazer o download do blob
      this.downloadBlob(blob, finalFilename);
      console.log(`PDF baixado com sucesso!`);
      return;
      
    } catch (error) {
      console.error('Erro ao baixar PDF:', error);
      throw error;
    }
  }

  // Função auxiliar para fazer download de blob
  private downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  async downloadPdfByApelido(apelido: string, filename?: string): Promise<void> {
    try {
      console.log(`Tentando baixar PDF do edital ${apelido}...`);
      const response = await fetch(`${this.baseUrl}/editais/apelido/${apelido}/pdf`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`PDF não encontrado para este edital. Verifique se o arquivo foi anexado ao edital.`);
        }
        if (response.status === 500) {
          throw new Error(`Erro no servidor ao buscar PDF do edital ${apelido}`);
        }
        throw new Error(`Erro ao baixar PDF: ${response.status} - ${response.statusText}`);
      }

      // Verificar o content-type
      const contentType = response.headers.get('content-type');
      console.log('Content-Type recebido:', contentType);
      
      // Extrair nome do arquivo do content-disposition, se disponível
      let extractedFilename = '';
      const contentDisposition = response.headers.get('content-disposition');
      console.log('Content-Disposition:', contentDisposition);
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=["']?([^"']+)["']?/i);
        if (filenameMatch && filenameMatch[1]) {
          extractedFilename = filenameMatch[1];
          console.log('Nome de arquivo extraído:', extractedFilename);
        }
      }

      // Obter o blob da resposta
      const blob = await response.blob();
      
      if (blob.size === 0) {
        throw new Error('PDF está vazio ou corrompido');
      }

      // Usar o nome de arquivo da resposta, ou o fornecido, ou um padrão
      const finalFilename = filename || extractedFilename || `${apelido}.pdf`;
      
      // Fazer o download do blob
      this.downloadBlob(blob, finalFilename);
      console.log(`PDF do edital ${apelido} baixado com sucesso!`);
      return;
      
    } catch (error) {
      console.error('Erro ao baixar PDF:', error);
      throw error;
    }
  }
}

export const editalApi = new EditalApiService();