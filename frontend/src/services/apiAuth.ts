// import { jwtDecode } from 'jwt-decode'; // Removido - não necessário para o backend atual

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
  name: string;
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
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'auth_user';

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Email ou senha incorretos');
        }
        throw new Error('Erro ao fazer login');
      }

      const data: LoginResponse = await response.json();
      
      // Armazena o token
      this.setToken(data.access_token);
      
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
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error('Email já cadastrado');
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

  setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  getToken(): string | null {
    const token = localStorage.getItem(this.TOKEN_KEY);
    
    if (!token) {
      return null;
    }

    // Comentado - verificação de expiração do token não é necessária para o backend atual
    // if (this.isTokenExpired(token)) {
    //   this.logout();
    //   return null;
    // }

    return token;
  }

  // Comentado - não necessário para o backend atual
  // isTokenExpired(token: string): boolean {
  //   try {
  //     const decoded: DecodedToken = jwtDecode(token);
  //     const currentTime = Date.now() / 1000;
  //     return decoded.exp < currentTime;
  //   } catch (error) {
  //     return true;
  //   }
  // }

  isAuthenticated(): boolean {
    const token = this.getToken();
    return token !== null;
    // Comentado - verificação de expiração
    // return token !== null && !this.isTokenExpired(token);
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
    localStorage.removeItem(this.TOKEN_KEY);
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
