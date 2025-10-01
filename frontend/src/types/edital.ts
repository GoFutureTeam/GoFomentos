// Interfaces para tipos de dados dos editais
export interface Edital {
  id: number;
  titulo: string;
  descricao: string;
  descricao_resumida: string;
  descricao_completa?: string;
  empresa: string;
  contrapartida: string;
  cooperacao: string;
  categoria: string;
  area_foco?: string;
  apelido?: string;
  apelido_edital?: string;
  tipo_proponente?: string;
  tipo_contrapartida?: string;
  tipo_cooperacao?: string;
  arquivo_nome?: string; // Adicionando a propriedade opcional para o nome do arquivo
  origem?: string;
  data_inicio_submissao?: string;
  data_fim_submissao?: string;
  data_resultado?: string;
  financiador_1?: string;
  financiador_2?: string;
  observacoes?: string;
  empresas_elegiveis?: string;
  link?: string;
  tipo_recurso?: string;
  created_at: string;
  updated_at: string;
  // Campos financeiros e de duração
  duracao_min_meses?: number;
  duracao_max_meses?: number;
  valor_min?: number;
  valor_max?: number;
  recepcao_recursos?: string;
  permite_custeio?: boolean;
  permite_capital?: boolean;
  contrapartida_min_percent?: number;
  contrapartida_max_percent?: number;
  // Campos adicionais para compatibilidade com componentes existentes
  imageSrc?: string;
  title?: string;
  description?: string;
  category?: string;
  pdfLink?: string; // Adicionando a propriedade opcional para o link do PDF
}

export interface EditalCreateData {
  titulo: string;
  descricao: string;
  empresa: string;
  contrapartida: string;
  cooperacao: string;
  categoria: string;
  apelido?: string;
  arquivo: File;
}

export interface EditalFilters {
  categoria?: string;
  empresa?: string;
  contrapartida?: string;
  tipo_recurso?: string;
  financiador?: string;
  search?: string;
  page?: number;
  limit?: number;
}

export interface EditalEnums {
  categorias: string[];
  empresas: string[];
  contrapartidas: string[];
  cooperacoes: string[];
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  status: number;
}

export interface EditalUpdateData {
  apelido: string;
}