import { useEffect, useState } from 'react';

/**
 * Interface que define os breakpoints e informações de tela
 */
export interface ResponsiveState {
  /** Indica se está em dispositivo móvel (< 768px) */
  isMobile: boolean;
  /** Indica se está em tablet (768px - 1024px) */
  isTablet: boolean;
  /** Indica se está em desktop (>= 1024px) */
  isDesktop: boolean;
  /** Largura atual da janela em pixels */
  width: number;
  /** Altura atual da janela em pixels */
  height: number;
  /** Orientação do dispositivo */
  orientation: 'portrait' | 'landscape';
}

/**
 * Breakpoints padrão do Tailwind CSS
 */
export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

/**
 * Hook para detectar responsividade e breakpoints
 * 
 * Retorna informações sobre o tamanho da tela e dispositivo,
 * permitindo renderização condicional e ajustes de layout.
 * 
 * @returns ResponsiveState com isMobile, isTablet, isDesktop, width, height, orientation
 * 
 * Exemplo de uso: const { isMobile, isDesktop } = useResponsive();
 */
export const useResponsive = (): ResponsiveState => {
  const [state, setState] = useState<ResponsiveState>(() => {
    // Verificação SSR-safe
    if (typeof window === 'undefined') {
      return {
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        width: 1920,
        height: 1080,
        orientation: 'landscape',
      };
    }

    const width = window.innerWidth;
    const height = window.innerHeight;

    return {
      isMobile: width < BREAKPOINTS.md,
      isTablet: width >= BREAKPOINTS.md && width < BREAKPOINTS.lg,
      isDesktop: width >= BREAKPOINTS.lg,
      width,
      height,
      orientation: width > height ? 'landscape' : 'portrait',
    };
  });

  useEffect(() => {
    // Verificação SSR
    if (typeof window === 'undefined') return;

    let timeoutId: NodeJS.Timeout;

    const handleResize = () => {
      // Debounce para performance
      clearTimeout(timeoutId);
      
      timeoutId = setTimeout(() => {
        const width = window.innerWidth;
        const height = window.innerHeight;

        setState({
          isMobile: width < BREAKPOINTS.md,
          isTablet: width >= BREAKPOINTS.md && width < BREAKPOINTS.lg,
          isDesktop: width >= BREAKPOINTS.lg,
          width,
          height,
          orientation: width > height ? 'landscape' : 'portrait',
        });
      }, 150); // Debounce de 150ms
    };

    // Listener de resize
    window.addEventListener('resize', handleResize);
    
    // Listener de orientação (mobile)
    window.addEventListener('orientationchange', handleResize);

    // Cleanup
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  return state;
};

/**
 * Hook para detectar breakpoint específico do Tailwind
 * 
 * @param breakpoint - Nome do breakpoint ('sm' | 'md' | 'lg' | 'xl' | '2xl')
 * @returns true se a largura for maior ou igual ao breakpoint
 * 
 * Exemplo: const isLargeScreen = useBreakpoint('lg');
 */
export const useBreakpoint = (breakpoint: keyof typeof BREAKPOINTS): boolean => {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.innerWidth >= BREAKPOINTS[breakpoint];
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleResize = () => {
      setMatches(window.innerWidth >= BREAKPOINTS[breakpoint]);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return matches;
};

/**
 * Hook para detectar se está em modo mobile (touch)
 * 
 * @returns true se o dispositivo suporta touch
 * 
 * Exemplo: const isTouchDevice = useTouchDevice();
 * Use para desabilitar hover effects em dispositivos touch
 */
export const useTouchDevice = (): boolean => {
  const [isTouch, setIsTouch] = useState(() => {
    if (typeof window === 'undefined') return false;
    
    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      // @ts-expect-error - IE específico
      (navigator.msMaxTouchPoints && navigator.msMaxTouchPoints > 0)
    );
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Detectar primeiro touch
    const handleTouch = () => {
      setIsTouch(true);
    };

    window.addEventListener('touchstart', handleTouch, { once: true });
    
    return () => {
      window.removeEventListener('touchstart', handleTouch);
    };
  }, []);

  return isTouch;
};

/**
 * Hook para detectar modo dark do sistema
 * 
 * @returns true se o usuário prefere dark mode
 * 
 * Exemplo: const prefersDark = usePrefersDarkMode();
 * Use para aplicar tema dark automaticamente baseado na preferência do sistema
 */
export const usePrefersDarkMode = (): boolean => {
  const [prefersDark, setPrefersDark] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersDark(e.matches);
    };

    // Listener moderno
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return prefersDark;
};

export default useResponsive;
