import React from 'react';
import { useParams } from 'react-router-dom';
import CommonHeader from '../components/CommonHeader';
import SidebarCard from '../components/details/SidebarCard';
import ChatInterface from '../components/details/ChatInterface';
import Footer from '../components/details/Footer';
import { useEditalPortugues } from '../hooks/useEditaisPortugues';
import { Skeleton } from '../components/ui/skeleton';
import logger from '../utils/logger';
import {
  temValor,
  formatarValor,
  formatarMoeda,
  formatarPercentual,
  formatarBooleano,
  formatarData,
} from '../utils/formatters';

const EditalDetails = () => {
  const {
    id
  } = useParams<{ id: string }>();
  const editalUuid = id; // URL param 'id' now contains UUID string
  
  logger.log(`🎬 EditalDetails: Componente iniciado com UUID: ${editalUuid}`);
  
  const {
    edital,
    carregando: loading,
    erro: error,
    baixarPdf: downloadPdf,
    pdfDisponivel: pdfAvailable,
    verificandoPdf: pdfChecking
  } = useEditalPortugues(editalUuid);
  
  logger.log(`📋 EditalDetails: Estado atual:`, {
    editalUuid,
    loading,
    error,
    hasEdital: !!edital,
    editalData: edital
  });

  /**
   * ✅ Componente para linha de informação condicional
   */
  const InfoRow = ({ 
    label, 
    value 
  }: { 
    label: string; 
    value: string | null 
  }) => {
    if (!value) return null;
    
    return (
      <p className="text-gray-700 leading-relaxed text-base">
        <strong>{label}:</strong> {value}
      </p>
    );
  };
  
  if (loading) {
    logger.log(`⏳ EditalDetails: Renderizando loading state`);
    return <div className="min-h-screen">`
        <CommonHeader />
        <main className="container mx-auto px-4 py-8">
          <div className="space-y-6">
            <Skeleton className="h-12 w-3/4" />
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-2/3" />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-4">
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-32 w-full" />
              </div>
              <div className="space-y-4">
                <Skeleton className="h-48 w-full" />
              </div>
            </div>
          </div>
        </main>
      </div>;
  }
  if (error || !edital) {
    logger.log(`❌ EditalDetails: Estado de erro ou edital não encontrado:`, { error, edital });
    return <div className="min-h-screen">
        <CommonHeader />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Edital não encontrado</h1>
            <p className="text-muted-foreground">{error || 'O edital solicitado não existe.'}</p>
          </div>
        </main>
      </div>;
  }

  // Função para formatar data no padrão brasileiro
  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  // Função para extrair objetivos do texto de descrição completa
  const extractObjectives = (text: string) => {
    const objectivePatterns = /\b(apoiar|promover|incentivar|fomentar|desenvolver|fortalecer)\b[^.!?]*[.!?]/gi;
    const matches = text.match(objectivePatterns);
    return matches || [];
  };
  const objectives = edital.descricao_completa ? extractObjectives(edital.descricao_completa) : [];

  logger.log(`🎯 EditalDetails: Edital carregado com sucesso:`, {
    uuid: edital.uuid,
    apelido_edital: edital.apelido_edital,
    descricao_completa_length: edital.descricao_completa?.length || 0,
    objectives_found: objectives.length,
    all_fields: Object.keys(edital)
  });

  // Função para download do edital
  const handleDownloadEdital = () => {
    const downloadUrl = `https://api-editais.gofuture.cc/api/v1/editais/${edital.uuid}/download`;
    window.open(downloadUrl, '_blank');
  };
  return <div className="overflow-hidden">
      <CommonHeader title={edital.apelido_edital} description="" showSecondSection={false} />
      

      
      <main>
        <div className="bg-white px-5 lg:px-20 py-12">
          <div className="max-w-[1200px] mx-auto">
            
            <div className="flex gap-8 lg:gap-12 flex-col xl:flex-row">
              <div className="w-full xl:w-[60%] space-y-10">
                
                {/* Seção Objetivo do Edital */}
                {temValor(edital.descricao_completa) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Objetivo do Edital</h2>
                    <p className="text-gray-700 leading-relaxed text-base mb-4">
                      {edital.descricao_completa}
                    </p>
                  </section>
                )}

                {/* Seção Financiadores */}
                {(temValor(edital.financiador_1) || temValor(edital.financiador_2)) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Financiadores</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      <InfoRow 
                        label="Financiador Principal" 
                        value={formatarValor(edital.financiador_1)} 
                      />
                      <InfoRow 
                        label="Financiador Secundário" 
                        value={formatarValor(edital.financiador_2)} 
                      />
                    </div>
                  </section>
                )}

                {/* Seção Áreas de Foco */}
                {temValor(edital.area_foco) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Áreas de Foco</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <ul className="list-disc pl-5 space-y-1">
                        {edital.area_foco.split(',').map((area: string, index: number) => (
                          <li key={index}>{area.trim()}</li>
                        ))}
                      </ul>
                    </div>
                  </section>
                )}

                {/* Seção Tipo de Recurso */}
                {temValor(edital.tipo_recurso) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Tipo de Recurso</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <InfoRow 
                        label="Modalidade de apoio" 
                        value={formatarValor(edital.tipo_recurso)} 
                      />
                    </div>
                  </section>
                )}

                {/* Seção Categoria */}
                {temValor(edital.categoria) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Categoria</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <p>{edital.categoria}</p>
                    </div>
                  </section>
                )}

                {/* Seção Informações Financeiras */}
                {(temValor(edital.valor_min_R) || temValor(edital.valor_max_R) || temValor(edital.duracao_min_meses) || temValor(edital.duracao_max_meses) || temValor(edital.recepcao_recursos) || temValor(edital.custeio) || temValor(edital.capital)) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Informações Financeiras e Prazos</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      <InfoRow 
                        label="Valor Mínimo" 
                        value={formatarMoeda(edital.valor_min_R)} 
                      />
                      <InfoRow 
                        label="Valor Máximo" 
                        value={formatarMoeda(edital.valor_max_R)} 
                      />
                      <InfoRow 
                        label="Duração Mínima" 
                        value={formatarValor(edital.duracao_min_meses, (d) => `${d} meses`)} 
                      />
                      <InfoRow 
                        label="Duração Máxima" 
                        value={formatarValor(edital.duracao_max_meses, (d) => `${d} meses`)} 
                      />
                      <InfoRow 
                        label="Recepção de recursos" 
                        value={formatarValor(edital.recepcao_recursos)} 
                      />
                      <InfoRow 
                        label="Permite custeio" 
                        value={formatarBooleano(edital.custeio)} 
                      />
                      <InfoRow 
                        label="Permite capital" 
                        value={formatarBooleano(edital.capital)} 
                      />
                    </div>
                  </section>
                )}

                {/* Seção Contrapartida */}
                {(temValor(edital.tipo_contrapartida) || temValor(edital.contrapartida_min_pct) || temValor(edital.contrapartida_max_pct)) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Contrapartida</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      <InfoRow 
                        label="Tipo" 
                        value={formatarValor(edital.tipo_contrapartida)} 
                      />
                      <InfoRow 
                        label="Percentual Mínimo" 
                        value={formatarPercentual(edital.contrapartida_min_pct)} 
                      />
                      <InfoRow 
                        label="Percentual Máximo" 
                        value={formatarPercentual(edital.contrapartida_max_pct)} 
                      />
                    </div>
                  </section>
                )}

                {/* Seção Tipo de Proponente e Empresas */}
                {(temValor(edital.tipo_proponente) || temValor(edital.empresas_que_podem_submeter)) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Elegibilidade</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      <InfoRow 
                        label="Tipo de Proponente" 
                        value={formatarValor(edital.tipo_proponente)} 
                      />
                      <InfoRow 
                        label="Empresas que podem submeter" 
                        value={formatarValor(edital.empresas_que_podem_submeter)} 
                      />
                    </div>
                  </section>
                )}

                {/* Seção O que este edital oferece? */}
                {temValor(edital.observacoes) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">O que este edital oferece?</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <p>{edital.observacoes}</p>
                    </div>
                  </section>
                )}

                {/* Seção Quem pode participar e como? */}
                {temValor(edital.empresas_elegiveis) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Quem pode participar?</h2>
                    <div className="text-gray-700 leading-relaxed text-base mb-4">
                      <p>{edital.empresas_elegiveis}</p>
                    </div>
                    {temValor(edital.link) && (
                      <div className="text-gray-700 leading-relaxed text-base">
                        <p>
                          Para mais informações e submissão de propostas, acesse:{' '}
                          <a href={edital.link} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800">
                            {edital.link.includes('.pdf') ? 'documento do edital' : 'plataforma oficial'}
                          </a>
                        </p>
                      </div>
                    )}
                  </section>
                )}

                {/* Seção Cronograma Completo */}
                {(temValor(edital.data_inicial_submissao) || temValor(edital.data_final_submissao) || temValor(edital.data_resultado)) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Cronograma Completo</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      <InfoRow 
                        label="Início das Submissões" 
                        value={formatDate(edital.data_inicial_submissao)} 
                      />
                      <InfoRow 
                        label="Fim das Submissões" 
                        value={formatDate(edital.data_final_submissao)} 
                      />
                      <InfoRow 
                        label="Divulgação do Resultado" 
                        value={formatDate(edital.data_resultado)} 
                      />
                    </div>
                  </section>
                )}

              </div>
              
              <div className="w-full xl:w-[40%] space-y-8">
                <SidebarCard 
                  edital={edital} 
                  onDownload={() => downloadPdf(edital.uuid, edital.arquivo_nome || `edital-${edital.uuid}.pdf`)} 
                  downloadEnabled={pdfAvailable !== false} // Habilita se não verificamos ainda ou se disponível
                  pdfChecking={pdfChecking}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Chat Interface - positioned between main content and footer */}
        <div className="bg-gradient-to-b from-white to-gray-50 px-5 lg:px-20 py-12">
          <div className="max-w-[1200px] mx-auto">
            <ChatInterface />
          </div>
        </div>
      </main>
      
      <Footer />
    </div>;
};
export default EditalDetails;