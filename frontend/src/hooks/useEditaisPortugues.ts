import { useState, useEffect, useCallback } from 'react';
import { Edital, EditalFilters, EditalEnums, EditalCreateData, EditalUpdateData } from '../types/edital';
import { apiEdital } from '../services/apiEdital';
import { useToast } from './use-toast';

/**
 * Hook para gerenciar editais
 * 
 * Nota: Este hook mantém o prefixo "use" para compatibilidade com o React,
 * mas internamente usa nomenclatura em português para maior clareza.
 */
export const useEditaisPortugues = (filtrosIniciais: EditalFilters = {}) => {
  const [editais, setEditais] = useState<Edital[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [filtros, setFiltros] = useState<EditalFilters>(filtrosIniciais);
  const { toast } = useToast();

  const buscarEditais = useCallback(async (filtrosPersonalizados?: EditalFilters) => {
    setCarregando(true);
    setErro(null);
    
    const filtrosParaUsar = filtrosPersonalizados || filtros;
    
    try {
      const resposta = await apiEdital.listarEditais(filtrosParaUsar);
      
      if (resposta.success) {
        console.log("Editais recebidos da API:", resposta.data);
        
        const dataAtual = new Date();

        // Filtrar editais com data válida
        const editaisFiltrados = resposta.data.filter((edital) => {
          if (!edital.data_fim_submissao) {
            console.warn(`Edital sem data de submissão:`, edital);
            return false; // Remove editais sem data de submissão
          }

          const dataSubmissao = new Date(edital.data_fim_submissao);
          return dataSubmissao >= dataAtual; // Mantém apenas editais válidos
        });

        console.log("Editais filtrados:", editaisFiltrados);
        setEditais(editaisFiltrados);
      } else {
        throw new Error(resposta.message || 'Erro ao carregar editais');
      }
    } catch (err) {
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      setErro(mensagemErro);
      toast({
        title: "Erro",
        description: mensagemErro,
        variant: "destructive",
      });
    } finally {
      setCarregando(false);
    }
  }, [filtros, toast]);

  const atualizarFiltros = useCallback((novosFiltros: EditalFilters) => {
    setFiltros(novosFiltros);
    // Remove execução dupla - o useEffect abaixo já vai executar
  }, []);

  const recarregar = useCallback(() => {
    buscarEditais();
  }, [buscarEditais]);

  useEffect(() => {
    buscarEditais();
  }, [filtros, buscarEditais]); // Executa sempre que filtros muda

  return {
    editais,
    carregando,
    erro,
    filtros,
    atualizarFiltros,
    recarregar,
  };
};

/**
 * Hook para gerenciar um edital específico
 */
export const useEditalPortugues = (id?: number) => {
  const [edital, setEdital] = useState<Edital | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [pdfDisponivel, setPdfDisponivel] = useState<boolean | null>(null);
  const [verificandoPdf, setVerificandoPdf] = useState<boolean>(false);
  const { toast } = useToast();

  const verificarDisponibilidadePdf = useCallback(async (idEdital: number) => {
    try {
      setVerificandoPdf(true);
      const isPdfDisponivel = await apiEdital.verificarExistenciaPdf(idEdital.toString());
      setPdfDisponivel(isPdfDisponivel);
      return isPdfDisponivel;
    } catch (erro) {
      console.error("Erro ao verificar disponibilidade do PDF:", erro);
      setPdfDisponivel(false);
      return false;
    } finally {
      setVerificandoPdf(false);
    }
  }, []);

  const buscarEdital = useCallback(async (idEdital: number) => {
    console.log(`🚀 Hook useEditalPortugues: Iniciando busca do edital ID: ${idEdital}`);
    setCarregando(true);
    setErro(null);
    
    try {
      console.log(`📞 Hook useEditalPortugues: Chamando apiEdital.obterEdital(${idEdital})`);
      const resposta = await apiEdital.obterEdital(idEdital);
      console.log(`📦 Hook useEditalPortugues: Resposta recebida:`, resposta);
      
      if (resposta.success) {
        console.log(`✅ Hook useEditalPortugues: Dados do edital carregados:`, resposta.data);
        setEdital(resposta.data);
        // Verifica a disponibilidade do PDF após carregar o edital
        verificarDisponibilidadePdf(idEdital);
      } else {
        throw new Error(resposta.message || 'Erro ao carregar edital');
      }
    } catch (err) {
      console.error(`❌ Hook useEditalPortugues: Erro ao carregar edital ${idEdital}:`, err);
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      setErro(mensagemErro);
      toast({
        title: "Erro",
        description: mensagemErro,
        variant: "destructive",
      });
    } finally {
      setCarregando(false);
    }
  }, [toast, verificarDisponibilidadePdf]);

  const baixarPdf = useCallback(async (idEdital: number, nomeArquivo?: string) => {
    try {
      // Primeiro verifica se o PDF existe
      const isPdfDisponivel = await verificarDisponibilidadePdf(idEdital);
      
      if (!isPdfDisponivel) {
        toast({
          title: "Indisponível",
          description: "PDF não disponível para este edital.",
          variant: "destructive",
        });
        throw new Error("PDF não disponível para este edital");
      }
      
      toast({
        title: "Processando",
        description: "Preparando o download do PDF...",
      });
      
      await apiEdital.baixarPdf(idEdital.toString(), nomeArquivo);
      
      toast({
        title: "Sucesso",
        description: "PDF baixado com sucesso!",
      });
    } catch (err) {
      if (err instanceof Error && err.message === "PDF não disponível para este edital") {
        // Erro já tratado acima
      } else {
        const mensagemErro = err instanceof Error ? err.message : 'Erro ao baixar PDF';
        toast({
          title: "Erro",
          description: mensagemErro,
          variant: "destructive",
        });
      }
      throw err; // Repassar o erro para que o componente que chamou saiba que houve falha
    }
  }, [toast, verificarDisponibilidadePdf]);

  useEffect(() => {
    if (id) {
      buscarEdital(id);
    }
  }, [id, buscarEdital]);

  return {
    edital,
    carregando,
    erro,
    buscarEdital,
    baixarPdf,
    pdfDisponivel,
    verificandoPdf,
    verificarDisponibilidadePdf
  };
};

/**
 * Hook para obter enumerações de editais
 */
export const useEnumsEdital = () => {
  const [enums, setEnums] = useState<EditalEnums | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const { toast } = useToast();

  const buscarEnums = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    
    try {
      const resposta = await apiEdital.obterEnums();
      
      if (resposta.success) {
        setEnums(resposta.data);
      } else {
        throw new Error(resposta.message || 'Erro ao carregar opções de filtro');
      }
    } catch (err) {
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      setErro(mensagemErro);
      toast({
        title: "Erro",
        description: mensagemErro,
        variant: "destructive",
      });
    } finally {
      setCarregando(false);
    }
  }, [toast]);

  useEffect(() => {
    buscarEnums();
  }, [buscarEnums]);

  return {
    enums,
    carregando,
    erro,
    recarregar: buscarEnums,
  };
};

/**
 * Hook para operações de mutação de editais
 */
export const useMutacoesEdital = () => {
  const { toast } = useToast();

  const criarEdital = useCallback(async (dados: EditalCreateData): Promise<Edital | null> => {
    try {
      const resposta = await apiEdital.criarEdital(dados);
      
      if (resposta.success) {
        toast({
          title: "Sucesso",
          description: "Edital criado com sucesso!",
        });
        return resposta.data;
      } else {
        throw new Error(resposta.message || 'Erro ao criar edital');
      }
    } catch (err) {
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: mensagemErro,
        variant: "destructive",
      });
      return null;
    }
  }, [toast]);

  const atualizarEdital = useCallback(async (id: number, dados: EditalUpdateData): Promise<Edital | null> => {
    try {
      const resposta = await apiEdital.atualizarEdital(id, dados);
      
      if (resposta.success) {
        toast({
          title: "Sucesso",
          description: "Edital atualizado com sucesso!",
        });
        return resposta.data;
      } else {
        throw new Error(resposta.message || 'Erro ao atualizar edital');
      }
    } catch (err) {
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: mensagemErro,
        variant: "destructive",
      });
      return null;
    }
  }, [toast]);

  const atualizarPdf = useCallback(async (id: number, arquivo: File): Promise<Edital | null> => {
    try {
      const resposta = await apiEdital.atualizarPdf(id, arquivo);
      
      if (resposta.success) {
        toast({
          title: "Sucesso",
          description: "PDF atualizado com sucesso!",
        });
        return resposta.data;
      } else {
        throw new Error(resposta.message || 'Erro ao atualizar PDF');
      }
    } catch (err) {
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: mensagemErro,
        variant: "destructive",
      });
      return null;
    }
  }, [toast]);

  const deletarEdital = useCallback(async (id: number): Promise<boolean> => {
    if (!confirm('Tem certeza que deseja deletar este edital? Esta ação não pode ser desfeita.')) {
      return false;
    }

    try {
      const resposta = await apiEdital.deletarEdital(id);
      
      if (resposta.success) {
        toast({
          title: "Sucesso",
          description: "Edital deletado com sucesso!",
        });
        return true;
      } else {
        throw new Error(resposta.message || 'Erro ao deletar edital');
      }
    } catch (err) {
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: mensagemErro,
        variant: "destructive",
      });
      return false;
    }
  }, [toast]);

  return {
    criarEdital,
    atualizarEdital,
    atualizarPdf,
    deletarEdital,
  };
};
