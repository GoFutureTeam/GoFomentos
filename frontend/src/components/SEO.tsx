/**
 * COMPONENTE SEO - VERSÃO SIMPLIFICADA SEM DEPENDÊNCIAS
 * 
 * Esta versão não usa react-helmet-async, apenas atualiza o título da página.
 * Para habilitar SEO completo, instale: npm install react-helmet-async
 * 
 * Por enquanto, defina meta tags estáticas no index.html
 */

import React from 'react';

/**
 * Props do componente SEO
 */
export interface SEOProps {
  title: string;
  description: string;
  keywords?: string;
  ogImage?: string;
  ogType?: 'website' | 'article' | 'profile';
  canonicalUrl?: string;
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
  noIndex?: boolean;
  noFollow?: boolean;
}

/**
 * Componente SEO simplificado
 * Atualiza apenas o título da página via JavaScript
 */
export const SEO: React.FC<SEOProps> = ({ 
  title,
  description,
}) => {
  React.useEffect(() => {
    const siteName = 'GoFomentos';
    document.title = `${title} | ${siteName}`;
    
    // Tenta atualizar a meta description se existir
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute('content', description);
    }
  }, [title, description]);

  return null;
};

/**
 * SEO padrão para páginas sem SEO específico
 */
export const DefaultSEO: React.FC = () => {
  return (
    <SEO
      title="Encontre Editais e Fomentos para seu Projeto"
      description="Descubra oportunidades de financiamento, editais públicos e privados."
    />
  );
};
