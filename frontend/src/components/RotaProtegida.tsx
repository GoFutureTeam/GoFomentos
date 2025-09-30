import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';

/**
 * Componente que protege rotas que requerem autenticação
 * Redireciona para a página de login se o usuário não estiver autenticado
 */
const RotaProtegida: React.FC = () => {
  const { autenticado } = useAutenticacaoPortugues();
  
  // Em uma aplicação real, você pode adicionar um estado de 'carregando' aqui
  // para mostrar um spinner enquanto verifica a autenticação
  
  return autenticado ? <Outlet /> : <Navigate to="/login" replace />;
};

export default RotaProtegida;
