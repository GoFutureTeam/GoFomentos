/**
 * Adaptador para converter dados de projeto entre frontend e backend
 * 
 * Frontend: campos em português/snake_case
 * Backend: campos em inglês/snake_case
 */

import type { DadosProjeto } from '../services/apiProjeto';

/**
 * Converte projeto do backend para o formato do frontend
 */
export function adaptProjectFromBackend(backendData: Record<string, unknown>): DadosProjeto {
  return {
    id: backendData.id ? String(backendData.id) : undefined,
    titulo_projeto: String(backendData.titulo || backendData.titulo_projeto || ''),
    objetivo_principal: String(backendData.descricao || backendData.objetivo_principal || ''),
    
    // Dados da empresa
    nome_empresa: String(backendData.nome_empresa || ''),
    resumo_atividades: String(backendData.resumo_atividades || ''),
    cnae: String(backendData.cnae || ''),
    
    // Documento
    documento_url: backendData.documento_url ? String(backendData.documento_url) : undefined,
    
    // IDs relacionados
    user_id: backendData.user_id ? String(backendData.user_id) : undefined,
    edital_uuid: backendData.edital_id || backendData.edital_uuid ? String(backendData.edital_id || backendData.edital_uuid) : undefined,
    
    // Metadados
    created_at: backendData.created_at ? String(backendData.created_at) : undefined,
    updated_at: backendData.updated_at ? String(backendData.updated_at) : undefined,
  };
}

/**
 * Converte projeto do frontend para o formato do backend
 */
export function adaptProjectToBackend(frontendData: Partial<DadosProjeto>): Record<string, unknown> {
  return {
    titulo: frontendData.titulo_projeto,
    descricao: frontendData.objetivo_principal,
    nome_empresa: frontendData.nome_empresa,
    resumo_atividades: frontendData.resumo_atividades,
    cnae: frontendData.cnae,
    
    // Campos opcionais
    edital_id: frontendData.edital_uuid,
    documento_url: frontendData.documento_url,
  };
}
