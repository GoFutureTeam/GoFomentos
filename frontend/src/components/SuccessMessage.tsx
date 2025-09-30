import React from 'react';
import { Check } from 'lucide-react';

interface SuccessMessageProps {
  title: string;
  description: string;
  className?: string;
}

export const SuccessMessage: React.FC<SuccessMessageProps> = ({ 
  title, 
  description, 
  className = "" 
}) => {
  return (
    <article 
      className={`relative bg-white shadow-lg flex flex-col items-center justify-center text-center px-16 py-8 rounded-3xl max-w-4xl w-full mx-auto ${className}`}
      role="alert"
      aria-live="polite"
    >
      <div className="mb-6">
        <Check className="w-16 h-16 text-gray-600 stroke-[3] mx-auto" />
      </div>
      
      <header className="mb-3">
        <h1 className="text-3xl font-bold text-gray-900 font-archivo leading-tight whitespace-nowrap">
          {title}
        </h1>
      </header>
      
      <p className="text-lg text-gray-700 font-archivo font-medium leading-relaxed whitespace-nowrap">
        {description}
      </p>
    </article>
  );
};