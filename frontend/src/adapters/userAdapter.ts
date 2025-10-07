/**
 * Adaptador para converter dados de usuário entre frontend e backend
 * 
 * Frontend usa português: { nome, sobrenome, senha }
 * Backend usa inglês: { name, password }
 */

export interface UserRegisterFrontend {
  nome: string;
  sobrenome: string;
  email: string;
  senha: string;
  tipo_usuario?: string;
}

export interface UserRegisterBackend {
  name: string;
  email: string;
  password: string;
}

export interface UserLoginFrontend {
  email: string;
  senha: string;
}

export interface UserLoginBackend {
  email: string;
  password: string;
}

/**
 * Converte dados de registro do frontend para o backend
 * Frontend: { nome, sobrenome, email, senha, tipo_usuario }
 * Backend: { name, email, password }
 */
export function adaptUserRegisterToBackend(
  frontendData: UserRegisterFrontend
): UserRegisterBackend {
  return {
    name: `${frontendData.nome} ${frontendData.sobrenome}`.trim(),
    email: frontendData.email,
    password: frontendData.senha,
    // tipo_usuario não é enviado - backend não tem esse campo
  };
}

/**
 * Converte dados de login do frontend para o backend
 * Frontend: { email, senha }
 * Backend: { email, password }
 */
export function adaptUserLoginToBackend(
  frontendData: UserLoginFrontend
): UserLoginBackend {
  return {
    email: frontendData.email,
    password: frontendData.senha,
  };
}

/**
 * Converte resposta de login do backend para o frontend
 */
export function adaptUserLoginFromBackend(backendData: Record<string, unknown>): {
  access_token: string;
  token_type: string;
  user: Record<string, unknown> | null;
} {
  return {
    access_token: String(backendData.access_token || ''),
    token_type: String(backendData.token_type || 'bearer'),
    user: (backendData.user as Record<string, unknown>) || null,
  };
}

/**
 * Converte dados de usuário do backend para o frontend
 * Útil para informações de perfil
 */
export function adaptUserFromBackend(backendData: Record<string, unknown> | null): Record<string, unknown> | null {
  if (!backendData) return null;
  
  const name = String(backendData.name || '');
  const nameParts = name.split(' ');

  return {
    id: backendData.id || backendData._id,
    nome: nameParts[0] || '',
    sobrenome: nameParts.slice(1).join(' ') || '',
    email: backendData.email,
    createdAt: backendData.created_at,
    updatedAt: backendData.updated_at,
  };
}
