import React, { useState } from 'react';
import Header from '../components/Header';
import HeroSection from '../components/HeroSection';
import FilterSection from '../components/FilterSection';
import EditalGrid from '../components/EditalGrid';
import Pagination from '../components/Pagination';
import Footer from '../components/details/Footer';
import { useContextoEditaisPortugues } from '../hooks/useContextoEditaisPortugues';
import { FilterUpdate } from '../contexts/EditaisContextTypes';

const Index = () => {
  // console.log('📄 Index page carregando...');
  
  const [currentPage, setCurrentPage] = useState(1);
  
  // Usar o contexto global de editais
  const {
    filteredEditais: editais,
    isLoading,
    loadingDetails,
    error,
    totalCount,
    updateFilters
  } = useContextoEditaisPortugues();

  // console.log('📊 Estado atual do contexto:', { 
  //   editaisCount: editais?.length, 
  //   isLoading, 
  //   error,
  //   totalCount,
  //   editais: editais
  // });

  // console.log('🎯 Index - Condição de renderização:', {
  //   isLoading,
  //   'editais.length': editais?.length,
  //   'Array.isArray(editais)': Array.isArray(editais),
  //   'editais': editais
  // });

  const handleFiltersChange = (newFilters: FilterUpdate) => {
    // console.log('📄 Index recebeu mudança de filtros:', newFilters);
    updateFilters(newFilters);
    setCurrentPage(1);
  };

  // Configurações de paginação
  const itemsPerPage = 6;
  const totalItems = editais.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll to top when page changes
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  return (
    <div className="overflow-hidden">
      <Header />
      
      <main>
        <HeroSection />
        <FilterSection className="py-0" onFiltersChange={handleFiltersChange} />
        
        <section className="bg-white flex w-full flex-col py-[4px]">
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[rgba(67,80,88,1)]"></div>
              <span className="ml-2 text-[rgba(67,80,88,1)]">Buscando editais...</span>
            </div>
          ) : (
            <EditalGrid 
              editais={editais} 
              currentPage={currentPage} 
              itemsPerPage={itemsPerPage} 
              isLoadingDetails={loadingDetails} 
              totalCount={totalCount} 
            />
          )}
          <div className="flex justify-center mt-8">
            <Pagination currentPage={currentPage} totalPages={totalPages} totalItems={totalItems} itemsPerPage={itemsPerPage} onPageChange={handlePageChange} />
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};
export default Index;