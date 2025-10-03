import React, { createContext, useState, ReactNode } from 'react';

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
 * Provedor de autenticação para gerenciar o estado de autenticação global
 */
export const ProvedorAutenticacao = ({ children }: { children: ReactNode }) => {
  // Estado para controlar se o usuário está autenticado
  const [autenticado, setAutenticado] = useState<boolean>(() => !!localStorage.getItem('auth_token'));
  
  // Estado para armazenar os dados do usuário
  const [usuario, setUsuario] = useState<Usuario | null>(() => {
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
