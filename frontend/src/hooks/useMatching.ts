import { useState, useCallback } from 'react';
import { Edital } from '@/types/edital';

export interface ProjectData {
  projectTitle: string;
  projectObjective: string;
  companyName: string;
  companyActivities: string;
  cnae: string;
  file?: File;
}

export interface MatchResult extends Edital {
  compatibilityScore?: number;
  matchReasons?: string[];
  // Campos retornados pelo n8n
  score?: number;
  titulo_edital?: string;
  motivo?: string;
  link?: string;
  orgao_responsavel?: string;
  data_inicial_submissao?: string;
  data_final_submissao?: string;
  id_edital?: string;
}

export const useMatching = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [matches, setMatches] = useState<MatchResult[]>([]);

  const calculateCompatibility = useCallback((projectData: ProjectData, edital: Edital): { score: number; reasons: string[] } => {
    let score = 0;
    const reasons: string[] = [];

    // Análise por palavras-chave no título e descrição
    const projectKeywords = [
      ...projectData.projectTitle.toLowerCase().split(' '),
      ...projectData.projectObjective.toLowerCase().split(' '),
      ...projectData.companyActivities.toLowerCase().split(' ')
    ].filter(word => word.length > 3);

    const editalContent = [
      edital.apelido_edital?.toLowerCase() || '',
      edital.financiador_1?.toLowerCase() || '',
      edital.financiador_2?.toLowerCase() || '',
      edital.tipo_proponente?.toLowerCase() || '',
      edital.origem?.toLowerCase() || ''
    ].join(' ');

    // Score por palavras-chave correspondentes (até 40 pontos)
    const keywordMatches = projectKeywords.filter(keyword => 
      editalContent.includes(keyword)
    ).length;
    
    const keywordScore = Math.min(40, (keywordMatches / projectKeywords.length) * 40);
    score += keywordScore;
    
    if (keywordMatches > 0) {
      reasons.push(`${keywordMatches} palavras-chave compatíveis encontradas`);
    }

    // Análise de categoria (até 25 pontos)
    const categoryKeywords = ['tecnologia', 'inovação', 'pesquisa', 'desenvolvimento', 'sustentabilidade', 'educação', 'saúde', 'social'];
    const projectCategories = categoryKeywords.filter(cat => 
      projectData.projectObjective.toLowerCase().includes(cat) ||
      projectData.companyActivities.toLowerCase().includes(cat)
    );
    
    const editalCategories = categoryKeywords.filter(cat => 
      edital.apelido_edital?.toLowerCase().includes(cat) ||
      edital.financiador_1?.toLowerCase().includes(cat) ||
      edital.tipo_proponente?.toLowerCase().includes(cat)
    );

    const categoryMatches = projectCategories.filter(cat => editalCategories.includes(cat));
    if (categoryMatches.length > 0) {
      score += 25;
      reasons.push(`Categoria compatível: ${categoryMatches.join(', ')}`);
    }

    // Análise de tipo de empresa/proponente (até 20 pontos)
    if (edital.tipo_proponente) {
      const eligibleTypes = edital.tipo_proponente.toLowerCase();
      if (eligibleTypes.includes('jurídica') || eligibleTypes.includes('empresa')) {
        score += 20;
        reasons.push('Tipo de proponente compatível');
      }
    } else {
      // Se não especifica, assume que aceita empresas
      score += 15;
      reasons.push('Tipo de proponente não especificado');
    }

    // Análise de CNAE (até 15 pontos)
    if (projectData.cnae) {
      const cnaePrefix = projectData.cnae.substring(0, 2);
      const techCnaes = ['62', '63', '72', '82', '85', '86', '90']; // CNAEs relacionados a tecnologia, educação, etc.
      
      if (techCnaes.includes(cnaePrefix)) {
        score += 15;
        reasons.push('CNAE compatível com área tecnológica');
      }
    }

    return { score: Math.round(score), reasons };
  }, []);

  const findMatches = useCallback(async (projectData: ProjectData, editais: Edital[]): Promise<MatchResult[]> => {
    setIsAnalyzing(true);
    
    try {
      // Promise para simular tempo de processamento
      const analysisPromise = new Promise<MatchResult[]>(resolve => {
        setTimeout(() => {
          const results: MatchResult[] = editais.map(edital => {
            const { score, reasons } = calculateCompatibility(projectData, edital);
            
            return {
              ...edital,
              compatibilityScore: score,
              matchReasons: reasons
            };
          });

          // Filtrar apenas matches com score >= 50% e ordenar por score
          const filteredResults = results
            .filter(result => result.compatibilityScore >= 50)
            .sort((a, b) => b.compatibilityScore - a.compatibilityScore);

          resolve(filteredResults);
        }, 1500);
      });

      // Promise para timeout (10 segundos)
      const timeoutPromise = new Promise<MatchResult[]>((_, reject) => {
        setTimeout(() => {
          reject(new Error('TIMEOUT'));
        }, 10000);
      });

      // Corrida entre análise e timeout
      const results = await Promise.race([analysisPromise, timeoutPromise]);
      
      setMatches(results);
      setIsAnalyzing(false);
      
      return results;
    } catch (error) {
      setIsAnalyzing(false);
      if (error instanceof Error && error.message === 'TIMEOUT') {
        throw new Error('TIMEOUT');
      }
      throw error;
    }
  }, [calculateCompatibility]);

  const resetMatches = useCallback(() => {
    setMatches([]);
  }, []);

  return {
    matches,
    isAnalyzing,
    findMatches,
    resetMatches
  };
};