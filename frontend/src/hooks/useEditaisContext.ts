import { useContext } from 'react';
import { EditaisContext } from '../contexts/EditaisContextCreator';

export const useEditaisContext = () => {
  const context = useContext(EditaisContext);
  if (!context) {
    throw new Error('useEditaisContext deve ser usado dentro de EditaisProvider');
  }
  return context;
};
