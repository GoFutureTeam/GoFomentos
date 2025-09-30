import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

interface SearchInputProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

const SearchInput: React.FC<SearchInputProps> = ({
  onSearch,
  placeholder = 'Pesquise um edital aqui',
}) => {
  const [query, setQuery] = useState('');

  // Debounce para busca automática
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onSearch(query);
    }, 300); // 300ms de delay

    return () => clearTimeout(timeoutId);
  }, [query]); // Remove onSearch da dependência para evitar loops

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query); // Busca imediata no submit
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    // A busca automática acontece via useEffect com debounce
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="
        flex items-center
        bg-white
        shadow-md
        px-6 py-3
        rounded-full
        w-full max-w-[600px]
        mx-auto
        gap-3
      "
    >
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
        aria-label="Search editais"
        className="
          flex-1
          bg-transparent
          outline-none
          text-base sm:text-lg
          placeholder:text-[#B1B1B1]
        "
      />
      <button type="submit" className="flex-shrink-0">
        <Search size={20} className="text-[#435058]" />
      </button>
    </form>
  );
};

export default SearchInput;
