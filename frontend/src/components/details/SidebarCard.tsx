import React, { useState, useEffect } from 'react';
import { Edital } from '../../types/edital';

interface SidebarCardProps {
  edital: Edital;
  onDownload?: () => void;
  downloadEnabled?: boolean;
  pdfChecking?: boolean;
}

const SidebarCard: React.FC<SidebarCardProps> = ({ 
  edital, 
  onDownload,
  downloadEnabled = true,
  pdfChecking = false
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  
  useEffect(() => {
    console.debug('Conteúdo recebido pelo SidebarCard:', { edital, onDownload, downloadEnabled, pdfChecking });
  }, [edital, onDownload, downloadEnabled, pdfChecking]);

  const handleDownload = () => {
    if (onDownload) {
      setIsDownloading(true);
      try {
        onDownload();
        // O estado será resetado após o download ser concluído ou falhar
        // setTimeout para dar tempo para o download começar e a mensagem de sucesso aparecer
        setTimeout(() => setIsDownloading(false), 3000);
      } catch (error) {
        setIsDownloading(false);
      }
    }
  };

  return (
    <aside className="bg-[rgba(217,217,217,0.15)] rounded-[39px] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] sticky top-8">
      {/* Elemento verde superior */}
      <div className="w-full h-[30px] bg-[#DCF763] rounded-t-[39px]" />
      
      
      <div className="p-6 sm:p-8">
        {/* Seção com valores da API */}
        <div className="mb-6">
          <div className="grid grid-cols-2 gap-x-8 gap-y-4 text-sm">
            <div>
              <h4 className="text-[rgba(67,80,88,1)] font-bold mb-2">Contrapartida</h4>
              <div className="text-black font-medium">{edital.contrapartida || 'Não especificado'}</div>
            </div>
            <div>
              <h4 className="text-[rgba(67,80,88,1)] font-bold mb-2">Empresa</h4>
              <div className="text-black font-medium">{edital.empresa || 'Não especificado'}</div>
            </div>
            <div>
              <h4 className="text-[rgba(67,80,88,1)] font-bold mb-2">Cobertura</h4>
              <div className="text-black font-medium">{edital.origem || 'Não especificado'}</div>
            </div>
            <div>
              <h4 className="text-[rgba(67,80,88,1)] font-bold mb-2">Cooperação</h4>
              <div className="text-black font-medium">{edital.cooperacao || 'Não especificado'}</div>
            </div>
          </div>
        </div>

        {/* Linha divisória */}
        <div className="h-px bg-black my-6" />
        
        {/* Temas Transversais */}
        <div className="mb-4">
          <div className="bg-[rgba(0,0,0,0.75)] text-[rgba(248,248,248,1)] font-extrabold rounded-[13px] px-4 py-1 mb-3 text-sm inline-block">
            Temas Transversais
          </div>
          <div className="text-black font-medium text-sm leading-relaxed">
            {edital.area_foco || 'Não especificado'}
          </div>
        </div>
        
        {/* Público-alvo */}
        <div className="mb-4">
          <div className="bg-[rgba(0,0,0,0.75)] text-[rgba(248,248,248,1)] font-extrabold rounded-[13px] px-4 py-1 mb-3 text-sm inline-block">
            Público-alvo
          </div>
          <div className="text-black font-medium text-sm leading-relaxed">
            {edital.empresas_elegiveis || 'Não especificado'}
          </div>
        </div>

        {/* Benefícios desse Edital */}
        <div className="mb-6">
          <div className="bg-[rgba(0,0,0,0.75)] text-[rgba(248,248,248,1)] font-extrabold rounded-[13px] px-4 py-1 mb-3 text-sm inline-block">
            Benefícios desse Edital
          </div>
          <div className="text-black font-medium text-sm leading-relaxed">
            {edital.descricao_completa || edital.descricao || 'Não especificado'}
          </div>
        </div>

        {/* Botão de Download */}
        {edital.link ? (
          <a
            href={edital.link}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full font-extrabold py-3 px-6 rounded-[28px] transition-colors bg-[#DCF763] hover:bg-[#DCF763]/90 text-black text-center block"
            onClick={() => console.debug('Link do PDF clicado:', edital.link)}
          >
            <span>Baixar PDF do Edital</span>
          </a>
        ) : (
          <button 
            className="w-full font-extrabold py-3 px-6 rounded-[28px] bg-gray-300 text-gray-500 cursor-not-allowed"
            disabled
          >
            <span>📄 PDF não disponível</span>
          </button>
        )}
        
        {/* Informação sobre disponibilidade do PDF */}
        {!downloadEnabled && !isDownloading && !pdfChecking && (
          <div className="text-xs text-gray-500 text-center mt-2">
            Este edital não possui PDF para download
          </div>
        )}
        
        {edital.arquivo_nome && (
          <div className="text-xs text-green-600 text-center mt-2">
            ✓ Arquivo: {edital.arquivo_nome}
          </div>
        )}
        
      </div>
    </aside>
  );
};

export default SidebarCard;