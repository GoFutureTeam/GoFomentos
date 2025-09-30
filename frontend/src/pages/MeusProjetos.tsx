import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useProjetoPortugues } from '@/hooks/useProjetoPortugues';
import CommonHeader from '@/components/CommonHeader';
import Footer from '@/components/details/Footer';
import { Trash2 } from 'lucide-react';

const MeusProjetos: React.FC = () => {
  const { projetos, carregando, excluirProjeto } = useProjetoPortugues();
  const navigate = useNavigate();
  
  const fazerMatch = (projetoId: string) => {
    navigate(`/matchs?projetoId=${projetoId}`);
  };
  
  const criarNovoProjeto = () => {
    navigate('/matchs');
  };
  
  const confirmarExclusao = (projetoId: string, nomeProjeto: string) => {
    if (window.confirm(`Tem certeza que deseja excluir o projeto "${nomeProjeto}"?`)) {
      excluirProjeto(projetoId);
    }
  };
  
  return (
    <div className="overflow-hidden">
      <CommonHeader 
        title="Meus Projetos" 
        description="Gerencie seus projetos e encontre editais compatíveis" 
        showSecondSection={false} 
      />
      
      <div 
        style={{
          backgroundImage: 'url(/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }} 
        className="relative bg-[rgba(220,247,99,0.65)] z-10 flex w-full flex-col items-center py-12 sm:py-16 px-5 lg:px-20 lg:py-[20px]" 
      />
      
      <main className="bg-white flex flex-col items-stretch max-md:max-w-full relative pb-[80px]">
        <header className="text-center pt-[40px]">
          <h2 className="text-[rgba(67,80,88,1)] text-4xl font-extrabold">
            Meus Projetos
          </h2>
          <p className="text-black text-2xl font-medium leading-[30px] mt-3.5 max-md:max-w-full">
            Gerencie seus projetos e faça match com editais disponíveis
          </p>
        </header>

        <div className="flex flex-col relative w-full items-center mt-[40px] px-20 max-md:max-w-full max-md:px-5">
          <div className="relative z-10 w-[900px] max-w-full">
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-[rgba(67,80,88,1)] text-3xl font-extrabold">
                Seus Projetos
              </h3>
              <button 
                onClick={criarNovoProjeto}
                className="bg-[#DCF763] text-black font-semibold px-[24px] py-[16px] rounded-[24px] hover:bg-[#DCF763]/90 transition-colors text-base"
              >
                + Novo Projeto
              </button>
            </div>
            
            {carregando ? (
              <div className="text-center py-12">
                <p className="text-[rgba(67,80,88,1)] font-medium">Carregando projetos...</p>
              </div>
            ) : projetos.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-[rgba(67,80,88,1)] font-medium mb-6 text-xl">
                  Você ainda não tem projetos cadastrados.
                </p>
                <button 
                  onClick={criarNovoProjeto}
                  className="bg-[#DCF763] text-black font-extrabold px-[30px] py-[21px] rounded-[28px] hover:bg-[#DCF763]/90 transition-colors"
                >
                  Cadastrar Meu Primeiro Projeto
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {projetos.map((projeto) => (
                  <div
                    key={projeto.id}
                    className="bg-white shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] rounded-[39px] overflow-hidden hover:shadow-lg transition-shadow"
                  >
                    <div className="w-full h-[23px] bg-[#DCF763]"></div>
                    <div className="p-6">
                      <h4 className="font-bold text-2xl text-[rgba(67,80,88,1)] mb-3">
                        {projeto.nomeProjeto}
                      </h4>
                      <p className="text-base text-[rgba(67,80,88,1)] mb-4 line-clamp-3">
                        {projeto.descricao}
                      </p>
                      <div className="flex items-center justify-between gap-2 flex-wrap mt-6">
                        <span className="text-sm text-[rgba(67,80,88,1)] font-medium">
                          {projeto.areaProjeto || 'Geral'}
                        </span>
                        <div className="flex gap-3 items-center">
                          <button
                            onClick={() => confirmarExclusao(projeto.id!, projeto.nomeProjeto)}
                            className="group relative bg-red-500 text-white p-2.5 rounded-full hover:bg-red-600 transition-colors"
                            title="Excluir"
                          >
                            <Trash2 size={18} />
                            <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                              Excluir
                            </span>
                          </button>
                          <button
                            onClick={() => fazerMatch(projeto.id!)}
                            className="bg-[#DCF763] text-black font-semibold px-5 py-2.5 rounded-[20px] hover:bg-[#DCF763]/90 transition-colors text-sm"
                          >
                            Fazer Match
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default MeusProjetos;
