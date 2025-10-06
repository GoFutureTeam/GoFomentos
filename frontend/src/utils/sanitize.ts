/**
 * Utilitários de segurança para prevenção de XSS e validação
 * 
 * IMPORTANTE: Sempre use essas funções ao:
 * - Renderizar conteúdo HTML de usuários
 * - Validar URLs de links externos
 * - Exibir dados não confiáveis
 */

/**
 * Sanitiza HTML para prevenir ataques XSS
 * Remove tags e atributos perigosos
 * 
 * @example
 * ```tsx
 * const userInput = '<script>alert("XSS")</script><p>Texto seguro</p>';
 * const safe = sanitizeHTML(userInput);
 * // Resultado: '<p>Texto seguro</p>'
 * ```
 */
export const sanitizeHTML = (dirty: string): string => {
  // Lista de tags permitidas (whitelist approach)
  const ALLOWED_TAGS = [
    'p', 'br', 'span', 'div',
    'b', 'i', 'em', 'strong', 'u',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'a', 'img',
  ];

  // Atributos permitidos por tag
  const ALLOWED_ATTRS: Record<string, string[]> = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
  };

  const doc = new DOMParser().parseFromString(dirty, 'text/html');
  const body = doc.body;

  // Função recursiva para limpar elementos
  const cleanElement = (element: Element): void => {
    const tagName = element.tagName.toLowerCase();

    // Remover tag se não estiver na whitelist
    if (!ALLOWED_TAGS.includes(tagName)) {
      element.replaceWith(...Array.from(element.childNodes));
      return;
    }

    // Limpar atributos
    const allowedAttrs = ALLOWED_ATTRS[tagName] || [];
    Array.from(element.attributes).forEach(attr => {
      if (!allowedAttrs.includes(attr.name)) {
        element.removeAttribute(attr.name);
      }

      // Validar URLs em href e src
      if ((attr.name === 'href' || attr.name === 'src') && attr.value) {
        if (!isValidUrl(attr.value)) {
          element.removeAttribute(attr.name);
        }
      }
    });

    // Adicionar rel="noopener noreferrer" em links externos
    if (tagName === 'a' && element.getAttribute('target') === '_blank') {
      element.setAttribute('rel', 'noopener noreferrer');
    }

    // Processar filhos
    Array.from(element.children).forEach(child => cleanElement(child));
  };

  Array.from(body.children).forEach(child => cleanElement(child));

  return body.innerHTML;
};

/**
 * Remove completamente todas as tags HTML
 * Útil quando só queremos texto puro
 * 
 * @example
 * ```tsx
 * const html = '<p>Olá <b>mundo</b>!</p>';
 * const text = stripHTML(html);
 * // Resultado: 'Olá mundo!'
 * ```
 */
export const stripHTML = (html: string): string => {
  const div = document.createElement('div');
  div.innerHTML = html;
  return div.textContent || div.innerText || '';
};

/**
 * Sanitiza texto simples (escapa caracteres HTML)
 * Previne interpretação de HTML
 * 
 * @example
 * ```tsx
 * const userInput = '<script>alert("XSS")</script>';
 * const safe = sanitizeText(userInput);
 * // Resultado: '&lt;script&gt;alert("XSS")&lt;/script&gt;'
 * ```
 */
export const sanitizeText = (text: string): string => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

/**
 * Valida se uma URL é segura
 * Previne protocolos perigosos como javascript:, data:, etc.
 * 
 * @example
 * ```tsx
 * isValidUrl('https://example.com') // true
 * isValidUrl('javascript:alert(1)') // false
 * isValidUrl('data:text/html,...') // false
 * ```
 */
export const isValidUrl = (url: string): boolean => {
  // Protocolo vazio ou relativo é permitido
  if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
    return true;
  }

  try {
    const parsedUrl = new URL(url, window.location.origin);
    const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
    return allowedProtocols.includes(parsedUrl.protocol);
  } catch {
    // URL inválida
    return false;
  }
};

/**
 * Valida se uma URL é externa (domínio diferente)
 * 
 * @example
 * ```tsx
 * isExternalUrl('https://google.com') // true
 * isExternalUrl('/about') // false
 * isExternalUrl('https://meusite.com') // false (se estiver no meusite.com)
 * ```
 */
export const isExternalUrl = (url: string): boolean => {
  if (!isValidUrl(url)) return false;
  
  // URLs relativas não são externas
  if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
    return false;
  }

  try {
    const parsedUrl = new URL(url, window.location.origin);
    return parsedUrl.hostname !== window.location.hostname;
  } catch {
    return false;
  }
};

/**
 * Escapa caracteres especiais em regex
 * Útil para criar regex dinâmicos seguros
 * 
 * @example
 * ```tsx
 * const userInput = 'test.com';
 * const escaped = escapeRegex(userInput);
 * const regex = new RegExp(escaped);
 * ```
 */
export const escapeRegex = (str: string): string => {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

/**
 * Valida e sanitiza input de busca
 * Remove caracteres perigosos e limita tamanho
 * 
 * @example
 * ```tsx
 * const search = sanitizeSearchInput('<script>alert(1)</script>', 100);
 * // Remove tags e limita caracteres
 * ```
 */
export const sanitizeSearchInput = (input: string, maxLength: number = 200): string => {
  // Remove tags HTML
  let clean = stripHTML(input);
  
  // Remove caracteres de controle
  // eslint-disable-next-line no-control-regex
  clean = clean.replace(/[\x00-\x1F\x7F]/g, '');
  
  // Remove espaços múltiplos
  clean = clean.replace(/\s+/g, ' ');
  
  // Trim e limita tamanho
  clean = clean.trim().substring(0, maxLength);
  
  return clean;
};

/**
 * Valida e sanitiza nome de arquivo
 * Remove caracteres perigosos e path traversal
 * 
 * @example
 * ```tsx
 * sanitizeFilename('../../../etc/passwd') // 'etc_passwd'
 * sanitizeFilename('my file.txt') // 'my_file.txt'
 * ```
 */
export const sanitizeFilename = (filename: string): string => {
  // Remove path traversal
  let clean = filename.replace(/\.\./g, '');
  
  // Remove caracteres perigosos
  // eslint-disable-next-line no-control-regex
  clean = clean.replace(/[<>:"/\\|?*\x00-\x1F]/g, '_');
  
  // Remove espaços múltiplos e substitui por underscore
  clean = clean.replace(/\s+/g, '_');
  
  // Limita tamanho
  clean = clean.substring(0, 255);
  
  return clean.trim();
};

/**
 * Cria um Content Security Policy hash para scripts inline
 * Útil para permitir scripts específicos
 * 
 * @example
 * ```tsx
 * const script = 'console.log("hello")';
 * const hash = await createCSPHash(script);
 * // Adicionar ao CSP: script-src 'sha256-{hash}'
 * ```
 */
export const createCSPHash = async (content: string): Promise<string> => {
  const encoder = new TextEncoder();
  const data = encoder.encode(content);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
};

/**
 * Objeto com funções de sanitização comumente usadas
 * Facilita importação e uso
 */
export const Sanitizer = {
  html: sanitizeHTML,
  text: sanitizeText,
  strip: stripHTML,
  search: sanitizeSearchInput,
  filename: sanitizeFilename,
  url: {
    isValid: isValidUrl,
    isExternal: isExternalUrl,
  },
} as const;

export default Sanitizer;
