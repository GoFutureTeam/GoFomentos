import React, { createContext, useState, ReactNode, useEffect } from 'react';
import TokenService from '../services/tokenService';
import logger from '@/utils/logger';

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
  entrar: (dadosUsuario: Usuario) => void;
  sair: () => void;
}

// Criação do contexto
export const ContextoAutenticacao = createContext<ValorContextoAutenticacao | undefined>(undefined);

/**
 * Provedor de autenticação para gerenciar o estado de autenticação global
 */
export const ProvedorAutenticacao = ({ children }: { children: ReactNode }) => {
  // Validar token na inicialização usando TokenService
  const tokenInicial = TokenService.getAccessToken();
  const tokenValido = tokenInicial ? !TokenService.isTokenExpired(tokenInicial) : false;
  
  // Se token inválido, limpar tudo
  if (!tokenValido && tokenInicial) {
    logger.warn('⚠️ Token inválido ou expirado, limpando dados...');
    TokenService.clearTokens();
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
   * ✅ Token já é salvo pelo apiAuth.login() via TokenService
   */
  const entrar = (dadosUsuario: Usuario) => {
    localStorage.setItem('usuario', JSON.stringify(dadosUsuario));
    setUsuario(dadosUsuario);
    setAutenticado(true);
  };

  /**
   * Função para deslogar o usuário
   * ✅ Limpa TODOS os tokens e dados do usuário
   */
  const sair = () => {
    TokenService.clearTokens();
    localStorage.removeItem('usuario');
    setUsuario(null);
    setAutenticado(false);
  };

  // Verificar token periodicamente (a cada 30 segundos)
  useEffect(() => {
    const intervalo = setInterval(() => {
      const token = TokenService.getAccessToken();
      const valido = token ? !TokenService.isTokenExpired(token) : false;
      
      if (!valido && autenticado) {
        logger.warn('⚠️ Token expirou, fazendo logout automático...');
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
