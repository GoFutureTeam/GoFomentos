import { Edital, EditalCreateData, EditalFilters, EditalEnums, ApiResponse, EditalUpdateData } from '../types/edital';
import { fixEncoding } from '../lib/utils';

// Configuração da API
const URL_BASE_API = 'https://fomentos-homologacao-api.gofuture.cc/api/v1';

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

  async criarEdital(dados: EditalCreateData): Promise<ApiResponse<Edital>> {
    try {
      const resposta = await fetch(`${URL_BASE_API}/editais`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(dados)
      });

      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }

      const novoEdital: Edital = await resposta.json();

      return {
        data: novoEdital,
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

      const url = `${URL_BASE_API}/editais`;
       console.log('🔗 Fazendo requisição para:', url);

      const resposta = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }

      const dados = await resposta.json();
      console.log('📊 Dados brutos recebidos da API:', dados);
      
      // A API retorna diretamente um array de editais, não um objeto com propriedade editais
      const arrayEditais = Array.isArray(dados) ? dados : (dados.editais || []);
      
      // Aplicar limpeza de encoding em todos os editais
      const editaisLimpos = arrayEditais.map((edital: Edital) => this.limparDadosEdital(edital));
      
      console.log('🔧 Array de editais processado:', editaisLimpos.length, 'editais');
      console.log('🔍 Exemplo do primeiro edital (original):', arrayEditais[0]);
      console.log('✨ Exemplo do primeiro edital (limpo):', editaisLimpos[0]);

      return {
        data: editaisLimpos,
        success: true,
        status: resposta.status,
        message: `${editaisLimpos.length} editais carregados com sucesso`
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

  async obterEdital(id: number): Promise<ApiResponse<Edital>> {
    try {
      console.log(`🔍 Buscando edital por ID: ${id}`);
      const url = `${URL_BASE_API}/editais/${id}`;
      console.log(`🌐 URL da requisição: ${url}`);
      
      const resposta = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
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
        editalLimpo.pdfLink = `${URL_BASE_API}/edital/${editalLimpo.id}`;
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
    try {
      const resposta = await fetch(`${URL_BASE_API}/editais/apelido/${apelido}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!resposta.ok) {
        throw new Error(`HTTP error! status: ${resposta.status}`);
      }
      
      const edital: Edital = await resposta.json();
      console.log('🎯 Edital encontrado por apelido (original):', apelido, edital);
      
      // Aplicar limpeza de encoding
      const editalLimpo = this.limparDadosEdital(edital);
      console.log('✨ Edital limpo por apelido:', editalLimpo);
      
      return {
        data: editalLimpo,
        success: true,
        status: resposta.status,
        message: 'Edital encontrado'
      };
    } catch (erro) {
      console.error('❌ Erro ao buscar edital por apelido:', erro);
      
      return {
        data: null,
        success: false,
        status: 404,
        message: `Edital não encontrado: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async atualizarEdital(id: number, dados: EditalUpdateData): Promise<ApiResponse<Edital>> {
    try {
      const resposta = await fetch(`${URL_BASE_API}/editais/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
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

  async atualizarPdf(id: number, arquivo: File): Promise<ApiResponse<Edital>> {
    try {
      const formData = new FormData();
      formData.append('pdf', arquivo);
      
      const resposta = await fetch(`${URL_BASE_API}/editais/${id}/pdf`, {
        method: 'PUT',
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

  async deletarEdital(id: number): Promise<ApiResponse<void>> {
    try {
      const resposta = await fetch(`${URL_BASE_API}/editais/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
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
    try {
      console.log(`Tentando baixar PDF do edital ${apelido}...`);
      const resposta = await fetch(`${this.urlBase}/editais/apelido/${apelido}/pdf`);
      
      if (!resposta.ok) {
        if (resposta.status === 404) {
          throw new Error(`PDF não encontrado para este edital. Verifique se o arquivo foi anexado ao edital.`);
        }
        if (resposta.status === 500) {
          throw new Error(`Erro no servidor ao buscar PDF do edital ${apelido}`);
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
      const nomeArquivoFinal = nomeArquivo || nomeArquivoExtraido || `${apelido}.pdf`;
      
      // Fazer o download do blob
      this.downloadBlob(blob, nomeArquivoFinal);
      console.log(`PDF do edital ${apelido} baixado com sucesso!`);
      return;
      
    } catch (erro) {
      console.error('Erro ao baixar PDF:', erro);
      throw erro;
    }
  }
}

export const apiEdital = new ServicoApiEdital();
