import TokenService from './tokenService';
import { API_ENDPOINTS, buildApiUrl } from './api';
import { 
  adaptUserRegisterToBackend, 
  adaptUserLoginToBackend,
  adaptUserLoginFromBackend,
  type UserRegisterFrontend,
  type UserLoginFrontend
} from '../adapters/userAdapter';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

export interface RegisterRequest {
  email: string;
  name: string;  // Backend espera 'name', não 'nome' e 'sobrenome'
  password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetResponse {
  message: string;
  success: boolean;
}

// interface DecodedToken {
//   sub: string;
//   exp: number;
//   [key: string]: any;
// }

class AuthService {
  private readonly USER_KEY = 'auth_user';

  /**
   * Login de usuário
   * ✅ ADAPTADO: Converte { email, senha } → { email, password }
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      // ✅ Adaptar dados do frontend para o backend
      const backendCredentials = {
        email: credentials.email,
        password: credentials.password,
      };
      
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.AUTH.LOGIN}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendCredentials),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Email ou senha incorretos');
        }
        if (response.status === 422) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Dados de login inválidos');
        }
        throw new Error('Erro ao fazer login');
      }

      const data: LoginResponse = await response.json();
      
      // ✅ Adaptar resposta do backend
      const adaptedData = adaptUserLoginFromBackend(data as unknown as Record<string, unknown>);
      
      // Armazena o token usando TokenService (mais seguro)
      TokenService.setTokens(adaptedData.access_token, '', true);
      
      // Busca e armazena os dados do usuário
      await this.fetchAndStoreUserData(adaptedData.access_token);
      
      return {
        access_token: adaptedData.access_token,
        token_type: adaptedData.token_type,
        user: adaptedData.user as LoginResponse['user']
      };
    } catch (error) {
      console.error('❌ Erro no login:', error);
      throw error;
    }
  }

  /**
   * Registrar novo usuário
   * ✅ ADAPTADO: Converte { name } para o backend
   */
  async register(userData: RegisterRequest): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.AUTH.REGISTER}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          name: userData.name,  // Nome completo
          password: userData.password,
        }),
      });

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error('Email já cadastrado');
        }
        if (response.status === 422) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Dados de registro inválidos. Verifique os campos.');
        }
        throw new Error('Erro ao criar conta');
      }

      const user = await response.json();
      
      // Após registrar, faz login automaticamente
      return await this.login({
        email: userData.email,
        password: userData.password,
      });
    } catch (error) {
      console.error('❌ Erro no registro:', error);
      throw error;
    }
  }

  async fetchAndStoreUserData(token: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.USERS.ME}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        localStorage.setItem(this.USER_KEY, JSON.stringify(userData));
      }
    } catch (error) {
      console.error('Erro ao buscar dados do usuário:', error);
    }
  }

  getToken(): string | null {
    // Usar TokenService que já valida expiração
    return TokenService.getAccessToken();
  }

  isAuthenticated(): boolean {
    // TokenService.getAccessToken() já retorna null se token expirado
    return TokenService.isAccessTokenValid();
  }

  getCurrentUser(): unknown | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  getUserId(): string | null {
    const user = this.getCurrentUser() as { id?: string } | null;
    return user?.id || null;
  }

  logout(): void {
    // Limpar tokens usando TokenService
    TokenService.clearTokens();
    localStorage.removeItem(this.USER_KEY);
  }

  /**
   * ❌ DESABILITADO: Backend não implementa recuperação de senha
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<PasswordResetResponse> {
    console.warn('⚠️ Funcionalidade de recuperação de senha não está implementada no backend');
    throw new Error('Funcionalidade não disponível. Entre em contato com o administrador.');
    
    /* CÓDIGO ORIGINAL COMENTADO - Backend não tem este endpoint
    try {
      const response = await fetch(`${API_BASE_URL}/api/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao solicitar redefinição de senha');
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao solicitar recuperação de senha:', error);
      throw error;
    }
    */
  }
}

export const authService = new AuthService();

export const authApi = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return authService.login(credentials);
  },

  async register(userData: RegisterRequest): Promise<LoginResponse> {
    return authService.register(userData);
  },

  async requestPasswordReset(data: PasswordResetRequest): Promise<PasswordResetResponse> {
    return authService.requestPasswordReset(data);
  }
};

export default authService;
