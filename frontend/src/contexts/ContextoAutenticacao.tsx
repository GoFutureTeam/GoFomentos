import React, { createContext, useState, ReactNode, useEffect } from 'react';

// Interface para o usuário
export interface Usuario {
  id: string;
  nome: string;
  email: string;
}

// Interface para o contexto de autenticação
export interface ValorContextoAutenticacao {
  autenticado: boolean;
  usuario: Usuario | null;
  entrar: (dadosUsuario: Usuario, token: string) => void;
  sair: () => void;
}

// Criação do contexto
export const ContextoAutenticacao = createContext<ValorContextoAutenticacao | undefined>(undefined);

/**
 * Valida se o token JWT é válido e não expirou
 */
const validarToken = (token: string | null): boolean => {
  if (!token) return false;
  
  try {
    // Decodifica o payload do JWT (parte do meio)
    const payload = JSON.parse(atob(token.split('.')[1]));
    
    // Verifica se o token não expirou (exp é em segundos)
    const agora = Math.floor(Date.now() / 1000);
    return payload.exp > agora;
  } catch (erro) {
    console.error('❌ Erro ao validar token:', erro);
    return false;
  }
};

/**
 * Provedor de autenticação para gerenciar o estado de autenticação global
 */
export const ProvedorAutenticacao = ({ children }: { children: ReactNode }) => {
  // Validar token na inicialização
  const tokenInicial = localStorage.getItem('auth_token');
  const tokenValido = validarToken(tokenInicial);
  
  // Se token inválido, limpar localStorage
  if (!tokenValido && tokenInicial) {
    console.warn('⚠️ Token inválido ou expirado, limpando localStorage...');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('usuario');
  }
  
  // Estado para controlar se o usuário está autenticado
  const [autenticado, setAutenticado] = useState<boolean>(tokenValido);
  
  // Estado para armazenar os dados do usuário
  const [usuario, setUsuario] = useState<Usuario | null>(() => {
    if (!tokenValido) return null;
    const usuarioArmazenado = localStorage.getItem('usuario');
    return usuarioArmazenado ? JSON.parse(usuarioArmazenado) : null;
  });

  /**
   * Função para autenticar o usuário
   */
  const entrar = (dadosUsuario: Usuario, token: string) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('usuario', JSON.stringify(dadosUsuario));
    setUsuario(dadosUsuario);
    setAutenticado(true);
  };

  /**
   * Função para deslogar o usuário
   */
  const sair = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('usuario');
    setUsuario(null);
    setAutenticado(false);
  };

  // Verificar token periodicamente (a cada 30 segundos)
  useEffect(() => {
    const intervalo = setInterval(() => {
      const token = localStorage.getItem('auth_token');
      const valido = validarToken(token);
      
      if (!valido && autenticado) {
        console.warn('⚠️ Token expirou, fazendo logout automático...');
        sair();
      }
    }, 30000); // 30 segundos

    return () => clearInterval(intervalo);
  }, [autenticado]);

  // Valor do contexto
  const valor: ValorContextoAutenticacao = {
    autenticado,
    usuario,
    entrar,
    sair
  };

  return (
    <ContextoAutenticacao.Provider value={valor}>
      {children}
    </ContextoAutenticacao.Provider>
  );
};
