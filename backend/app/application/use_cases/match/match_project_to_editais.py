"""
Match Project to Editais Use Case
Algoritmo de match usando ChromaDB + GPT-4o em múltiplas etapas
"""
import json
import time
from typing import List, Dict, Any
from datetime import datetime
from openai import AsyncOpenAI

from ....application.services.chromadb_service import ChromaDBService
from ....domain.repositories.edital_repository import EditalRepository


class MatchProjectToEditaisUseCase:
    """
    Caso de uso para encontrar editais compatíveis com um projeto.
    
    Algoritmo:
    1. Recebe dados do projeto
    2. GPT-4o gera 3 frases-chave para busca
    3. Para cada frase, busca vetorial no ChromaDB
    4. Agrega resultados e remove duplicatas
    5. GPT-4o analisa compatibilidade e ranqueia
    6. Retorna top editais com scores
    """

    def __init__(
        self,
        chromadb_service: ChromaDBService,
        edital_repository: EditalRepository,
        openai_api_key: str
    ):
        """
        Inicializa o caso de uso.

        Args:
            chromadb_service: Serviço de busca vetorial
            edital_repository: Repositório de editais
            openai_api_key: Chave da API OpenAI
        """
        self.chromadb = chromadb_service
        self.edital_repository = edital_repository
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)

    async def execute(
        self,
        titulo_projeto: str,
        objetivo_principal: str,
        nome_empresa: str,
        resumo_atividades: str,
        cnae: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Executa o algoritmo de match.

        Args:
            titulo_projeto: Título do projeto
            objetivo_principal: Objetivo principal do projeto
            nome_empresa: Nome da empresa
            resumo_atividades: Resumo das atividades
            cnae: CNAE da empresa
            user_id: ID do usuário

        Returns:
            Dict com resultados do match
        """
        start_time = time.time()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎯 Iniciando algoritmo de match...")

        # ETAPA 1: Consolidar informações do projeto
        project_info = {
            "titulo_projeto": titulo_projeto,
            "objetivo_principal": objetivo_principal,
            "nome_empresa": nome_empresa,
            "resumo_atividades": resumo_atividades,
            "cnae": cnae,
            "user_id": user_id
        }
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📋 Projeto: {titulo_projeto}")

        # ETAPA 2: Gerar 3 frases-chave com GPT-4o
        keywords = await self._generate_search_keywords(project_info)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔑 Palavras-chave geradas: {keywords}")

        # ETAPA 3: Buscar chunks no ChromaDB para cada frase-chave
        all_chunks = []
        for i, keyword in enumerate(keywords, 1):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Buscando com palavra-chave {i}/3: '{keyword}'")
            
            chunks = await self.chromadb.search_similar(
                query=keyword,
                n_results=10  # Top 10 chunks por palavra-chave
            )
            
            all_chunks.extend(chunks)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Encontrados {len(chunks)} chunks")

        # ETAPA 4: Agrupar chunks por edital e remover duplicatas
        editais_chunks = self._group_chunks_by_edital(all_chunks)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📊 Total de editais candidatos: {len(editais_chunks)}")

        # ETAPA 5: Analisar compatibilidade com GPT-4o
        matches = await self._analyze_compatibility_with_gpt(
            project_info=project_info,
            editais_chunks=editais_chunks
        )

        # ETAPA 6: Ordenar por score e retornar top 10
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        top_matches = matches[:10]

        execution_time = time.time() - start_time
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Match concluído em {execution_time:.2f}s")

        return {
            "success": True,
            "total_matches": len(top_matches),
            "keywords_used": keywords,
            "matches": top_matches,
            "execution_time_seconds": round(execution_time, 2)
        }

    async def _generate_search_keywords(self, project_info: Dict[str, Any]) -> List[str]:
        """
        Gera 3 frases-chave para busca usando GPT-4o.

        Args:
            project_info: Informações do projeto

        Returns:
            Lista com 3 frases-chave
        """
        prompt = f"""Você é um especialista em análise de projetos e editais de fomento.

Com base nas informações do projeto abaixo, gere EXATAMENTE 3 frases-chave curtas e relevantes que serão usadas para busca em um banco vetorial (ChromaDB) de editais de fomento.

INFORMAÇÕES DO PROJETO:
- Título: {project_info['titulo_projeto']}
- Objetivo: {project_info['objetivo_principal']}
- Empresa: {project_info['nome_empresa']}
- Atividades: {project_info['resumo_atividades']}
- CNAE: {project_info['cnae']}

INSTRUÇÕES:
1. Cada frase deve ter entre 5-15 palavras
2. Foque em: área temática, público-alvo, tecnologias, impacto social
3. Use termos técnicos relevantes para editais de fomento
4. Evite repetição de palavras entre as frases
5. Retorne APENAS um array JSON com as 3 frases

FORMATO DE SAÍDA (JSON):
["frase 1", "frase 2", "frase 3"]

Exemplo:
["plataforma educacional gamificada para ensino fundamental sobre meio ambiente", "tecnologia educacional EdTech para consciência ecológica infantil", "desenvolvimento software educativo biomas brasileiros sustentabilidade"]
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de projetos e editais. Retorne apenas JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            content = response.choices[0].message.content.strip()
            
            # Extrair JSON do conteúdo (caso venha com markdown)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            keywords = json.loads(content)
            
            # Validar que retornou 3 frases
            if not isinstance(keywords, list) or len(keywords) != 3:
                raise ValueError("GPT não retornou 3 frases-chave")
            
            return keywords

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao gerar palavras-chave: {e}")
            # Fallback: usar informações diretas do projeto
            return [
                f"{project_info['titulo_projeto']} {project_info['objetivo_principal'][:50]}",
                f"{project_info['resumo_atividades'][:80]}",
                f"{project_info['cnae']} tecnologia inovação"
            ]

    def _group_chunks_by_edital(self, chunks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa chunks por edital_uuid e remove duplicatas.

        Args:
            chunks: Lista de chunks do ChromaDB

        Returns:
            Dict {edital_uuid: [chunks]}
        """
        editais_map = {}
        seen_chunk_ids = set()

        for chunk in chunks:
            chunk_id = chunk.get("id")
            
            # Evitar duplicatas
            if chunk_id in seen_chunk_ids:
                continue
            
            seen_chunk_ids.add(chunk_id)
            
            metadata = chunk.get("metadata", {})
            edital_uuid = metadata.get("edital_uuid")
            
            if not edital_uuid:
                continue
            
            if edital_uuid not in editais_map:
                editais_map[edital_uuid] = []
            
            editais_map[edital_uuid].append(chunk)

        return editais_map

    async def _analyze_compatibility_with_gpt(
        self,
        project_info: Dict[str, Any],
        editais_chunks: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Analisa compatibilidade entre projeto e editais usando GPT-4o.

        Args:
            project_info: Informações do projeto
            editais_chunks: Chunks agrupados por edital

        Returns:
            Lista de matches com scores
        """
        matches = []

        for edital_uuid, chunks in editais_chunks.items():
            try:
                # Buscar informações completas do edital
                edital = await self.edital_repository.find_by_uuid(edital_uuid)
                
                if not edital:
                    continue

                # Montar contexto com chunks
                context = self._build_context_for_analysis(chunks)

                # Prompt para análise de compatibilidade
                prompt = f"""Você é um especialista em análise de compatibilidade entre projetos e editais de fomento.

PROJETO:
- Título: {project_info['titulo_projeto']}
- Objetivo: {project_info['objetivo_principal']}
- Empresa: {project_info['nome_empresa']}
- Atividades: {project_info['resumo_atividades']}
- CNAE: {project_info['cnae']}

EDITAL:
- Nome: {edital.apelido_edital}
- Financiador: {edital.financiador_1 or 'N/A'}
- Área de Foco: {edital.area_foco or 'N/A'}
- Tipo de Proponente: {edital.tipo_proponente or 'N/A'}
- Valor Mínimo: R$ {edital.valor_min_R or 'N/A'}
- Valor Máximo: R$ {edital.valor_max_R or 'N/A'}

TRECHOS RELEVANTES DO EDITAL:
{context}

TAREFA:
Analise a compatibilidade entre o projeto e o edital. Retorne um JSON com:
1. "match_score": número de 0 a 100 (compatibilidade)
2. "reasoning": justificativa clara e objetiva (máx 200 caracteres)
3. "compatibility_factors": objeto com fatores-chave de compatibilidade

FORMATO DE SAÍDA (JSON):
{{
  "match_score": 85.5,
  "reasoning": "Alta compatibilidade em educação, tecnologia e meio ambiente. Público-alvo alinhado.",
  "compatibility_factors": {{
    "area_match": "Educação e Tecnologia",
    "target_audience": "Ensino Fundamental",
    "theme_alignment": "Meio Ambiente",
    "innovation_level": "Alto"
  }}
}}
"""

                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um especialista em análise de editais. Retorne apenas JSON válido."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )

                content = response.choices[0].message.content.strip()
                
                # Extrair JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(content)

                # Montar resultado
                match_result = {
                    "edital_uuid": edital_uuid,
                    "edital_name": edital.apelido_edital,
                    "match_score": float(analysis.get("match_score", 0)),
                    "match_percentage": f"{analysis.get('match_score', 0):.1f}%",
                    "reasoning": analysis.get("reasoning", "Análise não disponível"),
                    "compatibility_factors": analysis.get("compatibility_factors", {}),
                    "edital_details": {
                        "financiador": edital.financiador_1,
                        "area_foco": edital.area_foco,
                        "valor_min": edital.valor_min_R,
                        "valor_max": edital.valor_max_R,
                        "data_final_submissao": edital.data_final_submissao.isoformat() if edital.data_final_submissao else None,
                        "link": edital.link
                    },
                    "chunks_found": len(chunks)
                }

                matches.append(match_result)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Analisado: {edital.apelido_edital} - Score: {match_result['match_score']:.1f}")

            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Erro ao analisar edital {edital_uuid}: {e}")
                continue

        return matches

    def _build_context_for_analysis(self, chunks: List[Dict[str, Any]], max_length: int = 2000) -> str:
        """
        Constrói contexto a partir dos chunks para análise.

        Args:
            chunks: Lista de chunks
            max_length: Tamanho máximo do contexto

        Returns:
            Contexto formatado
        """
        context_parts = []
        current_length = 0

        # Ordenar chunks por relevância (distance)
        sorted_chunks = sorted(chunks, key=lambda x: x.get("distance", 999))

        for i, chunk in enumerate(sorted_chunks[:5], 1):  # Top 5 chunks
            text = chunk.get("text", "")
            
            if current_length + len(text) > max_length:
                break
            
            context_parts.append(f"[Trecho {i}] {text[:400]}...")
            current_length += len(text)

        return "\n\n".join(context_parts) if context_parts else "Nenhum trecho relevante encontrado."
