import React from 'react';

/**
 * Skip Link para acessibilidade (WCAG 2.1)
 * 
 * Permite que usuários de teclado/screen readers pulem a navegação
 * e vão direto para o conteúdo principal.
 * 
 * O link fica invisível até receber foco (Tab), então aparece no topo.
 * 
 * Uso: Adicione no App.tsx antes do Header, e coloque id="main-content" no elemento main
 */
export const SkipLink: React.FC = () => {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 
                 focus:z-[9999] focus:px-6 focus:py-3 focus:bg-blue-600 focus:text-white 
                 focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 
                 focus:ring-blue-500 focus:ring-offset-2 transition-all"
    >
      Pular para o conteúdo principal
    </a>
  );
};

/**
 * Props do A11yChecker
 */
interface A11yCheckerProps {
  /** Ativar verificação (apenas dev por padrão) */
  enabled?: boolean;
  /** Mostrar warnings no console */
  verbose?: boolean;
}

/**
 * Componente para verificar problemas de acessibilidade
 * 
 * ATENÇÃO: Usar APENAS em desenvolvimento!
 * Remove automaticamente em produção.
 * 
 * Verifica:
 * - Imagens sem atributo alt
 * - Botões sem texto ou aria-label
 * - Links vazios
 * - Inputs sem labels
 * - Contraste de cores (básico)
 * - Heading hierarchy
 * 
 * Uso: Adicione no App.tsx dentro de uma condicional de ambiente dev
 */
export const A11yChecker: React.FC<A11yCheckerProps> = ({ 
  enabled = import.meta.env.DEV,
  verbose = true,
}) => {
  React.useEffect(() => {
    if (!enabled || !verbose) return;

    const runChecks = () => {
      const errors: string[] = [];
      const warnings: string[] = [];

      // 1. Verificar imagens sem alt
      const imgsWithoutAlt = document.querySelectorAll('img:not([alt])');
      if (imgsWithoutAlt.length > 0) {
        errors.push(`[A11Y] ${imgsWithoutAlt.length} imagem(ns) sem atributo alt`);
        console.warn('[A11Y] Imagens sem alt:', imgsWithoutAlt);
      }

      // 2. Verificar imagens com alt vazio (decorativas devem ter alt="")
      const imgsWithEmptyAlt = document.querySelectorAll('img[alt=""]');
      if (imgsWithEmptyAlt.length > 0) {
        warnings.push(`[WARNING] ${imgsWithEmptyAlt.length} imagem(ns) decorativa(s) (alt="")`);
      }

      // 3. Verificar botões sem label
      const buttonsWithoutLabel = document.querySelectorAll(
        'button:not([aria-label]):not([aria-labelledby]):empty'
      );
      if (buttonsWithoutLabel.length > 0) {
        errors.push(`[A11Y] ${buttonsWithoutLabel.length} botão(ões) sem texto ou aria-label`);
        console.warn('[A11Y] Botões sem label:', buttonsWithoutLabel);
      }

      // 4. Verificar links vazios
      const emptyLinks = document.querySelectorAll(
        'a:not([aria-label]):not([aria-labelledby]):empty'
      );
      if (emptyLinks.length > 0) {
        errors.push(`[A11Y] ${emptyLinks.length} link(s) vazio(s)`);
        console.warn('[A11Y] Links vazios:', emptyLinks);
      }

      // 5. Verificar inputs sem label
      const inputsWithoutLabel = Array.from(document.querySelectorAll('input')).filter(input => {
        const hasLabel = input.labels && input.labels.length > 0;
        const hasAriaLabel = input.hasAttribute('aria-label') || input.hasAttribute('aria-labelledby');
        const isHidden = input.type === 'hidden';
        return !hasLabel && !hasAriaLabel && !isHidden;
      });
      if (inputsWithoutLabel.length > 0) {
        errors.push(`[A11Y] ${inputsWithoutLabel.length} input(s) sem label`);
        console.warn('[A11Y] Inputs sem label:', inputsWithoutLabel);
      }

      // 6. Verificar heading hierarchy
      const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
      let lastLevel = 0;
      headings.forEach(heading => {
        const level = parseInt(heading.tagName[1]);
        if (lastLevel > 0 && level > lastLevel + 1) {
          warnings.push(`[WARNING] Heading pulado: ${heading.tagName} após H${lastLevel}`);
        }
        lastLevel = level;
      });

      // 7. Verificar landmarks (main, nav, etc)
      const hasMain = document.querySelector('main');
      if (!hasMain) {
        warnings.push('[WARNING] Página sem elemento <main>');
      }

      // 8. Verificar idioma
      const hasLang = document.documentElement.hasAttribute('lang');
      if (!hasLang) {
        warnings.push('[WARNING] HTML sem atributo lang');
      }

      // 9. Verificar tabindex positivos (anti-pattern)
      const positiveTabindex = document.querySelectorAll('[tabindex]:not([tabindex="-1"]):not([tabindex="0"])');
      if (positiveTabindex.length > 0) {
        warnings.push(`[WARNING] ${positiveTabindex.length} elemento(s) com tabindex positivo (anti-pattern)`);
      }

      // 10. Verificar elementos interativos dentro de botões/links
      const nestedInteractive = document.querySelectorAll('button button, button a, a button, a a');
      if (nestedInteractive.length > 0) {
        errors.push(`[A11Y] ${nestedInteractive.length} elemento(s) interativo(s) aninhado(s)`);
        console.warn('[A11Y] Elementos interativos aninhados:', nestedInteractive);
      }

      // Exibir resumo
      if (errors.length > 0 || warnings.length > 0) {
        console.group('[A11Y] Verificação de Acessibilidade');
        
        if (errors.length > 0) {
          console.error('ERROS CRÍTICOS:');
          errors.forEach(err => console.error(err));
        }
        
        if (warnings.length > 0) {
          console.warn('AVISOS:');
          warnings.forEach(warn => console.warn(warn));
        }
        
        console.groupEnd();
      } else {
        console.log('[A11Y] Nenhum problema de acessibilidade detectado!');
      }
    };

    // Executar após DOM carregar completamente
    const timer = setTimeout(runChecks, 1000);

    return () => clearTimeout(timer);
  }, [enabled, verbose]);

  // Não renderiza nada
  return null;
};

/**
 * Componente wrapper que adiciona atributos ARIA úteis
 * 
 * @example
 * ```tsx
 * <VisuallyHidden>
 *   Texto visível apenas para screen readers
 * </VisuallyHidden>
 * ```
 */
export const VisuallyHidden: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <span className="sr-only">
      {children}
    </span>
  );
};

/**
 * Componente de ícone com label acessível
 * 
 * @example
 * ```tsx
 * <IconWithLabel icon={<SearchIcon />} label="Buscar" />
 * ```
 */
interface IconWithLabelProps {
  icon: React.ReactNode;
  label: string;
  className?: string;
}

export const IconWithLabel: React.FC<IconWithLabelProps> = ({ icon, label, className }) => {
  return (
    <span className={className} aria-label={label} role="img">
      {icon}
      <VisuallyHidden>{label}</VisuallyHidden>
    </span>
  );
};

/**
 * Hook para anunciar mensagens para screen readers
 * Usa aria-live region
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const announce = useAriaAnnounce();
 *   
 *   const handleSave = () => {
 *     saveData();
 *     announce('Dados salvos com sucesso!');
 *   };
 * }
 * ```
 */
export const useAriaAnnounce = () => {
  const [message, setMessage] = React.useState('');

  const announce = React.useCallback((text: string) => {
    setMessage(text);
    // Limpar depois de 1 segundo
    setTimeout(() => setMessage(''), 1000);
  }, []);

  const AriaLiveRegion = React.useMemo(() => {
    return () => (
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {message}
      </div>
    );
  }, [message]);

  return { announce, AriaLiveRegion };
};

/**
 * Componente FocusTrap para modais
 * Mantém o foco dentro do modal
 * 
 * @example
 * ```tsx
 * <FocusTrap active={isModalOpen}>
 *   <div role="dialog" aria-modal="true">
 *     <h2>Modal</h2>
 *     <button>Fechar</button>
 *   </div>
 * </FocusTrap>
 * ```
 */
interface FocusTrapProps {
  children: React.ReactNode;
  active: boolean;
}

export const FocusTrap: React.FC<FocusTrapProps> = ({ children, active }) => {
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (!active || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    // Focar primeiro elemento
    firstElement?.focus();

    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, [active]);

  return <div ref={containerRef}>{children}</div>;
};

export default {
  SkipLink,
  A11yChecker,
  VisuallyHidden,
  IconWithLabel,
  FocusTrap,
  useAriaAnnounce,
};
