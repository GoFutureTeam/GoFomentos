import TokenService from './tokenService';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';

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

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
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
      
      // Armazena o token usando TokenService (mais seguro)
      TokenService.setTokens(data.access_token, '', true);
      
      // Busca e armazena os dados do usuário
      await this.fetchAndStoreUserData(data.access_token);
      
      return data;
    } catch (error) {
      console.error('Erro no login:', error);
      throw error;
    }
  }

  async register(userData: RegisterRequest): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users`, {
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
      console.error('Erro no registro:', error);
      throw error;
    }
  }

  async fetchAndStoreUserData(token: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/me`, {
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

  async requestPasswordReset(data: PasswordResetRequest): Promise<PasswordResetResponse> {
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
