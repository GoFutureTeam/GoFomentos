/**
 * Serviço de gerenciamento de tokens
 * 
 * Melhorias de segurança:
 * - Suporta sessionStorage (mais seguro) e localStorage
 * - Valida expiração de tokens
 * - Limpa tokens automaticamente quando expiram
 */

import logger from '@/utils/logger';

interface TokenPayload {
  sub: string; // email do usuário
  exp: number; // timestamp de expiração
  type?: 'access' | 'refresh';
}

class TokenService {
  private static readonly ACCESS_TOKEN_KEY = 'gf_access_token';
  private static readonly REFRESH_TOKEN_KEY = 'gf_refresh_token';
  private static readonly REMEMBER_KEY = 'gf_remember';

  /**
   * Salva tokens (access e refresh)
   * @param remember Se true, usa localStorage; se false, usa sessionStorage
   */
  static setTokens(accessToken: string, refreshToken: string, remember: boolean = false): void {
    const storage = remember ? localStorage : sessionStorage;
    
    storage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    storage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
    
    // Salvar preferência de "lembrar"
    if (remember) {
      localStorage.setItem(this.REMEMBER_KEY, 'true');
    } else {
      localStorage.removeItem(this.REMEMBER_KEY);
    }

    logger.log('✅ Tokens salvos', { remember, storage: remember ? 'localStorage' : 'sessionStorage' });
  }

  /**
   * Recupera access token
   */
  static getAccessToken(): string | null {
    // Tentar localStorage primeiro, depois sessionStorage
    return localStorage.getItem(this.ACCESS_TOKEN_KEY) || 
           sessionStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  /**
   * Recupera refresh token
   */
  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY) || 
           sessionStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Limpa todos os tokens
   */
  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.REMEMBER_KEY);
    
    sessionStorage.removeItem(this.ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(this.REFRESH_TOKEN_KEY);

    logger.log('🗑️ Tokens removidos');
  }

  /**
   * Verifica se token está expirado
   */
  static isTokenExpired(token: string): boolean {
    try {
      const payload = this.decodeToken(token);
      const now = Date.now() / 1000; // Converter para segundos
      
      // Considerar expirado se faltar menos de 30 segundos
      return payload.exp < (now + 30);
    } catch (error) {
      logger.error('❌ Erro ao decodificar token:', error);
      return true;
    }
  }

  /**
   * Decodifica token JWT (apenas payload, não valida assinatura)
   */
  static decodeToken(token: string): TokenPayload {
    try {
      const parts = token.split('.');
      
      if (parts.length !== 3) {
        throw new Error('Token JWT inválido');
      }

      const payload = JSON.parse(atob(parts[1]));
      return payload as TokenPayload;
    } catch (error) {
      throw new Error('Falha ao decodificar token');
    }
  }

  /**
   * Verifica se access token está válido
   */
  static isAccessTokenValid(): boolean {
    const token = this.getAccessToken();
    
    if (!token) {
      return false;
    }

    return !this.isTokenExpired(token);
  }

  /**
   * Obtém informações do usuário do token (sem validar)
   */
  static getUserFromToken(): { email: string } | null {
    const token = this.getAccessToken();
    
    if (!token) {
      return null;
    }

    try {
      const payload = this.decodeToken(token);
      return { email: payload.sub };
    } catch {
      return null;
    }
  }

  /**
   * Verifica se usuário optou por "lembrar"
   */
  static shouldRemember(): boolean {
    return localStorage.getItem(this.REMEMBER_KEY) === 'true';
  }
}

export default TokenService;
