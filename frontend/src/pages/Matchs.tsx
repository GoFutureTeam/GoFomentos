import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import CommonHeader from '../components/CommonHeader';
import { ProjectForm } from '../components/match/FormularioProjeto';
import { ProjetosSalvos } from '../components/match/ProjetosSalvos';
import Footer from '../components/details/Footer';
import { useProjetoPortugues } from '@/hooks/useProjetoPortugues';

const Matchs = () => {
  // Obter o ID do projeto da URL, se existir
  const [searchParams] = useSearchParams();
  const projetoId = searchParams.get('projetoId');
  
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
        description="Faça um match! Encontre empresas interessadas nos mesmos editais que você e formem uma cooperativa. Ou seja avisado automaticamente sempre que um edital compatível com o seu projeto surgir!" 
        showSecondSection={false} 
      />
      
      <div className="container mx-auto pt-6 px-4">
        <ProjetosSalvos />
        <div id="formulario-match">
          <ProjectForm projetoInicial={projetoSelecionado} />
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default Matchs;