import React, { useState, useMemo, useCallback } from 'react';
import { Edital, EditalFilters } from '../types/edital';
import { useEditaisAvancadoPortugues } from '../hooks/useEditaisAvancadoPortugues';
import { 
  EditaisContextValue,
  FilterState, 
  FilterUpdate, 
  EditaisProviderProps 
} from './EditaisContextTypes';
import { EditaisContext } from './EditaisContextCreator';

export const EditaisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState<FilterState>({
    area: [],
    tipo_recurso: [],
    contrapartida: [],
    financiador: []
  });

  // Hook sem fallback - mostrar erro real se API falhar
  const {
    editais: allEditais,
    carregando: isLoading,
    carregandoDetalhes: loadingDetails,
    totalContagem: totalCount,
    erro: error,
    atualizarFiltros: hookUpdateFilters
  } = useEditaisAvancadoPortugues({});
  
  // Debug logs
  // console.log('🔍 EditaisContext - allEditais:', allEditais?.length, allEditais);
  // console.log('🔍 EditaisContext - isLoading:', isLoading);
  // console.log('🔍 EditaisContext - activeFilters:', activeFilters);

  // Garantir que allEditais seja sempre um array válido
  const safeAllEditais = useMemo(() => {
    return Array.isArray(allEditais) ? allEditais : [];
  }, [allEditais]);

  // Filtrar editais baseado nos filtros ativos e busca (CLIENT-SIDE)
  const filteredEditais = useMemo(() => {
    // console.log('🔍 filteredEditais useMemo - safeAllEditais:', safeAllEditais.length, 'activeFilters:', activeFilters);
    
    if (!safeAllEditais || safeAllEditais.length === 0) {
      // console.log('🔍 filteredEditais - retornando array vazio, nenhum edital disponível');
      return [];
    }

    let filtered = safeAllEditais;

    // Aplicar filtro de busca (otimizado)
    if (searchQuery?.trim()) {
      const query = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(edital => {
        const searchableText = [
          edital.titulo,
          edital.apelido_edital,
          edital.descricao,
          edital.descricao_completa,
          edital.empresa,
          edital.area_foco,
          edital.categoria
        ].filter(Boolean).join(' ').toLowerCase();
        
        return searchableText.includes(query);
      });
    }

    // Aplicar filtros de área (otimizado)
    if (activeFilters.area?.length > 0) {
      filtered = filtered.filter(edital => {
        const editalArea = (edital.area_foco || edital.categoria || '').toLowerCase();
        return activeFilters.area.some(filterAreaId => {
          // Extrair o valor real do ID do filtro (remover prefixo "area-X-")
          const filterValue = filterAreaId.replace(/^area-\d+-/, '').toLowerCase();
          // Normalizar caracteres especiais para comparação
          const normalizedEditalArea = editalArea.replace(/[^a-z0-9]/g, '');
          const normalizedFilterValue = filterValue.replace(/[^a-z0-9]/g, '');
          
          // console.log('🔍 Comparando área:', {
          //   editalArea,
          //   filterAreaId,
          //   filterValue,
          //   normalizedEditalArea,
          //   normalizedFilterValue,
          //   match: normalizedEditalArea.includes(normalizedFilterValue) || normalizedFilterValue.includes(normalizedEditalArea)
          // });
          
          return normalizedEditalArea.includes(normalizedFilterValue) || 
                 normalizedFilterValue.includes(normalizedEditalArea);
        });
      });
    }

    // Aplicar filtros de tipo de recurso (otimizado)
    if (activeFilters.tipo_recurso?.length > 0) {
      filtered = filtered.filter(edital => {
        const editalTipo = (edital.tipo_recurso || '').toLowerCase();
        return activeFilters.tipo_recurso.some(filterTipoId => {
          // Extrair o valor real do ID do filtro (remover prefixo "tipo-X-")
          const filterValue = filterTipoId.replace(/^tipo-\d+-/, '').toLowerCase();
          const normalizedEditalTipo = editalTipo.replace(/[^a-z0-9]/g, '');
          const normalizedFilterValue = filterValue.replace(/[^a-z0-9]/g, '');
          
          return normalizedEditalTipo.includes(normalizedFilterValue) || 
                 normalizedFilterValue.includes(normalizedEditalTipo);
        });
      });
    }

    // Aplicar filtros de contrapartida (otimizado)
    if (activeFilters.contrapartida?.length > 0) {
      filtered = filtered.filter(edital => {
        const editalContrapartida = (edital.tipo_contrapartida || '').toLowerCase();
        return activeFilters.contrapartida.some(filterContrapartidaId => {
          // Extrair o valor real do ID do filtro (remover prefixo "contrapartida-X-")
          const filterValue = filterContrapartidaId.replace(/^contrapartida-\d+-/, '').toLowerCase();
          const normalizedEditalContrapartida = editalContrapartida.replace(/[^a-z0-9]/g, '');
          const normalizedFilterValue = filterValue.replace(/[^a-z0-9]/g, '');
          
          return normalizedEditalContrapartida.includes(normalizedFilterValue) || 
                 normalizedFilterValue.includes(normalizedEditalContrapartida);
        });
      });
    }

    // Aplicar filtros de financiador (otimizado)
    if (activeFilters.financiador?.length > 0) {
      filtered = filtered.filter(edital => {
        const financiadores = [
          edital.financiador_1,
          edital.financiador_2
        ].filter(Boolean).join(' ').toLowerCase();
        
        return activeFilters.financiador.some(filterFinanciadorId => {
          // Extrair o valor real do ID do filtro (remover prefixo "financiador-X-")
          const filterValue = filterFinanciadorId.replace(/^financiador-\d+-/, '').toLowerCase();
          const normalizedFinanciadores = financiadores.replace(/[^a-z0-9]/g, '');
          const normalizedFilterValue = filterValue.replace(/[^a-z0-9]/g, '');
          
          return normalizedFinanciadores.includes(normalizedFilterValue) || 
                 normalizedFilterValue.includes(normalizedFinanciadores);
        });
      });
    }

    // console.log('✨ filteredEditais - resultado final (client-side):', filtered.length, 'de', safeAllEditais.length);
    return filtered;
  }, [safeAllEditais, searchQuery, activeFilters]);

  const updateFilters = useCallback((newFilters: FilterUpdate) => {
    // console.log('🔄 EditaisContext - updateFilters chamado com:', newFilters);
    
    // Atualizar filtros locais (APENAS client-side, sem chamada à API)
    if (newFilters.search !== undefined) {
      setSearchQuery(newFilters.search);
    }
    
    if (newFilters.filters !== undefined) {
      setActiveFilters({
        area: newFilters.filters.area || [],
        tipo_recurso: newFilters.filters.tipo_recurso || [],
        contrapartida: newFilters.filters.contrapartida || [],
        financiador: newFilters.filters.financiador || []
      });
    } else if (newFilters.area !== undefined || 
              newFilters.tipo_recurso !== undefined || 
              newFilters.contrapartida !== undefined || 
              newFilters.financiador !== undefined) {
      // Handle direct filter updates (not wrapped in a filters object)
      setActiveFilters({
        area: newFilters.area || activeFilters.area,
        tipo_recurso: newFilters.tipo_recurso || activeFilters.tipo_recurso,
        contrapartida: newFilters.contrapartida || activeFilters.contrapartida,
        financiador: newFilters.financiador || activeFilters.financiador
      });
    }
    
    // REMOVIDO: Não fazer chamadas à API para cada mudança de filtro
    // A filtragem agora é feita client-side no useMemo filteredEditais
    // console.log('✅ Filtros atualizados client-side, sem reload da API');
  }, [activeFilters]);

  const value: EditaisContextValue = {
    allEditais: safeAllEditais,
    filteredEditais,
    searchQuery,
    activeFilters,
    isLoading,
    loadingDetails,
    totalCount,
    error,
    setSearchQuery,
    setActiveFilters,
    updateFilters
  };
  
  // console.log('🔍 EditaisContext - value final:', {
  //   allEditaisLength: safeAllEditais?.length,
  //   filteredEditaisLength: filteredEditais?.length,
  //   isLoading,
  //   totalCount
  // });

  return (
    <EditaisContext.Provider value={value}>
      {children}
    </EditaisContext.Provider>
  );
};