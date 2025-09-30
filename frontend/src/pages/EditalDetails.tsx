import React from 'react';
import { useParams } from 'react-router-dom';
import CommonHeader from '../components/CommonHeader';
import ContentSection from '../components/details/ContentSection';
import SidebarCard from '../components/details/SidebarCard';
import ChatInterface from '../components/details/ChatInterface';
import Footer from '../components/details/Footer';
import { useEditalPortugues } from '../hooks/useEditaisPortugues';
import { Skeleton } from '../components/ui/skeleton';
const EditalDetails = () => {
  const {
    id
  } = useParams<{ id: string }>();
  const editalId = id ? parseInt(id) : undefined;
  
  console.log(`🎬 EditalDetails: Componente iniciado com ID: ${id} (parsed: ${editalId})`);
  
  const {
    edital,
    carregando: loading,
    erro: error,
    baixarPdf: downloadPdf,
    pdfDisponivel: pdfAvailable,
    verificandoPdf: pdfChecking
  } = useEditalPortugues(editalId);
  
  console.log(`📋 EditalDetails: Estado atual:`, {
    editalId,
    loading,
    error,
    hasEdital: !!edital,
    editalData: edital
  });
  
  if (loading) {
    console.log(`⏳ EditalDetails: Renderizando loading state`);
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
    console.log(`❌ EditalDetails: Estado de erro ou edital não encontrado:`, { error, edital });
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
    if (!dateString) return 'Data não informada';
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

  console.log(`🎯 EditalDetails: Edital carregado com sucesso:`, {
    id: edital.id,
    titulo: edital.titulo,
    apelido_edital: edital.apelido_edital,
    descricao_completa_length: edital.descricao_completa?.length || 0,
    objectives_found: objectives.length,
    all_fields: Object.keys(edital)
  });

  // Função para download do edital
  const handleDownloadEdital = () => {
    const downloadUrl = `https://api-editais.gofuture.cc/api/v1/editais/${edital.id}/download`;
    window.open(downloadUrl, '_blank');
  };
  return <div className="overflow-hidden">
      <CommonHeader title={edital.apelido_edital} description="" showSecondSection={false} />
      
      <div style={{
        backgroundImage: 'url(/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }} className="relative bg-[rgba(220,247,99,0.65)] z-10 flex w-full flex-col items-center py-12 sm:py-16 px-5 lg:px-20 lg:py-[20px]" />
      
      <main>
        <div className="bg-white px-5 lg:px-20 py-12">
          <div className="max-w-[1200px] mx-auto">
            
            <div className="flex gap-8 lg:gap-12 flex-col xl:flex-row">
              <div className="w-full xl:w-[60%] space-y-10">
                
                {/* Seção Objetivo do Edital */}
                {edital.descricao_completa && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Objetivo do Edital</h2>
                    <p className="text-gray-700 leading-relaxed text-base mb-4">
                      {edital.descricao_completa}
                    </p>
                    <p className="text-gray-700 leading-relaxed text-base mb-4">
                      Esta chamada representa uma excelente oportunidade para propostas inovadoras que se alinhem com esta visão estratégica. O edital busca fomentar o desenvolvimento de projetos que contribuam significativamente para o avanço do setor, promovendo não apenas a inovação tecnológica, mas também o desenvolvimento sustentável e o impacto social positivo.
                    </p>
                    <p className="text-gray-700 leading-relaxed text-base">
                      As propostas selecionadas receberão não apenas apoio financeiro, mas também orientação técnica especializada e acesso a uma rede de parceiros estratégicos, criando um ecossistema favorável ao sucesso dos projetos aprovados.
                    </p>
                  </section>
                )}

                {/* Seção Financiadores */}
                {(edital.financiador_1 || edital.financiador_2) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Financiadores</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      {edital.financiador_1 && (
                        <p><strong>Financiador Principal:</strong> {edital.financiador_1}</p>
                      )}
                      {edital.financiador_2 && (
                        <p><strong>Financiador Secundário:</strong> {edital.financiador_2}</p>
                      )}
                    </div>
                  </section>
                )}

                {/* Seção Áreas de Foco */}
                {edital.area_foco && (
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
                {edital.tipo_recurso && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Tipo de Recurso</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <p><strong>Modalidade de apoio:</strong> {edital.tipo_recurso}</p>
                    </div>
                  </section>
                )}

                {/* Seção Categoria */}
                {edital.categoria && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Categoria</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <p>{edital.categoria}</p>
                    </div>
                  </section>
                )}

                {/* Seção Informações Financeiras */}
                {(edital.valor_min !== undefined || edital.valor_max !== undefined || edital.duracao_min_meses || edital.duracao_max_meses) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Informações Financeiras e Prazos</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      {(edital.valor_min !== undefined || edital.valor_max !== undefined) && (
                        <p>
                          <strong>Valores:</strong> 
                          {edital.valor_min !== undefined && edital.valor_max !== undefined ? (
                            ` De R$ ${edital.valor_min.toLocaleString('pt-BR')} até R$ ${edital.valor_max.toLocaleString('pt-BR')}`
                          ) : edital.valor_max !== undefined ? (
                            ` Até R$ ${edital.valor_max.toLocaleString('pt-BR')}`
                          ) : (
                            ` A partir de R$ ${edital.valor_min!.toLocaleString('pt-BR')}`
                          )}
                        </p>
                      )}
                      {(edital.duracao_min_meses || edital.duracao_max_meses) && (
                        <p>
                          <strong>Duração do projeto:</strong>
                          {edital.duracao_min_meses && edital.duracao_max_meses ? (
                            ` De ${edital.duracao_min_meses} a ${edital.duracao_max_meses} meses`
                          ) : edital.duracao_max_meses ? (
                            ` Até ${edital.duracao_max_meses} meses`
                          ) : (
                            ` Mínimo de ${edital.duracao_min_meses} meses`
                          )}
                        </p>
                      )}
                      {edital.recepcao_recursos && (
                        <p><strong>Recepção de recursos:</strong> {edital.recepcao_recursos}</p>
                      )}
                      {edital.permite_custeio !== undefined && (
                        <p><strong>Permite custeio:</strong> {edital.permite_custeio ? 'Sim' : 'Não'}</p>
                      )}
                      {edital.permite_capital !== undefined && (
                        <p><strong>Permite capital:</strong> {edital.permite_capital ? 'Sim' : 'Não'}</p>
                      )}
                    </div>
                  </section>
                )}

                {/* Seção Contrapartida */}
                {(edital.tipo_contrapartida || edital.contrapartida_min_percent !== undefined || edital.contrapartida_max_percent !== undefined) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Contrapartida</h2>
                    <div className="text-gray-700 leading-relaxed text-base space-y-2">
                      {edital.tipo_contrapartida && (
                        <p><strong>Tipo:</strong> {edital.tipo_contrapartida}</p>
                      )}
                      {(edital.contrapartida_min_percent !== undefined || edital.contrapartida_max_percent !== undefined) && (
                        <p>
                          <strong>Percentual:</strong>
                          {edital.contrapartida_min_percent !== undefined && edital.contrapartida_max_percent !== undefined ? (
                            ` De ${edital.contrapartida_min_percent}% a ${edital.contrapartida_max_percent}%`
                          ) : edital.contrapartida_max_percent !== undefined ? (
                            ` Até ${edital.contrapartida_max_percent}%`
                          ) : (
                            ` Mínimo de ${edital.contrapartida_min_percent}%`
                          )}
                        </p>
                      )}
                    </div>
                  </section>
                )}

                {/* Seção Tipo de Proponente */}
                {edital.tipo_proponente && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Tipo de Proponente</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <p>{edital.tipo_proponente}</p>
                    </div>
                  </section>
                )}

                {/* Seção O que este edital oferece? */}
                {edital.observacoes && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">O que este edital oferece?</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <p>{edital.observacoes}</p>
                    </div>
                  </section>
                )}

                {/* Seção Quem pode participar e como? */}
                {edital.empresas_elegiveis && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Quem pode participar?</h2>
                    <div className="text-gray-700 leading-relaxed text-base mb-4">
                      <p>{edital.empresas_elegiveis}</p>
                    </div>
                    {edital.link && (
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
                {(edital.data_inicio_submissao || edital.data_fim_submissao) && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Cronograma Completo</h2>
                    <p className="text-gray-700 leading-relaxed text-base">
                      Fique atento ao cronograma: 
                      {edital.data_inicio_submissao && edital.data_fim_submissao && (
                        <>o período para submissão de propostas se inicia em <strong>{formatDate(edital.data_inicio_submissao)}</strong> e vai até a data final de <strong>{formatDate(edital.data_fim_submissao)}</strong>.</>
                      )}
                      {!edital.data_inicio_submissao && edital.data_fim_submissao && (
                        <>o prazo final para submissão das propostas é <strong>{formatDate(edital.data_fim_submissao)}</strong>.</>
                      )}
                      {edital.data_resultado && (
                        <> A divulgação dos resultados está prevista para <strong>{formatDate(edital.data_resultado)}</strong>.</>
                      )}
                    </p>
                  </section>
                )}

                {/* Seção Tipo de Contrapartida */}
                {edital.tipo_contrapartida && (
                  <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">Tipo de Contrapartida</h2>
                    <div className="text-gray-700 leading-relaxed text-base">
                      <p>{edital.tipo_contrapartida}</p>
                    </div>
                  </section>
                )}

              </div>
              
              <div className="w-full xl:w-[40%] space-y-8">
                <SidebarCard 
                  edital={edital} 
                  onDownload={() => downloadPdf(edital.id, edital.arquivo_nome || `edital-${edital.id}.pdf`)} 
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