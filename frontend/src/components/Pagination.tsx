import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange
}) => {
  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  const handlePageClick = (page: number) => {
    onPageChange(page);
  };

  const getPageNumbers = () => {
    const pages = [];
    const showEllipsis = totalPages > 5;
    
    if (!showEllipsis) {
      // Show all pages if 5 or less
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show smart pagination with ellipsis
      if (currentPage <= 3) {
        pages.push(1, 2, 3, 4, '...', totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1, '...', totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
      }
    }
    
    return pages;
  };

  // Calcular quantos editais estão sendo realmente exibidos na página atual
  const actualDisplayedItems = Math.min(itemsPerPage, totalItems - (currentPage - 1) * itemsPerPage);
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = (currentPage - 1) * itemsPerPage + actualDisplayedItems;

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="text-sm text-gray-600">
        Mostrando {startItem}-{endItem} de {totalItems} editais
      </div>
      
      <nav aria-label="Pagination" className="flex w-full max-w-[400px] gap-2 text-sm sm:text-base text-black font-semibold justify-center items-center flex-wrap">
        <button 
          onClick={handlePrevious} 
          disabled={currentPage === 1} 
          className="disabled:opacity-50 disabled:cursor-not-allowed p-2" 
          aria-label="Previous page"
        >
          <img 
            src="https://cdn.builder.io/api/v1/image/assets/f302f4804c934a9ca3c4b476c31d8232/53545b935b927d7f3e5a86a6c978f08ef9302a38?placeholderIfAbsent=true" 
            alt="Previous" 
            className="aspect-[1] object-contain w-[9px]" 
          />
        </button>
        
        {getPageNumbers().map((page, index) => (
          page === '...' ? (
            <span key={`ellipsis-${index}`} className="px-2 py-1">...</span>
          ) : (
            <button
              key={page}
              onClick={() => handlePageClick(page as number)}
              className={`px-3 py-2 rounded-md transition-colors ${
                currentPage === page 
                  ? 'bg-[rgba(67,80,88,1)] text-neutral-100' 
                  : 'text-black hover:bg-gray-100'
              }`}
              aria-current={currentPage === page ? 'page' : undefined}
            >
              {page}
            </button>
          )
        ))}
        
        <button 
          onClick={handleNext} 
          disabled={currentPage === totalPages} 
          className="disabled:opacity-50 disabled:cursor-not-allowed p-2" 
          aria-label="Next page"
        >
          <img 
            src="https://cdn.builder.io/api/v1/image/assets/f302f4804c934a9ca3c4b476c31d8232/bf97150824951efd853d42294a18cfbed95af157?placeholderIfAbsent=true" 
            alt="Next" 
            className="aspect-[1] object-contain w-[9px]" 
          />
        </button>
      </nav>
    </div>
  );
};

export default Pagination;