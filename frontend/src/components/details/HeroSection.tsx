import React from 'react';

interface HeroSectionProps {
  title: string;
  description: string;
  editalNumber: string;
}

const HeroSection: React.FC<HeroSectionProps> = ({ title, description, editalNumber }) => {
  return (
    <section className="bg-[rgba(67,80,88,1)]">
      <div 
        className="px-5 lg:px-20 py-12 lg:py-16 relative"
        style={{
          backgroundImage: 'url(/lovable-uploads/fc8e9f15-312d-4438-9834-cd7b3554cb1d.png)',
          backgroundSize: 'auto 100%',
          backgroundPosition: 'right center',
          backgroundRepeat: 'no-repeat'
        }}
      >
        <nav className="text-[rgba(248,248,248,1)] text-base sm:text-lg font-medium mb-8" aria-label="Breadcrumb">
          Inicio &gt; Editais
        </nav>
        <div className="flex gap-8 flex-col lg:flex-row items-center">
          <div className="w-full lg:w-[65%]">
            <h1 className="text-[rgba(248,248,248,1)] text-4xl sm:text-5xl lg:text-6xl font-black leading-tight tracking-wide mb-6">
              Soluções para alavancar a inovação em sua empresa
            </h1>
            <p className="text-[rgba(248,248,248,1)] text-lg sm:text-xl font-normal leading-7 sm:leading-8 max-w-2xl">
              Conheça os instrumentos de apoio à inovação disponíveis e selecione os mais adequados ao seu projeto.
            </p>
          </div>
        </div>
      </div>
      <div 
        className="h-6 sm:h-8 lg:h-10" 
        style={{
          backgroundImage: 'url(/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
      />
    </section>
  );
};

export default HeroSection;