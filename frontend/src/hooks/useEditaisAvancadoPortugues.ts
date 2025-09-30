import { useState, useEffect, useCallback } from 'react';
import { Edital, EditalFilters } from '../types/edital';
import { apiEdital } from '../services/apiEdital';

/**
 * Hook avançado para gerenciar editais com mais opções
 * 
 * Nota: Este hook mantém o prefixo "use" para compatibilidade com o React,
 * mas usa o sufixo "Portugues" para indicar que segue as convenções de nomenclatura em português.
 */
export const useEditaisAvancadoPortugues = (filtrosIniciais: EditalFilters = {}) => {
  const [editais, setEditais] = useState<Edital[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [carregandoDetalhes, setCarregandoDetalhes] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [filtros, setFiltros] = useState<EditalFilters>(filtrosIniciais);
  const [totalContagem, setTotalContagem] = useState<number>(0);

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
        setTotalContagem(editaisFiltrados.length);
      } else {
        throw new Error(resposta.message || 'Erro ao carregar editais');
      }
    } catch (err) {
      const mensagemErro = err instanceof Error ? err.message : 'Erro desconhecido';
      setErro(mensagemErro);
      console.error("Erro ao buscar editais:", mensagemErro);
    } finally {
      setCarregando(false);
    }
  }, [filtros]);

  const atualizarFiltros = useCallback((novosFiltros: EditalFilters) => {
    setFiltros(prev => ({...prev, ...novosFiltros}));
  }, []);

  useEffect(() => {
    buscarEditais();
  }, [filtros, buscarEditais]);

  return {
    editais,
    carregando,
    carregandoDetalhes,
    totalContagem,
    erro,
    atualizarFiltros
  };
};
