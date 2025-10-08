import React from 'react';
import EditalCard from './EditalCard';
import { Edital } from '../types/edital';
import { Skeleton } from './ui/skeleton';

interface EditalGridProps {
  editais: Edital[];
  currentPage: number;
  itemsPerPage: number;
  isLoadingDetails?: boolean;
  totalCount?: number;
}

const EditalGrid: React.FC<EditalGridProps> = ({ 
  editais, 
  currentPage, 
  itemsPerPage, 
  isLoadingDetails = false,
  totalCount = 0 
}) => {
  
  // Debug logs
  // console.log(' EditalGrid - editais recebidos:', editais?.length, editais);
  // console.log(' EditalGrid - currentPage:', currentPage, 'itemsPerPage:', itemsPerPage);

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Data não informada';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  // Calcular quais editais mostrar na página atual
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentEditais = editais.slice(startIndex, endIndex);
  
  // Se ainda está carregando e temos menos editais que o esperado, mostrar skeletons
  const missingCards = isLoadingDetails && currentEditais.length < itemsPerPage 
    ? itemsPerPage - currentEditais.length 
    : 0;

  if (editais.length === 0) {
    return (
      <div className="w-full max-w-[1295px] mx-auto px-5 lg:px-0">
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <p className="text-lg text-gray-600">Nenhum edital encontrado para sua busca.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-[1295px] mx-auto px-5 lg:px-0">
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
        {currentEditais.map((edital) => (
          <EditalCard
            key={edital.uuid}
            id={edital.uuid}
            area={edital.area_foco || edital.categoria}
            nome={edital.apelido_edital || edital.titulo}
            tipoProponente={edital.tipo_proponente}
            origem={edital.origem}
            dataFinalSubmissao={formatDate(edital.data_final_submissao || '')}
            objetivoEdital={edital.descricao_completa}
          />
        ))}
        {Array.from({ length: missingCards }).map((_, index) => (
          <div key={`skeleton-${index}`} className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
            <Skeleton className="h-6 w-20" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-16 w-full" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-28" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EditalGrid;