/**
 * Remove acentos, converte para minúsculas e normaliza string para comparação
 */
export const normalizeString = (str: string): string => {
  if (!str) return '';
  
  return str
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove diacríticos (acentos)
    .trim();
};

/**
 * Verifica se uma string normalizada contém outra string normalizada
 */
export const includesNormalized = (text: string, search: string): boolean => {
  return normalizeString(text).includes(normalizeString(search));
};