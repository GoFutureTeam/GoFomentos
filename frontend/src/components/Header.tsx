import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAutenticacaoPortugues } from "@/hooks/useAutenticacaoPortugues";
import { LogOut } from "lucide-react";

const Header = () => {
  const [logoLoaded, setLogoLoaded] = useState(false);
  const [logoError, setLogoError] = useState(false);
  const { autenticado, sair } = useAutenticacaoPortugues();
  const navigate = useNavigate();

  const handleLogout = () => {
    sair();
    navigate('/');
  };

  return (
    <header className="bg-[rgba(67,80,88,1)] z-10 flex w-full flex-col px-5 lg:px-20 pt-3">
      <nav className="flex w-full max-w-[1283px] mx-auto items-center gap-5 text-neutral-100 flex-wrap justify-between py-4">
        <a href="/" className="relative">
          {/* Fallback se erro no carregamento */}
          {logoError && (
            <div className="flex items-center justify-center text-white text-lg font-bold">
              gofomentos
            </div>
          )}

          {/* Logo principal */}
          <img
            src="/src/assets/logo/logo.svg"
            alt="GoFomentosLogo"
            className="h-8 object-contain"
            loading="eager"
            decoding="sync"
            onLoad={() => setLogoLoaded(true)}
            onError={() => setLogoError(true)}
          />
        </a>
        <div className="flex items-center gap-3 sm:gap-4 lg:gap-6 text-base sm:text-lg font-medium">
          <a
            href="/"
            className="hover:opacity-80 transition-opacity whitespace-nowrap"
          >
            Inicio
          </a>
          <a
            href="/"
            className="hover:opacity-80 transition-opacity whitespace-nowrap"
          >
            Editais
          </a>
          <a
            href="/matchs"
            className="hover:opacity-80 transition-opacity whitespace-nowrap"
          >
            Matchs
          </a>
          <a
            href="/meus-projetos"
            className="hover:opacity-80 transition-opacity whitespace-nowrap"
          >
            Meus Projetos
          </a>
          <a
            href="#footer"
            onClick={(e) => {
              e.preventDefault();
              const footer = document.querySelector('footer');
              if (footer) {
                footer.scrollIntoView({ behavior: 'smooth' });
              }
            }}
            className="hover:opacity-80 transition-opacity whitespace-nowrap cursor-pointer"
          >
            Contato
          </a>
          <button
            onClick={handleLogout}
            className="group relative hover:opacity-80 transition-opacity bg-transparent border-none cursor-pointer text-neutral-100 p-1"
            title="Logout"
          >
            <LogOut size={20} />
            <span className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
              Logout
            </span>
          </button>
        </div>
      </nav>
    </header>
  );
};
export default Header;
