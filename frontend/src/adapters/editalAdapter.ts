/**
 * Adaptador para converter dados de edital entre frontend e backend
 * 
 * Frontend: campos em português (orgaoResponsavel, valorTotal, etc)
 * Backend: campos em inglês/snake_case (orgao, valor, etc)
 */

import type { Edital } from '../types/edital';

/**
 * Gera slug a partir do título
 */
function generateSlug(titulo: string): string {
  if (!titulo) return '';
  
  return titulo
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove acentos
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Converte edital do backend para o formato do frontend
 * Backend retorna campos diferentes, precisamos adaptar
 */
export function adaptEditalFromBackend(backendData: Record<string, unknown>): Edital {
  const titulo = String(backendData.titulo || backendData.apelido_edital || '');
  const descricao = String(backendData.descricao || backendData.descricao_completa || '');
  const now = new Date().toISOString();
  
  return {
    // ✅ UUID - Identificador principal (mudado de 'id: number' para 'uuid: string')
    uuid: String(backendData.uuid || ''),
    
    // ✅ Informações básicas (REQUIRED)
    apelido_edital: String(backendData.apelido_edital || generateSlug(titulo)),
    link: String(backendData.link || ''),
    descricao_completa: String(backendData.descricao_completa || descricao || ''),
    origem: String(backendData.origem || ''),
    observacoes: backendData.observacoes ? String(backendData.observacoes) : null,
    status: backendData.status ? String(backendData.status) : null,
    
    // ✅ Financiadores (REQUIRED)
    financiador_1: String(backendData.financiador_1 || ''),
    financiador_2: backendData.financiador_2 ? String(backendData.financiador_2) : null,
    
    // ✅ Área e tipo de proponente (REQUIRED)
    area_foco: String(backendData.area_foco || ''),
    tipo_proponente: String(backendData.tipo_proponente || ''),
    empresas_que_podem_submeter: backendData.empresas_que_podem_submeter ? String(backendData.empresas_que_podem_submeter) : null,
    
    // ✅ Duração (REQUIRED - can be null)
    duracao_min_meses: backendData.duracao_min_meses !== undefined ? Number(backendData.duracao_min_meses) : null,
    duracao_max_meses: backendData.duracao_max_meses !== undefined ? Number(backendData.duracao_max_meses) : null,
    
    // ✅ Valores financeiros (REQUIRED - can be null)
    valor_min_R: backendData.valor_min_R !== undefined ? Number(backendData.valor_min_R) : null,
    valor_max_R: backendData.valor_max_R !== undefined ? Number(backendData.valor_max_R) : null,
    tipo_recurso: backendData.tipo_recurso ? String(backendData.tipo_recurso) : null,
    recepcao_recursos: backendData.recepcao_recursos ? String(backendData.recepcao_recursos) : null,
    
    // ✅ Tipos de recurso permitidos (REQUIRED boolean)
    custeio: Boolean(backendData.custeio),
    capital: Boolean(backendData.capital),
    
    // ✅ Contrapartida (REQUIRED - can be null)
    contrapartida_min_pct: backendData.contrapartida_min_pct !== undefined ? Number(backendData.contrapartida_min_pct) : null,
    contrapartida_max_pct: backendData.contrapartida_max_pct !== undefined ? Number(backendData.contrapartida_max_pct) : null,
    tipo_contrapartida: backendData.tipo_contrapartida ? String(backendData.tipo_contrapartida) : null,
    
    // ✅ Datas importantes (REQUIRED)
    data_inicial_submissao: String(backendData.data_inicial_submissao || backendData.data_inicio_submissao || ''),
    data_final_submissao: String(backendData.data_final_submissao || backendData.prazo || ''),
    data_resultado: String(backendData.data_resultado || ''),
    
    // ✅ Timestamps de sistema (REQUIRED)
    created_at: String(backendData.created_at || now),
    updated_at: String(backendData.updated_at || now),
    
    // ⚠️ DEPRECATED: Campos antigos mantidos para retrocompatibilidade
    id: backendData.id ? Number(backendData.id) : undefined,
    titulo,
    descricao,
    descricao_resumida: descricao.substring(0, 200) || '',
    empresa: String(backendData.orgao || backendData.empresa || ''),
    contrapartida: String(backendData.contrapartida || ''),
    cooperacao: String(backendData.cooperacao || ''),
    categoria: String(backendData.categoria || ''),
    apelido: String(backendData.apelido_edital || generateSlug(titulo)),
    tipo_cooperacao: String(backendData.tipo_cooperacao || ''),
    arquivo_nome: String(backendData.arquivo_nome || ''),
    data_inicio_submissao: String(backendData.data_inicial_submissao || backendData.data_inicio_submissao || ''),
    duracao_min: backendData.duracao_min_meses ? Number(backendData.duracao_min_meses) : undefined,
    duracao_max: backendData.duracao_max_meses ? Number(backendData.duracao_max_meses) : undefined,
    valor_min: backendData.valor_min_R ? Number(backendData.valor_min_R) : undefined,
    valor_max: backendData.valor_max_R ? Number(backendData.valor_max_R) : undefined,
    permite_custeio: Boolean(backendData.custeio || backendData.permite_custeio),
    permite_capital: Boolean(backendData.capital || backendData.permite_capital),
    contrapartida_min_percent: backendData.contrapartida_min_pct ? Number(backendData.contrapartida_min_pct) : undefined,
    contrapartida_max_percent: backendData.contrapartida_max_pct ? Number(backendData.contrapartida_max_pct) : undefined,
    empresas_elegiveis: String(backendData.empresas_que_podem_submeter || backendData.empresas_elegiveis || ''),
    imageSrc: String(backendData.imageSrc || ''),
    title: titulo,
    description: descricao.substring(0, 200) || '',
    category: String(backendData.categoria || ''),
    pdfLink: String(backendData.link || ''),
  };
}

/**
 * Converte edital do frontend para o formato do backend
 */
export function adaptEditalToBackend(frontendData: Partial<Edital>): Record<string, unknown> {
  return {
    titulo: frontendData.titulo,
    descricao: frontendData.descricao_completa || frontendData.descricao,
    orgao: frontendData.empresa,
    valor: frontendData.valor_max,
    prazo: frontendData.data_final_submissao,
    link: frontendData.link,
    
    // Campos opcionais que backend pode aceitar
    apelido_edital: frontendData.apelido_edital,
    valor_min_R: frontendData.valor_min,
    valor_max_R: frontendData.valor_max,
    categoria: frontendData.categoria,
    contrapartida: frontendData.contrapartida,
    cooperacao: frontendData.cooperacao,
  };
}

/**
 * Interface para o resultado do match vindo do backend
 */
export interface EditalMatchResult {
  edital_uuid: string;
  edital_name: string;
  match_score: number;
  match_percentage: number;
  reasoning: string;
  compatibility_factors: string[];
  chunks_found: number;
  edital_details?: {
    orgao_responsavel?: string;
    data_inicial_submissao?: string;
    data_final_submissao?: string;
    link?: string;
  };
}

/**
 * Interface para o formato esperado pelo MatchResults.tsx
 */
export interface MatchResultForDisplay {
  id_edital: string;
  id?: number;
  titulo_edital: string;
  titulo?: string;
  orgao_responsavel?: string;
  empresa?: string;
  motivo: string;
  descricao_resumida?: string;
  descricao?: string;
  score: number;
  compatibilityScore?: number;
  data_inicial_submissao?: string;
  data_inicio_submissao?: string;
  data_final_submissao?: string;
  link?: string;
}

/**
 * Adapta resultado do match do backend para o formato esperado pelo frontend
 * Backend retorna: edital_uuid, edital_name, match_score, reasoning, etc
 * Frontend espera: id_edital, titulo_edital, score, motivo, etc
 */
export function adaptMatchResultToDisplay(backendMatch: EditalMatchResult): MatchResultForDisplay {
  return {
    // Identificadores
    id_edital: backendMatch.edital_uuid,
    id: 0, // Não temos ID numérico, usar 0 como placeholder
    
    // Títulos
    titulo_edital: backendMatch.edital_name,
    titulo: backendMatch.edital_name,
    
    // Organização (pode vir em edital_details ou null)
    orgao_responsavel: backendMatch.edital_details?.orgao_responsavel || 'Organização não informada',
    empresa: backendMatch.edital_details?.orgao_responsavel || 'Organização não informada',
    
    // Score e reasoning
    score: backendMatch.match_percentage,
    compatibilityScore: backendMatch.match_percentage,
    motivo: backendMatch.reasoning,
    descricao_resumida: backendMatch.reasoning,
    descricao: backendMatch.reasoning,
    
    // Datas (podem vir em edital_details ou null)
    data_inicial_submissao: backendMatch.edital_details?.data_inicial_submissao,
    data_inicio_submissao: backendMatch.edital_details?.data_inicial_submissao,
    data_final_submissao: backendMatch.edital_details?.data_final_submissao,
    
    // Link
    link: backendMatch.edital_details?.link,
  };
}
