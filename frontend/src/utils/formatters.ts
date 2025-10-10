/**
 * Utilitários de Formatação Centralizados
 * Funções helper para formatação de dados
 */

/**
 * Verifica se um valor deve ser exibido
 */
export const temValor = (valor: unknown): boolean => {
  if (valor === null || valor === undefined) return false;
  if (typeof valor === 'string' && valor.trim() === '') return false;
  if (typeof valor === 'number' && isNaN(valor)) return false;
  return true;
};

/**
 * Formata um valor ou retorna null
 */
export const formatarValor = (
  valor: unknown,
  formatador?: (v: unknown) => string
): string | null => {
  if (!temValor(valor)) return null;
  return formatador ? formatador(valor) : String(valor);
};

/**
 * Formata valor monetário em BRL
 */
export const formatarMoeda = (valor: number | null | undefined): string | null => {
  if (!temValor(valor)) return null;
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor!);
};

/**
 * Formata percentual
 */
export const formatarPercentual = (valor: number | null | undefined): string | null => {
  if (!temValor(valor)) return null;
  return `${valor}%`;
};

/**
 * Formata valor booleano
 */
export const formatarBooleano = (valor: boolean | null | undefined): string | null => {
  if (valor === null || valor === undefined) return null;
  return valor ? 'Sim' : 'Não';
};

/**
 * Formata data no padrão brasileiro
 */
export const formatarData = (dateString: string | undefined): string | null => {
  if (!dateString) return null;
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
};

/**
 * Formata número com separadores de milhar
 */
export const formatarNumero = (valor: number | null | undefined): string | null => {
  if (!temValor(valor)) return null;
  return new Intl.NumberFormat('pt-BR').format(valor!);
};

/**
 * Trunca texto com reticências
 */
export const truncarTexto = (texto: string, maxLength: number): string => {
  if (texto.length <= maxLength) return texto;
  return texto.substring(0, maxLength) + '...';
};

/**
 * Capitaliza primeira letra de cada palavra
 */
export const capitalizarPalavras = (texto: string): string => {
  return texto
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};
