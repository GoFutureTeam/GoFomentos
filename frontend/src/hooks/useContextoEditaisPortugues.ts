import { useContext } from 'react';
import { EditaisContext } from '../contexts/EditaisContextCreator';
import { EditaisContextValue } from '../contexts/EditaisContextTypes';

/**
 * Hook para acessar o contexto de editais
 * 
 * Nota: Este hook mantém o prefixo "use" para compatibilidade com o React,
 * mas usa o sufixo "Portugues" para indicar que segue as convenções de nomenclatura em português.
 */
export const useContextoEditaisPortugues = (): EditaisContextValue => {
  const context = useContext(EditaisContext);
  
  if (!context) {
    throw new Error('useContextoEditaisPortugues deve ser usado dentro de um EditaisProvider');
  }
  
  return context;
};
