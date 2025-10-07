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
  const titulo = String(backendData.titulo || '');
  const descricao = String(backendData.descricao || '');
  const now = new Date().toISOString();
  
  return {
    // IDs
    id: Number(backendData.id || 0),
    
    // Campos básicos
    titulo,
    descricao,
    descricao_resumida: descricao.substring(0, 200) || '',
    descricao_completa: descricao || String(backendData.descricao_completa || ''),
    
    // Órgão/Empresa
    empresa: String(backendData.orgao || backendData.empresa || ''),
    
    // Campos obrigatórios
    contrapartida: String(backendData.contrapartida || ''),
    cooperacao: String(backendData.cooperacao || ''),
    categoria: String(backendData.categoria || ''),
    
    // Campos opcionais
    area_foco: String(backendData.area_foco || ''),
    apelido: String(backendData.apelido_edital || generateSlug(titulo)),
    apelido_edital: String(backendData.apelido_edital || generateSlug(titulo)),
    tipo_proponente: String(backendData.tipo_proponente || ''),
    tipo_contrapartida: String(backendData.tipo_contrapartida || ''),
    tipo_cooperacao: String(backendData.tipo_cooperacao || ''),
    arquivo_nome: String(backendData.arquivo_nome || ''),
    origem: String(backendData.origem || ''),
    
    // Datas - backend pode não ter, usar defaults
    data_inicio_submissao: String(backendData.data_inicio_submissao || backendData.data_inicio_inscricoes || ''),
    data_fim_submissao: String(backendData.prazo || backendData.data_fim_submissao || backendData.data_fim_inscricoes || ''),
    data_resultado: String(backendData.data_resultado || ''),
    
    // Financiadores
    financiador_1: String(backendData.financiador_1 || ''),
    financiador_2: String(backendData.financiador_2 || ''),
    
    // Observações e elegibilidade
    observacoes: String(backendData.observacoes || ''),
    empresas_elegiveis: String(backendData.empresas_elegiveis || ''),
    
    // Links
    link: String(backendData.link || ''),
    tipo_recurso: String(backendData.tipo_recurso || ''),
    
    // Timestamps
    created_at: String(backendData.created_at || now),
    updated_at: String(backendData.updated_at || now),
    
    // Campos financeiros e de duração
    duracao_min_meses: backendData.duracao_min_meses ? Number(backendData.duracao_min_meses) : undefined,
    duracao_max_meses: backendData.duracao_max_meses ? Number(backendData.duracao_max_meses) : undefined,
    valor_min: backendData.valor_min || backendData.valor_min_R ? Number(backendData.valor_min || backendData.valor_min_R) : undefined,
    valor_max: backendData.valor_max || backendData.valor_max_R || backendData.valor ? Number(backendData.valor_max || backendData.valor_max_R || backendData.valor) : undefined,
    recepcao_recursos: String(backendData.recepcao_recursos || ''),
    permite_custeio: Boolean(backendData.permite_custeio),
    permite_capital: Boolean(backendData.permite_capital),
    contrapartida_min_percent: backendData.contrapartida_min_percent ? Number(backendData.contrapartida_min_percent) : undefined,
    contrapartida_max_percent: backendData.contrapartida_max_percent ? Number(backendData.contrapartida_max_percent) : undefined,
    
    // Campos para compatibilidade com componentes
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
    prazo: frontendData.data_fim_submissao,
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
