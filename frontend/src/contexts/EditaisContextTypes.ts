import { Edital } from '../types/edital';
import { ReactNode } from 'react';

// Define filter state structure
export interface FilterState {
  area: string[];
  tipo_recurso: string[];
  contrapartida: string[];
  financiador: string[];
}

// Define the type for filter updates
export interface FilterUpdate {
  search?: string;
  filters?: {
    area?: string[];
    tipo_recurso?: string[];
    contrapartida?: string[];
    financiador?: string[];
  };
  area?: string[];
  tipo_recurso?: string[];
  contrapartida?: string[];
  financiador?: string[];
}

// Define context value interface
export interface EditaisContextValue {
  // Estados
  allEditais: Edital[];
  filteredEditais: Edital[];
  searchQuery: string;
  activeFilters: FilterState;
  isLoading: boolean;
  loadingDetails: boolean;
  totalCount: number;
  error: string | null;
  
  // Ações
  setSearchQuery: (query: string) => void;
  setActiveFilters: (filters: FilterState) => void;
  updateFilters: (newFilters: FilterUpdate) => void;
}

export interface EditaisProviderProps {
  children: ReactNode;
}
