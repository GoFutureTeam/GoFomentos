import { useContext } from 'react';
import { ContextoAutenticacao } from '../contexts/ContextoAutenticacao';

/**
 * Hook para acessar o contexto de autenticação
 * 
 * Nota: Este hook mantém o prefixo "use" para compatibilidade com o React,
 * mas usa o sufixo "Portugues" para indicar que segue as convenções de nomenclatura em português.
 */
export const useAutenticacaoPortugues = () => {
  const contexto = useContext(ContextoAutenticacao);
  if (contexto === undefined) {
    throw new Error('useAutenticacaoPortugues deve ser usado dentro de um ProvedorAutenticacao');
  }
  return contexto;
};
