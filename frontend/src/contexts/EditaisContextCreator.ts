import { createContext } from 'react';
import { EditaisContextValue } from './EditaisContextTypes';

// Create the context
export const EditaisContext = createContext<EditaisContextValue | undefined>(undefined);
