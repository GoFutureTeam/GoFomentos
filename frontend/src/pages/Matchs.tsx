import React, { useEffect } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import CommonHeader from '../components/CommonHeader';
import { ProjectForm } from '../components/match/FormularioProjeto';
import { ProjetosSalvos } from '../components/match/ProjetosSalvos';
import { MonitoringSection } from '../components/match/MonitoringSection';
import Footer from '../components/details/Footer';
import { useProjetoPortugues } from '@/hooks/useProjetoPortugues';

const Matchs = () => {
  // Obter o ID do projeto da URL, se existir
  const [searchParams] = useSearchParams();
  const projetoId = searchParams.get('projetoId');
  const location = useLocation();
  
  // Buscar os dados do projeto, se um ID foi fornecido
  const { projetos } = useProjetoPortugues();
  const projetoSelecionado = projetoId ? projetos.find(p => p.id === projetoId) : undefined;
  
  // Rolar automaticamente para o formulário quando a página carregar
  useEffect(() => {
    // Aguardar a renderização completa
    const timer = setTimeout(() => {
      const formulario = document.getElementById('formulario-match');
      if (formulario) {
        formulario.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 300);
    
    return () => clearTimeout(timer);
  }, [projetoId]); // Rola sempre que mudar o projetoId ou carregar a página
  
  return (
    <div className="overflow-hidden">
      <CommonHeader 
        title="Matchs" 
        description="Faça um match! Encontre empresas intressadas nos mesmos editais que você e formem uma cooperativa. Ou seja avisado automaticamente sempre que um edital compatível com o seu projeto surgir!" 
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
      
      <main>
        <ProjetosSalvos />
        <div id="formulario-match">
          <ProjectForm projetoInicial={projetoSelecionado} />
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Matchs;