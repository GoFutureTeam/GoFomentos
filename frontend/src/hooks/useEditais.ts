import { useState, useEffect, useCallback } from 'react';
import { Edital, EditalFilters, EditalEnums, EditalCreateData, EditalUpdateData } from '../types/edital';
import { editalApi } from '../services/editalApi';
import { useToast } from './use-toast';

export const useEditais = (initialFilters: EditalFilters = {}) => {
  const [editais, setEditais] = useState<Edital[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<EditalFilters>(initialFilters);
  const { toast } = useToast();

  const fetchEditais = useCallback(async (customFilters?: EditalFilters) => {
    setLoading(true);
    setError(null);
    
    const filtersToUse = customFilters || filters;
    
    try {
      const response = await editalApi.listEditais(filtersToUse);
      
      if (response.success) {
        console.log("Editais recebidos da API:", response.data);
        
        const currentDate = new Date();

        // Filtrar editais com data válida
        const filteredEditais = response.data.filter((edital) => {
          if (!edital.data_final_submissao) {
            console.warn(`Edital sem data de submissão:`, edital);
            return false; // Remove editais sem data de submissão
          }

          const submissionDate = new Date(edital.data_final_submissao);
          return submissionDate >= currentDate; // Mantém apenas editais válidos
        });

        console.log("Editais filtrados:", filteredEditais);
        setEditais(filteredEditais);
      } else {
        throw new Error(response.message || 'Erro ao carregar editais');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [filters, toast]);

  const updateFilters = useCallback((newFilters: EditalFilters) => {
    setFilters(newFilters);
    // Remove execução dupla - o useEffect abaixo já vai executar
  }, []);

  const refetch = useCallback(() => {
    fetchEditais();
  }, [fetchEditais]);

  useEffect(() => {
    fetchEditais();
  }, [filters, fetchEditais]); // Executa sempre que filters muda

  return {
    editais,
    loading,
    error,
    filters,
    updateFilters,
    refetch,
  };
};

export const useEdital = (id?: number) => {
  const [edital, setEdital] = useState<Edital | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pdfAvailable, setPdfAvailable] = useState<boolean | null>(null);
  const [pdfChecking, setPdfChecking] = useState<boolean>(false);
  const { toast } = useToast();

  const checkPdfAvailability = useCallback(async (editalId: number) => {
    try {
      setPdfChecking(true);
      const isPdfAvailable = await editalApi.checkPdfExists(editalId.toString());
      setPdfAvailable(isPdfAvailable);
      return isPdfAvailable;
    } catch (error) {
      console.error("Erro ao verificar disponibilidade do PDF:", error);
      setPdfAvailable(false);
      return false;
    } finally {
      setPdfChecking(false);
    }
  }, []);

  const fetchEdital = useCallback(async (editalId: number) => {
    console.log(`🚀 Hook useEdital: Iniciando busca do edital ID: ${editalId}`);
    setLoading(true);
    setError(null);
    
    try {
      console.log(`📞 Hook useEdital: Chamando editalApi.getEdital(${editalId})`);
      const response = await editalApi.getEdital(editalId);
      console.log(`📦 Hook useEdital: Resposta recebida:`, response);
      
      if (response.success) {
        console.log(`✅ Hook useEdital: Dados do edital carregados:`, response.data);
        setEdital(response.data);
        // Verifica a disponibilidade do PDF após carregar o edital
        checkPdfAvailability(editalId);
      } else {
        throw new Error(response.message || 'Erro ao carregar edital');
      }
    } catch (err) {
      console.error(`❌ Hook useEdital: Erro ao carregar edital ${editalId}:`, err);
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [toast, checkPdfAvailability]);

  const downloadPdf = useCallback(async (editalId: number, filename?: string) => {
    try {
      // Primeiro verifica se o PDF existe
      const isPdfAvailable = await checkPdfAvailability(editalId);
      
      if (!isPdfAvailable) {
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
      
      await editalApi.downloadPdf(editalId.toString(), filename);
      
      toast({
        title: "Sucesso",
        description: "PDF baixado com sucesso!",
      });
    } catch (err) {
      if (err instanceof Error && err.message === "PDF não disponível para este edital") {
        // Erro já tratado acima
      } else {
        const errorMessage = err instanceof Error ? err.message : 'Erro ao baixar PDF';
        toast({
          title: "Erro",
          description: errorMessage,
          variant: "destructive",
        });
      }
      throw err; // Repassar o erro para que o componente que chamou saiba que houve falha
    }
  }, [toast, checkPdfAvailability]);

  useEffect(() => {
    if (id) {
      fetchEdital(id);
    }
  }, [id, fetchEdital]);

  return {
    edital,
    loading,
    error,
    fetchEdital,
    downloadPdf,
    pdfAvailable,
    pdfChecking,
    checkPdfAvailability
  };
};

export const useEditalEnums = () => {
  const [enums, setEnums] = useState<EditalEnums | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchEnums = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await editalApi.getEnums();
      
      if (response.success) {
        setEnums(response.data);
      } else {
        throw new Error(response.message || 'Erro ao carregar opções de filtro');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchEnums();
  }, [fetchEnums]);

  return {
    enums,
    loading,
    error,
    refetch: fetchEnums,
  };
};

export const useEditalMutations = () => {
  const { toast } = useToast();

  const createEdital = useCallback(async (data: EditalCreateData): Promise<Edital | null> => {
    try {
      const response = await editalApi.createEdital(data);
      
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Edital criado com sucesso!",
        });
        return response.data;
      } else {
        throw new Error(response.message || 'Erro ao criar edital');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
      return null;
    }
  }, [toast]);

  const updateEdital = useCallback(async (id: number, data: EditalUpdateData): Promise<Edital | null> => {
    try {
      const response = await editalApi.updateEdital(id, data);
      
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Edital atualizado com sucesso!",
        });
        return response.data;
      } else {
        throw new Error(response.message || 'Erro ao atualizar edital');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
      return null;
    }
  }, [toast]);

  const updatePdf = useCallback(async (id: number, file: File): Promise<Edital | null> => {
    try {
      const response = await editalApi.updatePdf(id, file);
      
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "PDF atualizado com sucesso!",
        });
        return response.data;
      } else {
        throw new Error(response.message || 'Erro ao atualizar PDF');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
      return null;
    }
  }, [toast]);

  const deleteEdital = useCallback(async (id: number): Promise<boolean> => {
    if (!confirm('Tem certeza que deseja deletar este edital? Esta ação não pode ser desfeita.')) {
      return false;
    }

    try {
      const response = await editalApi.deleteEdital(id);
      
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Edital deletado com sucesso!",
        });
        return true;
      } else {
        throw new Error(response.message || 'Erro ao deletar edital');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
      return false;
    }
  }, [toast]);

  return {
    createEdital,
    updateEdital,
    updatePdf,
    deleteEdital,
  };
};