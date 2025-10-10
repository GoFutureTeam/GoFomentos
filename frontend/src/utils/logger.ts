/**
 * Sistema de Logger Condicional
 * Apenas loga em ambiente de desenvolvimento
 */

const isDevelopment = import.meta.env.DEV;

export const logger = {
  /**
   * Log normal - apenas em desenvolvimento
   */
  log: (...args: unknown[]): void => {
    if (isDevelopment) {
      console.log(...args);
    }
  },

  /**
   * Log de erro - apenas em desenvolvimento
   */
  error: (...args: unknown[]): void => {
    if (isDevelopment) {
      console.error(...args);
    }
  },

  /**
   * Log de aviso - apenas em desenvolvimento
   */
  warn: (...args: unknown[]): void => {
    if (isDevelopment) {
      console.warn(...args);
    }
  },

  /**
   * Log de informação - apenas em desenvolvimento
   */
  info: (...args: unknown[]): void => {
    if (isDevelopment) {
      console.info(...args);
    }
  },

  /**
   * Log de debug - apenas em desenvolvimento
   */
  debug: (...args: unknown[]): void => {
    if (isDevelopment) {
      console.debug(...args);
    }
  },
};

export default logger;
