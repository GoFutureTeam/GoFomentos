import React from 'react';
import { Link } from 'react-router-dom';
import { CompatibilityBadge } from './CompatibilityBadge';
interface MatchedEditalCardProps {
  id: number;
  title: string;
  organization: string;
  description: string;
  openingDate: string;
  closingDate: string;
  compatibilityScore: number;
  headerImage: string;
  externalLink?: string;
}
export const MatchedEditalCard: React.FC<MatchedEditalCardProps> = ({
  id,
  title,
  organization,
  description,
  openingDate,
  closingDate,
  compatibilityScore,
  headerImage,
  externalLink
}) => {
  // Função para formatar data no padrão brasileiro
  const formatDate = (dateString: string) => {
    if (!dateString || dateString === 'Data não disponível') return 'Data não disponível';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  return <article className="bg-white shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] pb-[46px] rounded-[39px] max-md:max-w-full">
      {/* Header Image */}
      <div className="w-full h-[23px] bg-[#DCF763] rounded-t-[39px] -mx-0"></div>
      
      <div className="flex w-full flex-col items-stretch mt-[45px] px-[65px] max-md:mt-10 max-md:px-5">
        {/* Header with title and compatibility badge */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-gray-800 mb-2">
              {title}
            </h3>
            <p className="text-lg text-gray-600 font-medium">
              {organization}
            </p>
          </div>
          <CompatibilityBadge percentage={compatibilityScore} />
        </div>
        
        {/* Divider */}
        <hr className="border-gray-300 my-6" />
        
        {/* Content section */}
        <div className="flex gap-8 items-start">
          <div className="flex-1">
            <p className="text-gray-700 text-base mb-6 leading-relaxed">
              {description}
            </p>
            
            {/* Dates */}
            <div className="flex gap-8 text-sm text-gray-600">
              <div>
                <span className="font-medium">Abertura:</span> {formatDate(openingDate)}
              </div>
              <div>
                <span className="font-medium">Encerramento:</span> {formatDate(closingDate)}
              </div>
            </div>
          </div>
          
          {/* Details button */}
          {externalLink ? <a href={externalLink} target="_blank" rel="noopener noreferrer" className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold px-8 py-3 rounded-2xl transition-colors whitespace-nowrap">
              Mais detalhes
            </a> : <Link 
              to={`/edital/${id}`} 
              state={{ fromResults: true, editalTitle: title }}
              className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold px-8 py-3 rounded-2xl transition-colors whitespace-nowrap"
            >
              Ver detalhes
            </Link>}
        </div>
      </div>
    </article>;
};