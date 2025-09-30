import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Corrige problemas de encoding UTF-8 em strings recebidas da API
 * Substitui caracteres mal codificados pelos corretos
 */
export function fixEncoding(text: string | null | undefined): string {
  if (!text) return '';
  
  const encodingFixes: Record<string, string> = {
    // Vogais com acentos
    'Ã¡': 'á', 'Ã ': 'à', 'Ã¢': 'â', 'Ã£': 'ã', 'Ã¤': 'ä',
    'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã«': 'ë',
    'Ã­': 'í', 'Ã¬': 'ì', 'Ã®': 'î', 'Ã¯': 'ï',
    'Ã³': 'ó', 'Ã²': 'ò', 'Ã´': 'ô', 'Ãµ': 'õ', 'Ã¶': 'ö',
    'Ãº': 'ú', 'Ã¹': 'ù', 'Ã»': 'û', 'Ã¼': 'ü',
    
    // Vogais maiúsculas com acentos  
    'Â': 'Â', 'Ä': 'Ä',
    'É': 'É', 'È': 'È', 'Ê': 'Ê', 'Ë': 'Ë',
    'Í': 'Í', 'Ì': 'Ì', 'Î': 'Î', 'Ï': 'Ï',
    'Ó': 'Ó', 'Ò': 'Ò', 'Ô': 'Ô', 'Õ': 'Õ', 'Ö': 'Ö',
    'Ú': 'Ú', 'Ù': 'Ù', 'Û': 'Û', 'Ü': 'Ü',
    
    // Caracteres especiais comuns
    'Ã§': 'ç', 'Ç': 'Ç',
    'Ã±': 'ñ', 'Ñ': 'Ñ',
    
    // Padrões específicos encontrados na API
    'Ã¡rio': 'ário',
    'Ã§Ã£o': 'ção',
    'Ã§Ãµes': 'ções',
    'Ã­fico': 'ífico',
    'Ã­fica': 'ífica',
    'Ã­cas': 'ícas',
    'Ã­cos': 'icos',
    'Ã³gica': 'ógica',
    'Ã³gico': 'ógico',
    'Ãºblica': 'ública',
    'Ãºblico': 'úblico',
    'Ãºblicas': 'úblicas',
    'Ãºblicos': 'úblicos',
    'Ã¡ria': 'ária',
    'Ã¡rias': 'árias',
    'Ã¡rios': 'ários',
    'PARTICIPAÃÃO': 'PARTICIPAÇÃO',
    'participaÃ§Ã£o': 'participação',
    'educaÃ§Ã£o': 'educação',
    'inovaÃ§Ã£o': 'inovação',
    'organizaÃ§Ãµes': 'organizações',
    'instituiÃ§Ãµes': 'instituições',
    'condiÃ§Ã£o': 'condição',
    'cientÃ­fica': 'científica',
    'tecnolÃ³gica': 'tecnológica',
    'universitÃ¡rias': 'universitárias',
    'comunitÃ¡rias': 'comunitárias',
    'polÃ­ticas': 'políticas',
    'pÃºblicas': 'públicas',
    'territÃ³rios': 'territórios',
    'prioritÃ¡rios': 'prioritários',
    'tÃ©cnico': 'técnico',
    'mÃ¡xima': 'máxima',
    'mÃ¡ximo': 'máximo',
    'diversidade': 'diversidade',
    'qualificaÃ§Ã£o': 'qualificação',
    'produÃ§Ã£o': 'produção',
    'extensÃ£o': 'extensão',
    'universitÃ¡ria': 'universitária',
    'AUXÃLIO': 'AUXÍLIO',
    'LIBERAÃÃES': 'LIBERAÇÕES',
    'ORÃAMENTÃRIA': 'ORÇAMENTÁRIA',
    'FINANCEIRA': 'FINANCEIRA'
  };
  
  let fixedText = text;
  
  // Aplica todas as correções
  Object.entries(encodingFixes).forEach(([wrong, correct]) => {
    fixedText = fixedText.replace(new RegExp(wrong, 'g'), correct);
  });
  
  return fixedText;
}
