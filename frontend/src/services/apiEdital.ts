import { Edital, EditalCreateData, EditalFilters, EditalEnums, ApiResponse, EditalUpdateData } from '../types/edital';
import { fixEncoding } from '../lib/utils';
import { API_ENDPOINTS, buildApiUrl } from './api';
import { adaptEditalFromBackend, adaptEditalToBackend } from '../adapters/editalAdapter';
import TokenService from './tokenService';

// Configuração da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

// Interface para resposta da API
interface RespostaApiEditais {
  editais: Edital[];
  total: number;
  skip: number;
  limit: number;
}

class ServicoApiEdital {
  private urlBase = '/api';

  /**
   * Retorna headers com autenticação
   */
  private getAuthHeaders(): HeadersInit {
    const token = TokenService.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  /**
   * Corrige problemas de encoding em todos os campos string de um edital
   */
  private limparDadosEdital(edital: Edital): Edital {
    const editalLimpo = { ...edital };
    
    // Lista de campos que são strings e podem ter problemas de encoding
    const camposString: (keyof Edital)[] = [
      'titulo', 'descricao', 'descricao_resumida', 'descricao_completa',
      'empresa', 'contrapartida', 'cooperacao', 'categoria', 'area_foco',
      'apelido', 'apelido_edital', 'tipo_proponente', 'tipo_contrapartida',
      'tipo_cooperacao', 'arquivo_nome', 'origem', 'financiador_1', 'financiador_2',
      'observacoes', 'empresas_elegiveis', 'link', 'tipo_recurso', 'recepcao_recursos'
    ];
    
    // Aplica a correção de encoding em todos os campos string
    camposString.forEach(campo => { 
      if (editalLimpo[campo] && typeof editalLimpo[campo] === 'string') {
        (editalLimpo as Record<string, unknown>)[campo] = fixEncoding(editalLimpo[campo] as string);
      }
    });
    
    return editalLimpo;
  }

  private async fazerRequisicao<T>(endpoint: string, opcoes: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const resposta = await fetch(`${this.urlBase}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...opcoes.headers,
        },
        ...opcoes,
      });

      // Verificar se a resposta é HTML (indica erro de proxy/404)
      const tipoConteudo = resposta.headers.get('content-type');
      if (tipoConteudo && tipoConteudo.includes('text/html')) {
        console.error(`API retornou HTML em vez de JSON para ${endpoint}. Status: ${resposta.status}`);
        return {
          data: null as T,
          success: false,
          status: resposta.status,
          message: `API indisponível: endpoint ${endpoint} não encontrado (Status: ${resposta.status})`
        };
      }

      let dados;
      try {
        dados = await resposta.json();
      } catch (erroParser) {
        console.error('Erro ao parsear JSON da resposta:', erroParser);
        return {
          data: null as T,
          success: false,
          status: resposta.status,
          message: `Resposta inválida da API: não é um JSON válido`
        };
      }

      if (!resposta.ok) {
        return {
          data: null as T,
          success: false,
          status: resposta.status,
          message: dados.message || `Erro HTTP ${resposta.status}`
        };
      }

      return {
        data: dados,
        success: true,
        status: resposta.status,
        message: dados.message || 'Sucesso'
      };
    } catch (erro) {
      console.error('Erro na requisição:', erro);
      return {
        data: null as T,
        success: false,
        status: 500,
        message: erro instanceof Error ? erro.message : 'Erro desconhecido'
      };
    }
  }

  /**
   * Criar novo edital
   * ✅ ADAPTADO: Converte dados do frontend para o backend
   */
  async criarEdital(dados: EditalCreateData): Promise<ApiResponse<Edital>> {
    try {
      // ✅ Adaptar dados antes de enviar (se necessário)
      const resposta = await fetch(`${API_BASE_URL}${API_ENDPOINTS.EDITAIS.CREATE}`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(dados)
      });

      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }

      const novoEdital = await resposta.json();
      
      // ✅ Adaptar resposta do backend
      const editalAdaptado = adaptEditalFromBackend(novoEdital as Record<string, unknown>);
      const editalLimpo = this.limparDadosEdital(editalAdaptado);

      return {
        data: editalLimpo,
        success: true,
        status: resposta.status,
        message: 'Edital criado com sucesso'
      };
    } catch (erro) {
      console.error('❌ Erro ao criar edital:', erro);

      return {
        data: null,
        success: false,
        status: 500,
        message: `Erro ao criar edital: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  /**
   * Listar editais com filtros
   * ✅ ADAPTADO: Converte resposta do backend
   */
  async listarEditais(filtros: EditalFilters = {}): Promise<ApiResponse<Edital[]>> {
    try {
      // Construir URL com parâmetros
      const params = new URLSearchParams({
        skip: '0',
        limit: '100'
      });

      // Adicionar filtros como parâmetros se existirem
      if (filtros.search) {
        params.append('search', filtros.search);
      }
      if (filtros.categoria) {
        params.append('categoria', filtros.categoria);
      }
      if (filtros.empresa) {
        params.append('empresa', filtros.empresa);
      }
      if (filtros.contrapartida) {
        params.append('contrapartida', filtros.contrapartida);
      }
      if (filtros.financiador) {
        params.append('financiador', filtros.financiador);
      }

      const url = `${API_BASE_URL}${API_ENDPOINTS.EDITAIS.LIST}`;
      console.log('🔗 Fazendo requisição para:', url);

      const resposta = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }

      const dados = await resposta.json();
      console.log('📊 Dados brutos recebidos da API:', dados);
      
      // A API retorna diretamente um array de editais
      const arrayEditais = Array.isArray(dados) ? dados : (dados.editais || []);
      
      // 🔍 LOG: Mostrar estrutura do primeiro edital recebido do backend
      if (arrayEditais.length > 0) {
        console.log('📋 Estrutura do primeiro edital recebido do BACKEND:', {
          uuid: arrayEditais[0].uuid,
          apelido_edital: arrayEditais[0].apelido_edital,
          link: arrayEditais[0].link,
          financiador_1: arrayEditais[0].financiador_1,
          financiador_2: arrayEditais[0].financiador_2,
          area_foco: arrayEditais[0].area_foco,
          tipo_proponente: arrayEditais[0].tipo_proponente,
          empresas_que_podem_submeter: arrayEditais[0].empresas_que_podem_submeter,
          duracao_min_meses: arrayEditais[0].duracao_min_meses,
          duracao_max_meses: arrayEditais[0].duracao_max_meses,
          valor_min_R: arrayEditais[0].valor_min_R,
          valor_max_R: arrayEditais[0].valor_max_R,
          tipo_recurso: arrayEditais[0].tipo_recurso,
          recepcao_recursos: arrayEditais[0].recepcao_recursos,
          custeio: arrayEditais[0].custeio,
          capital: arrayEditais[0].capital,
          contrapartida_min_pct: arrayEditais[0].contrapartida_min_pct,
          contrapartida_max_pct: arrayEditais[0].contrapartida_max_pct,
          tipo_contrapartida: arrayEditais[0].tipo_contrapartida,
          data_inicial_submissao: arrayEditais[0].data_inicial_submissao,
          data_final_submissao: arrayEditais[0].data_final_submissao,
          data_resultado: arrayEditais[0].data_resultado,
          descricao_completa: arrayEditais[0].descricao_completa,
          origem: arrayEditais[0].origem,
          observacoes: arrayEditais[0].observacoes,
          status: arrayEditais[0].status,
          created_at: arrayEditais[0].created_at,
          updated_at: arrayEditais[0].updated_at
        });
      }
      
      // ✅ Adaptar cada edital do backend
      const editaisAdaptados = arrayEditais.map((edital: Record<string, unknown>) => {
        const adaptado = adaptEditalFromBackend(edital);
        return this.limparDadosEdital(adaptado);
      });
      
      console.log('🔧 Editais processados e adaptados:', editaisAdaptados.length, 'editais');
      
      // 🔍 LOG: Mostrar estrutura do primeiro edital APÓS adaptação
      if (editaisAdaptados.length > 0) {
        console.log('📋 Estrutura do primeiro edital APÓS ADAPTAÇÃO:', editaisAdaptados[0]);
      }

      return {
        data: editaisAdaptados,
        success: true,
        status: resposta.status,
        message: `${editaisAdaptados.length} editais carregados com sucesso`
      };
    } catch (erro) {
      console.error('❌ Erro ao carregar editais da API:', erro);

      console.warn('⚠️ Retornando array vazio devido ao erro na API');
      const editaisFiltrados: Edital[] = [];

      return {
        data: editaisFiltrados,
        success: false,
        status: 500,
        message: `Erro ao carregar da API. Usando dados locais: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async obterEnums(): Promise<ApiResponse<EditalEnums>> {
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

  async obterEdital(uuid: string): Promise<ApiResponse<Edital>> {
    try {
      console.log(`🔍 Buscando edital por UUID: ${uuid}`);
      const url = `${API_BASE_URL}${API_ENDPOINTS.EDITAIS.DETAIL(uuid)}`;
      console.log(`🌐 URL da requisição: ${url}`);
      
      const resposta = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });
      
      console.log(`📡 Status da resposta: ${resposta.status}`);
      
      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }
      
      const edital: Edital = await resposta.json();
      console.log(`🎯 Edital encontrado (original):`, edital);
      
      // Aplicar limpeza de encoding
      const editalLimpo = this.limparDadosEdital(edital);
      
      console.log(`✨ Edital limpo:`, editalLimpo);
      console.log(`📋 Títulos e descrições (limpos):`, {
        id: editalLimpo.id,
        titulo: editalLimpo.titulo,
        descricao: editalLimpo.descricao,
        descricao_resumida: editalLimpo.descricao_resumida,
        descricao_completa: editalLimpo.descricao_completa
      });
      
      // Corrigindo o link do PDF para usar o caminho correto
      if (editalLimpo && editalLimpo.id) {
        editalLimpo.pdfLink = `${API_BASE_URL}/api/v1/edital/${editalLimpo.id}`;
      }
      
      return {
        data: editalLimpo,
        success: true,
        status: resposta.status,
        message: 'Edital encontrado'
      };
    } catch (erro) {
      console.error('❌ Erro ao buscar edital:', erro);
      
      return {
        data: null,
        success: false,
        status: 404,
        message: `Edital não encontrado: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async obterEditalPorApelido(apelido: string): Promise<ApiResponse<Edital>> {
    console.warn('⚠️ obterEditalPorApelido: Endpoint /api/v1/editais/apelido/{apelido} não existe no backend');
    console.warn('⚠️ Use obterEdital(id) com o UUID do edital em vez de apelido');
    
    return {
      data: null,
      success: false,
      status: 501,
      message: 'Endpoint não implementado no backend. Use obterEdital(id) com o UUID do edital.'
    };
  }

  async atualizarEdital(uuid: string, dados: EditalUpdateData): Promise<ApiResponse<Edital>> {
    try {
      const resposta = await fetch(`${API_BASE_URL}${API_ENDPOINTS.EDITAIS.UPDATE(uuid)}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(dados)
      });
      
      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }
      
      const editalAtualizado: Edital = await resposta.json();
      
      return {
        data: editalAtualizado,
        success: true,
        status: resposta.status,
        message: 'Edital atualizado com sucesso'
      };
    } catch (erro) {
      console.error('❌ Erro ao atualizar edital:', erro);
      
      return {
        data: null,
        success: false,
        status: 500,
        message: `Erro ao atualizar edital: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async atualizarPdf(uuid: string, arquivo: File): Promise<ApiResponse<Edital>> {
    try {
      const formData = new FormData();
      formData.append('pdf', arquivo);
      
      const token = TokenService.getAccessToken();
      const resposta = await fetch(`${API_BASE_URL}/api/v1/editais/${uuid}/pdf`, {
        method: 'PUT',
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: formData
      });
      
      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }
      
      const editalAtualizado: Edital = await resposta.json();
      
      return {
        data: editalAtualizado,
        success: true,
        status: resposta.status,
        message: 'PDF atualizado com sucesso'
      };
    } catch (erro) {
      console.error('❌ Erro ao atualizar PDF:', erro);
      
      return {
        data: null,
        success: false,
        status: 500,
        message: `Erro ao atualizar PDF: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async deletarEdital(uuid: string): Promise<ApiResponse<void>> {
    try {
      const resposta = await fetch(`${API_BASE_URL}${API_ENDPOINTS.EDITAIS.DELETE(uuid)}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      });
      
      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }
      
      return {
        data: undefined,
        success: true,
        status: resposta.status,
        message: 'Edital deletado com sucesso'
      };
    } catch (erro) {
      console.error('❌ Erro ao deletar edital:', erro);
      
      return {
        data: undefined,
        success: false,
        status: 500,
        message: `Erro ao deletar edital: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  // Função para verificar se PDF existe antes de tentar baixar
  async verificarExistenciaPdf(pdfUrl: string): Promise<boolean> {
    try {
      const resposta = await fetch(pdfUrl, {
        method: 'HEAD' // Apenas verifica se existe, sem baixar
      });
      return resposta.ok;
    } catch {
      return false;
    }
  }

  // Função para higienizar e extrair dados do HTML de download
  private parseRespostaDownload(conteudoHtml: string): { url: string; filename: string } | null {
    try {
      // Criar um elemento temporário para parsear o HTML
      const divTemp = document.createElement('div');
      divTemp.innerHTML = conteudoHtml;
      
      // Buscar pelo elemento <a> com atributo download
      const linkDownload = divTemp.querySelector('a[download]') as HTMLAnchorElement;
      
      if (linkDownload) {
        const url = linkDownload.href;
        const filename = linkDownload.getAttribute('download') || '';
        
        console.log('Link extraído:', { url, filename });
        return { url, filename };
      }
      
      // Fallback: tentar regex se DOM parsing falhar
      const hrefMatch = conteudoHtml.match(/href\s*=\s*["']([^"']+)["']/i);
      const downloadMatch = conteudoHtml.match(/download\s*=\s*["']([^"']+)["']/i);
      
      if (hrefMatch) {
        const url = hrefMatch[1];
        const filename = downloadMatch ? downloadMatch[1] : 'download.pdf';
        
        console.log('Link extraído via regex:', { url, filename });
        return { url, filename };
      }
      
      return null;
    } catch (erro) {
      console.error('Erro ao parsear resposta de download:', erro);
      return null;
    }
  }

  async baixarPdf(pdfUrl: string, nomeArquivo?: string): Promise<void> {
    try {
      console.log(`Tentando baixar PDF do link: ${pdfUrl}...`);
      const resposta = await fetch(pdfUrl);
      
      if (!resposta.ok) {
        if (resposta.status === 404) {
          throw new Error(`PDF não encontrado para este edital. Verifique se o arquivo foi anexado ao edital.`);
        }
        if (resposta.status === 500) {
          throw new Error(`Erro no servidor ao buscar PDF.`);
        }
        throw new Error(`Erro ao baixar PDF: ${resposta.status} - ${resposta.statusText}`);
      }

      // Verificar o content-type
      const tipoConteudo = resposta.headers.get('content-type');
      console.log('Content-Type recebido:', tipoConteudo);
      
      // Extrair nome do arquivo do content-disposition, se disponível
      let nomeArquivoExtraido = '';
      const contentDisposition = resposta.headers.get('content-disposition');
      console.log('Content-Disposition:', contentDisposition);
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=["']?([^"']+)["']?/i);
        if (filenameMatch && filenameMatch[1]) {
          nomeArquivoExtraido = filenameMatch[1];
          console.log('Nome de arquivo extraído:', nomeArquivoExtraido);
        }
      }

      // Obter o blob da resposta
      const blob = await resposta.blob();
      
      if (blob.size === 0) {
        throw new Error('PDF está vazio ou corrompido');
      }

      // Usar o nome de arquivo da resposta, ou o fornecido, ou um padrão
      const nomeArquivoFinal = nomeArquivo || nomeArquivoExtraido || `downloaded.pdf`;
      
      // Fazer o download do blob
      this.downloadBlob(blob, nomeArquivoFinal);
      console.log(`PDF baixado com sucesso!`);
      return;
      
    } catch (erro) {
      console.error('Erro ao baixar PDF:', erro);
      throw erro;
    }
  }

  // Função auxiliar para fazer download de blob
  private downloadBlob(blob: Blob, nomeArquivo: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = nomeArquivo;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  async baixarPdfPorApelido(apelido: string, nomeArquivo?: string): Promise<void> {
    console.warn('⚠️ baixarPdfPorApelido: Endpoint /editais/apelido/{apelido}/pdf não existe no backend');
    console.warn('⚠️ Use baixarPdf(pdfUrl) com o URL do PDF do edital em vez de apelido');
    
    throw new Error('Endpoint não implementado no backend. Use baixarPdf(pdfUrl) com o URL do PDF do edital.');
  }
}

export const apiEdital = new ServicoApiEdital();
