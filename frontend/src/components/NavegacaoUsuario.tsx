import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

/**
 * Componente de navegação para usuários autenticados
 * Exibe opções diferentes dependendo do estado de autenticação do usuário
 */
export const NavegacaoUsuario: React.FC = () => {
  const { autenticado, usuario, sair } = useAutenticacaoPortugues();
  const location = useLocation();
  
  // Obter as iniciais do nome do usuário para o avatar
  const obterIniciais = (nome: string) => {
    return nome
      .split(' ')
      .map(n => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };
  
  // Verificar se o link está ativo
  const isLinkAtivo = (path: string) => {
    return location.pathname === path;
  };
  
  // Estilo para links ativos
  const estiloLinkAtivo = "font-medium text-black";
  const estiloLinkInativo = "text-gray-600 hover:text-black";
  
  return (
    <nav className="bg-white border-b border-gray-200 py-3 px-4 flex items-center justify-between">
      <div className="flex items-center space-x-8">
        <Link to="/" className="flex items-center">
          <img 
            src="/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png" 
            alt="GoFomentos Logo" 
            className="h-8 w-auto"
          />
          <span className="ml-2 text-xl font-bold text-gray-800">GoFomentos</span>
        </Link>
        
        <div className="hidden md:flex space-x-6">
          <Link 
            to="/" 
            className={`${isLinkAtivo('/') ? estiloLinkAtivo : estiloLinkInativo}`}
          >
            Editais
          </Link>
          <Link 
            to="/matchs" 
            className={`${isLinkAtivo('/matchs') ? estiloLinkAtivo : estiloLinkInativo}`}
          >
            Match
          </Link>
          {autenticado && (
            <Link 
              to="/meus-projetos" 
              className={`${isLinkAtivo('/meus-projetos') ? estiloLinkAtivo : estiloLinkInativo}`}
            >
              Meus Projetos
            </Link>
          )}
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        {autenticado ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar>
                  <AvatarFallback className="bg-[#DCF763] text-black">
                    {usuario?.nome ? obterIniciais(usuario.nome) : 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <span className="font-medium">{usuario?.nome}</span>
                  <span className="text-xs text-gray-500">{usuario?.email}</span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/meus-projetos" className="w-full cursor-pointer">
                  Meus Projetos
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/perfil" className="w-full cursor-pointer">
                  Perfil
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={sair}
                className="text-red-600 cursor-pointer"
              >
                Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <div className="flex items-center space-x-2">
            <Button variant="outline" asChild>
              <Link to="/login">Entrar</Link>
            </Button>
            <Button className="bg-[#DCF763] text-black hover:bg-[#DCF763]/90" asChild>
              <Link to="/registro">Cadastrar</Link>
            </Button>
          </div>
        )}
      </div>
    </nav>
  );
};
