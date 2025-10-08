import React from 'react';
import { Link } from 'react-router-dom';

interface EditalCardProps {
  id: string; // Changed from number to string (UUID)
  area?: string;
  nome?: string;
  tipoProponente?: string;
  origem?: string;
  dataFinalSubmissao: string;
  objetivoEdital?: string;
}

const EditalCard: React.FC<EditalCardProps> = ({
  id,
  area,
  nome,
  tipoProponente,
  origem,
  dataFinalSubmissao,
  objetivoEdital
}) => {
  return (
    <Link to={`/edital/${id}`} className="block">
      <article className="bg-[rgba(217,217,217,0.15)] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] w-full pb-6 sm:pb-[41px] rounded-[39px] hover:shadow-[0px_6px_8px_4px_rgba(0,0,0,0.3)] transition-shadow cursor-pointer relative overflow-hidden min-h-[400px] flex flex-col">
        <div className="bg-[#DCF763] h-[15px] w-full rounded-t-[39px]"></div>
        <div className="flex w-full flex-col p-6 flex-grow">
          {area && (
            <div className="bg-[rgba(67,80,88,1)] flex flex-col items-stretch text-sm sm:text-[15px] text-neutral-50 font-extrabold justify-center px-3 py-1.5 rounded-[13px] w-fit">
              <span>Edital voltado para {area}</span>
            </div>
          )}
          {nome && (
            <h3 
              className="text-[rgba(67,80,88,1)] text-lg sm:text-[22px] font-extrabold mt-6 sm:mt-[31px] leading-tight line-clamp-3"
              title={nome}
            >
              {nome}
            </h3>
          )}
          {objetivoEdital && (
            <p className="text-gray-600 text-sm mt-3 leading-relaxed overflow-hidden" style={{
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical'
            }}>
              {objetivoEdital}
            </p>
          )}
          <hr className="shadow-[0px_4px_4px_rgba(0,0,0,0.25)] border border-black border-solid mt-6 sm:mt-[38px]" />
          <div className="flex flex-col gap-4 mt-4">
            {tipoProponente && (
              <div className="flex flex-col items-stretch">
                <span className="text-[rgba(67,80,88,1)] text-sm sm:text-base font-extrabold">
                  Tipo Proponente
                </span>
                <span className="text-black text-sm sm:text-[15px] font-medium mt-1 sm:mt-2.5 capitalize">
                  {tipoProponente.toLowerCase()}
                </span>
              </div>
            )}
            {origem && (
              <div className="flex flex-col">
                <span className="text-[rgba(67,80,88,1)] text-sm sm:text-base font-extrabold">
                  Origem
                </span>
                <div className="text-black text-sm sm:text-[15px] font-medium mt-1 sm:mt-[11px] capitalize">
                  {origem.toLowerCase()}
                </div>
              </div>
            )}
            <div className="flex flex-col items-stretch">
              <span className="text-[rgba(67,80,88,1)] text-sm sm:text-base font-extrabold">
                Data Final de Submissão
              </span>
              <span className="text-black text-sm sm:text-[15px] font-medium mt-1 sm:mt-[9px]">
                {dataFinalSubmissao}
              </span>
            </div>
          </div>
        </div>
      </article>
    </Link>
  );
};

export default EditalCard;
