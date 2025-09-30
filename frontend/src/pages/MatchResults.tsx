import React, { useEffect } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { MatchedEditalCard } from '@/components/match/MatchedEditalCard';
import { MonitoringSignup } from '@/components/match/MonitoringSignup';
import { ContactSection } from '@/components/match/ContactSection';
import Footer from '@/components/details/Footer';
import CommonHeader from '@/components/CommonHeader';
import { MatchResult } from '@/hooks/useMatching';
const MatchResults: React.FC = () => {
  const location = useLocation();

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Extract data from location state or sessionStorage
  const getStoredData = () => {
    // First try to get from location state
    if (location.state?.matches && location.state?.projectData) {
      // Store in sessionStorage for persistence
      sessionStorage.setItem('matchResults', JSON.stringify(location.state.matches));
      sessionStorage.setItem('projectData', JSON.stringify(location.state.projectData));
      return {
        matches: location.state.matches,
        projectData: location.state.projectData
      };
    }
    
    // If not in location state, try to get from sessionStorage
    try {
      const storedMatches = sessionStorage.getItem('matchResults');
      const storedProjectData = sessionStorage.getItem('projectData');
      
      if (storedMatches && storedProjectData) {
        return {
          matches: JSON.parse(storedMatches),
          projectData: JSON.parse(storedProjectData)
        };
      }
    } catch (error) {
      console.error('Error retrieving stored data:', error);
    }
    
    return { matches: [], projectData: null };
  };

  const { matches, projectData } = getStoredData();

  // Se não há dados de matches válidos, redireciona para a página de match
  if (!Array.isArray(matches) || matches.length === 0) {
    // console.log('MatchResults - No valid matches, redirecting to /matchs');
    return <Navigate to="/matchs" replace />;
  }
  return <div className="overflow-hidden">
      <CommonHeader 
        title="Editais encontrados"
        showSecondSection={false}
      />
      
      <div style={{
        backgroundImage: 'url(/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }} className="relative bg-[rgba(220,247,99,0.65)] z-10 flex w-full flex-col items-center py-12 sm:py-16 px-5 lg:px-20 lg:py-[20px]" />
      
      <main className="bg-white flex flex-col items-stretch max-md:max-w-full">
        <header className="text-center pt-[63px]">
          <h1 className="text-black text-[32px] font-extrabold text-center self-center max-md:max-w-full">
            Encontramos {matches.length} editais que combinam com seu projeto!
          </h1>
          <p className="text-black text-2xl font-medium leading-none text-center self-center mt-1.5 max-md:max-w-full">
            A seguir estão os editais mais compatíveis com o seu projeto cadastrado.
          </p>
        </header>

      {/* Editais Section */}
      <section className="flex flex-col relative w-full items-center mt-[63px] pt-px pb-[45px] px-20 max-md:max-w-full max-md:mt-10 max-md:px-5 py-0">
        
        <div className="relative w-[994px] max-w-full space-y-[60px]">
          {matches.map((match, index) => <MatchedEditalCard key={`match-${index}-${match.titulo_edital || match.titulo || index}`} id={parseInt(match.id_edital) || match.id || index} title={match.titulo_edital || match.titulo || 'Título não informado'} organization={match.orgao_responsavel || match.empresa || 'Organização não informada'} description={match.motivo || match.descricao_resumida || match.descricao || 'Descrição não informada'} openingDate={match.data_inicial_submissao || match.data_inicio_submissao || 'Data não disponível'} closingDate={match.data_final_submissao || match.data_fim_submissao || 'Data não disponível'} compatibilityScore={match.score || match.compatibilityScore || 0} headerImage={`/lovable-uploads/${index % 2 === 0 ? '8a170130-d07b-497a-9e68-ec6bb3ce56bb.png' : 'fc8e9f15-312d-4438-9834-cd7b3554cb1d.png'}`} externalLink={match.link} />)}
          
          <MonitoringSignup projectData={projectData} />
        </div>
      </section>

      <ContactSection />
      </main>
      
      <Footer />
    </div>;
};
export default MatchResults;