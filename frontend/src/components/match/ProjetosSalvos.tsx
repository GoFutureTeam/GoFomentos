import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjetoPortugues } from '@/hooks/useProjetoPortugues';
import { Button } from '@/components/ui/button';

export const ProjetosSalvos: React.FC = () => {
  const { projetos, carregando } = useProjetoPortugues();
  const navigate = useNavigate();

  const handleSelecionarProjeto = (projetoId: string) => {
    const formulario = document.getElementById('formulario-match');
    if (formulario) {
      formulario.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    navigate(`/matchs?projetoId=${projetoId}`, { replace: true });
  };

  if (carregando) {
    return (
      <div className="flex flex-col relative w-full items-center mt-[40px] pb-[40px] px-20 max-md:max-w-full max-md:px-5">
        <div className="relative z-10 w-[900px] max-w-full">
          <div className="bg-white shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] text-xl pb-[32px] rounded-[39px] max-md:max-w-full overflow-hidden">
            <div className="w-full h-[23px] bg-[#DCF763] rounded-t-[39px]"></div>
            <div className="p-6">
              <p className="text-center text-gray-500">Carregando projetos...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (projetos.length === 0) {
    return (
      <div className="flex flex-col relative w-full items-center mt-[40px] pb-[40px] px-20 max-md:max-w-full max-md:px-5">
        <div className="relative z-10 w-[900px] max-w-full">
          <div className="bg-white shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] text-xl pb-[32px] rounded-[39px] max-md:max-w-full overflow-hidden">
            <div className="w-full h-[23px] bg-[#DCF763] rounded-t-[39px]"></div>
            <div className="flex flex-col mt-6 px-[40px] max-md:max-w-full max-md:px-5">
              <div className="text-center">
                <h3 className="text-[rgba(67,80,88,1)] text-2xl font-extrabold mb-2">
                  Nenhum projeto salvo
                </h3>
                <p className="text-[rgba(67,80,88,1)] font-medium mb-4">
                  Você ainda não tem projetos salvos. Crie um novo projeto abaixo para começar!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col relative w-full items-center mt-[40px] pb-[40px] px-20 max-md:max-w-full max-md:px-5">
      <div className="relative z-10 w-[900px] max-w-full">
        <div className="bg-white shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] text-xl pb-[32px] rounded-[39px] max-md:max-w-full overflow-hidden">
          <div className="w-full h-[23px] bg-[#DCF763] rounded-t-[39px]"></div>
          
          <div className="flex flex-col mt-6 px-[40px] max-md:max-w-full max-md:px-5">
            <div className="mb-6">
              <h3 className="text-[rgba(67,80,88,1)] ml-[25px] max-md:ml-2.5 text-3xl font-extrabold mb-2">
                Meus Projetos Salvos
              </h3>
              <p className="text-[rgba(67,80,88,1)] ml-[25px] max-md:ml-2.5 font-medium">
                Selecione um projeto para testar o match com editais disponíveis
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projetos.map((projeto) => (
                <div
                  key={projeto.id}
                  className="bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] p-4 rounded-[25px] hover:shadow-md transition-shadow cursor-pointer border-2 border-transparent hover:border-[#DCF763]"
                  onClick={() => handleSelecionarProjeto(projeto.id!)}
                >
                  <h4 className="font-bold text-lg text-[rgba(67,80,88,1)] mb-2 line-clamp-2">
                    {projeto.nomeProjeto}
                  </h4>
                  <p className="text-sm text-[rgba(67,80,88,1)] mb-3 line-clamp-3">
                    {projeto.descricao}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[rgba(67,80,88,1)] font-medium">
                      {projeto.areaProjeto || 'Geral'}
                    </span>
                    <Button
                      size="sm"
                      className="bg-[#DCF763] text-black hover:bg-[#DCF763]/90 text-xs font-semibold"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelecionarProjeto(projeto.id!);
                      }}
                    >
                      Selecionar
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 text-center">
              <a
                href="/meus-projetos"
                className="text-sm text-[rgba(67,80,88,1)] hover:text-gray-900 underline font-medium"
              >
                Ver todos os projetos
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};