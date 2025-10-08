// Interfaces para tipos de dados dos editais
export interface Edital {
  // ✅ Identificadores
  uuid: string;  // Mudado de 'id: number' para 'uuid: string'
  
  // ✅ Informações básicas
  apelido_edital: string;
  link: string;
  descricao_completa: string;
  origem: string;
  observacoes: string | null;
  status: string | null;
  
  // ✅ Financiadores
  financiador_1: string;
  financiador_2: string | null;
  
  // ✅ Área e tipo de proponente
  area_foco: string;
  tipo_proponente: string;
  empresas_que_podem_submeter: string | null;
  
  // ✅ Duração (em meses)
  duracao_min_meses: number | null;
  duracao_max_meses: number | null;
  
  // ✅ Valores financeiros (em Reais)
  valor_min_R: number | null;
  valor_max_R: number | null;
  tipo_recurso: string | null;
  recepcao_recursos: string | null;
  
  // ✅ Tipos de recurso permitidos
  custeio: boolean;
  capital: boolean;
  
  // ✅ Contrapartida (em percentual)
  contrapartida_min_pct: number | null;
  contrapartida_max_pct: number | null;
  tipo_contrapartida: string | null;
  
  // ✅ Datas importantes
  data_inicial_submissao: string;  // ISO 8601: "YYYY-MM-DD"
  data_final_submissao: string;    // ISO 8601: "YYYY-MM-DD"
  data_resultado: string;          // ISO 8601: "YYYY-MM-DD"
  
  // ✅ Timestamps de sistema
  created_at: string;  // ISO 8601: "YYYY-MM-DDTHH:mm:ss.ffffff"
  updated_at: string;  // ISO 8601: "YYYY-MM-DDTHH:mm:ss.ffffff"
  
  // ⚠️ DEPRECATED: Campos antigos mantidos para retrocompatibilidade
  // TODO: Remover após migração completa
  id?: number;
  titulo?: string;
  descricao?: string;
  descricao_resumida?: string;
  empresa?: string;
  contrapartida?: string;
  cooperacao?: string;
  categoria?: string;
  apelido?: string;
  tipo_cooperacao?: string;
  arquivo_nome?: string;
  data_inicio_submissao?: string;
  // data_final_submissao: Now a REQUIRED field above, removed from deprecated
  duracao_min?: number;
  duracao_max?: number;
  valor_min?: number;
  valor_max?: number;
  permite_custeio?: boolean;
  permite_capital?: boolean;
  contrapartida_min_percent?: number;
  contrapartida_max_percent?: number;
  empresas_elegiveis?: string;
  imageSrc?: string;
  title?: string;
  description?: string;
  category?: string;
  pdfLink?: string;
  data_submissao?: string; // Alias para data_final_submissao
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