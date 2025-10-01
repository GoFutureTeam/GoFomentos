import React from 'react';
import { Outlet } from 'react-router-dom';
import { NavegacaoUsuario } from './NavegacaoUsuario';

/**
 * Componente de layout principal que envolve todas as páginas
 * Inclui a navegação e o conteúdo principal
 */
export const LayoutPrincipal: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <NavegacaoUsuario />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
};
