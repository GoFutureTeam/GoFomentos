import { useState, useEffect, useCallback } from 'react';
import { Edital, EditalFilters } from '../types/edital';
import { editalApi } from '../services/editalApi';
import { useToast } from './use-toast';

export const useEditaisAdvanced = (initialFilters: EditalFilters = {}) => {
  const [editais, setEditais] = useState<Edital[]>([]);
  const [loadingList, setLoadingList] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<EditalFilters>(initialFilters);
  const [loadedCount, setLoadedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const { toast } = useToast();

  const fetchEditaisAdvanced = useCallback(async (customFilters?: EditalFilters) => {
    setLoadingList(true);
    setLoadingDetails(false);
    setError(null);
    setEditais([]);
    setLoadedCount(0);
    setTotalCount(0);
    
    try {
      const filtersToUse = customFilters || filters;
      
      // Etapa 1: Buscar lista inicial e mostrar imediatamente
      const response = await editalApi.listEditais(filtersToUse);
      
      // console.log('🔧 useEditaisAdvanced - resposta completa da API:', response);
      // console.log('🔧 useEditaisAdvanced - response.data:', response.data);
      // console.log('🔧 useEditaisAdvanced - response.success:', response.success);
      
      if (!response.success) {
        throw new Error(response.message || 'Erro ao carregar lista de editais');
      }

      const basicEditais = response.data;
      
      // Filtrar editais com data de submissão válida
      const currentDate = new Date();
      const filteredEditais = basicEditais.filter((edital) => {
        if (!edital.data_final_submissao) {
          console.warn(`Edital sem data de submissão:`, edital);
          return false; // Remove editais sem data de submissão
        }

        const submissionDate = new Date(edital.data_final_submissao);
        return submissionDate >= currentDate; // Mantém apenas editais válidos
      });
      
      setTotalCount(filteredEditais.length);
      
      // Mostrar editais básicos imediatamente
      // console.log('🔧 useEditaisAdvanced - setEditais chamado com:', filteredEditais.length, filteredEditais);
      setEditais(filteredEditais);
      setLoadedCount(filteredEditais.length);
      setLoadingList(false);
      // console.log('🔧 useEditaisAdvanced - estado após setEditais');
      
      // Etapa 2: Carregar detalhes em background
      setLoadingDetails(true);
      
      // Carregar detalhes em lotes pequenos para não sobrecarregar
      for (let i = 0; i < filteredEditais.length; i += 2) {
        const batch = filteredEditais.slice(i, i + 2);
        
        const batchPromises = batch.map(async (basicEdital, index) => {
          try {
            const detailResponse = await editalApi.getEdital(basicEdital.id);
            return {
              index: i + index,
              edital: detailResponse.success ? detailResponse.data : basicEdital
            };
          } catch (err) {
            console.warn(`Erro ao carregar detalhes do edital ${basicEdital.id}:`, err);
            return {
              index: i + index,
              edital: basicEdital
            };
          }
        });

        const batchResults = await Promise.all(batchPromises);
        
        // Atualizar editais individuais conforme detalhes carregam
        setEditais(current => {
          const updated = [...current];
          batchResults.forEach(({ index, edital }) => {
            if (updated[index]) {
              updated[index] = edital;
            }
          });
          return updated;
        });
        
        // Pequeno delay para não sobrecarregar
        if (i + 2 < basicEditais.length) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }

      setLoadingDetails(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      setLoadingList(false);
      setLoadingDetails(false);
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
    }
  }, [toast, filters]);

  const updateFilters = useCallback((newFilters: EditalFilters) => {
    setFilters(newFilters);
    fetchEditaisAdvanced(newFilters);
  }, [fetchEditaisAdvanced]);

  const refetch = useCallback(() => {
    fetchEditaisAdvanced(filters);
  }, [fetchEditaisAdvanced, filters]);

  useEffect(() => {
    // Adicionar um delay para evitar múltiplas chamadas simultâneas
    const timeoutId = setTimeout(() => {
      fetchEditaisAdvanced(filters);
    }, 100);
    
    return () => clearTimeout(timeoutId);
  }, [fetchEditaisAdvanced, filters]);

  // console.log('🔧 useEditaisAdvanced - return:', {
  //   editaisLength: editais?.length,
  //   editais: editais,
  //   loadingList,
  //   loadingDetails,
  //   error,
  //   totalCount
  // });

  return {
    editais,
    loadingList,
    loadingDetails,
    error,
    filters,
    updateFilters,
    refetch,
    loadedCount,
    totalCount,
    isLoading: loadingList
  };
};