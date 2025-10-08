"""
OpenAI Extractor Service - Extração de variáveis com LLM
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
import asyncio
from openai import AsyncOpenAI

from ...domain.repositories.edital_repository import EditalRepository


class OpenAIExtractorService:
    """
    Serviço para extração de variáveis de editais usando OpenAI.
    Implementa salvamento progressivo no MongoDB e vetorização no ChromaDB.
    """

    def __init__(
        self,
        openai_api_key: str,
        edital_repository: EditalRepository,
        chromadb_service: Optional[Any] = None,
        chunk_delay_ms: int = 500
    ):
        """
        Inicializa o serviço.

        Args:
            openai_api_key: Chave da API OpenAI
            edital_repository: Repositório de editais
            chromadb_service: Serviço ChromaDB (opcional)
            chunk_delay_ms: Delay em milissegundos entre chunks para não sobrecarregar a API
        """
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.edital_repo = edital_repository
        self.chromadb_service = chromadb_service
        self.chunk_delay_ms = chunk_delay_ms

    def _chunk_text(self, text: str, chunk_size: int = 3000, overlap: int = 300) -> List[str]:
        """
        Divide o texto em chunks com sobreposição.

        Args:
            text: Texto completo
            chunk_size: Tamanho de cada chunk
            overlap: Sobreposição entre chunks

        Returns:
            List[str]: Lista de chunks
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start += chunk_size - overlap
        return chunks

    def _merge_variables(self, accumulated: Dict, new: Dict) -> Dict:
        """
        Merge inteligente de variáveis extraídas.
        Prioriza valores mais completos e não-nulos.

        Args:
            accumulated: Dicionário acumulado
            new: Novo dicionário com variáveis

        Returns:
            Dict: Dicionário merged
        """
        for key, value in new.items():
            # Nunca sobrescrever link e uuid que vêm do sistema
            if key in ["link", "uuid"]:
                continue

            if value is not None and value != "":
                # Se o campo ainda não existe ou é nulo, adiciona
                if accumulated.get(key) is None or accumulated.get(key) == "":
                    accumulated[key] = value
                # Se ambos têm valor string, mantém o mais longo
                elif isinstance(value, str) and isinstance(accumulated.get(key), str):
                    if len(value) > len(accumulated[key]):
                        accumulated[key] = value
                # Para números, mantém o não-zero
                elif isinstance(value, (int, float)) and value != 0:
                    if accumulated.get(key) == 0 or accumulated.get(key) is None:
                        accumulated[key] = value

        return accumulated

    async def extract_variables_progressive(
        self,
        text: str,
        edital_uuid: str,
        pdf_url: str,
        max_retries: int = 1
    ) -> Dict[str, Any]:
        """
        Extrai variáveis do texto chunk por chunk e SALVA PROGRESSIVAMENTE.

        Args:
            text: Texto completo do edital
            edital_uuid: UUID do edital
            pdf_url: URL do PDF
            max_retries: Número máximo de tentativas em caso de erro

        Returns:
            Dict[str, Any]: Variáveis consolidadas
        """
        chunks = self._chunk_text(text)
        accumulated_vars = {
            "link": pdf_url,
            "uuid": edital_uuid
        }

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📊 Total de chunks: {len(chunks)}")

        for i, chunk in enumerate(chunks, 1):
            retry_count = 0
            success = False

            while retry_count <= max_retries and not success:
                try:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Processando chunk {i}/{len(chunks)}")

                    # Extrair variáveis do chunk
                    chunk_vars = await self._extract_chunk(chunk, i, len(chunks))

                    # ✅ SALVAR NO MONGODB A CADA CHUNK
                    await self.edital_repo.save_partial_extraction(
                        edital_uuid=edital_uuid,
                        chunk_index=i,
                        variables=chunk_vars,
                        status="in_progress"
                    )
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💾 Chunk {i} salvo no MongoDB")

                    # 🔍 VETORIZAR E SALVAR NO CHROMADB
                    if self.chromadb_service:
                        try:
                            edital_name = chunk_vars.get('apelido_edital') or accumulated_vars.get('apelido_edital') or 'Edital CNPq'
                            await self.chromadb_service.add_chunk(
                                chunk_text=chunk,
                                edital_uuid=edital_uuid,
                                edital_name=edital_name,
                                chunk_index=i,
                                total_chunks=len(chunks),
                                metadata={
                                    "financiador": chunk_vars.get('financiador_1') or chunk_vars.get('financiador_2'),
                                    "area_foco": chunk_vars.get('area_foco'),
                                    "link": pdf_url
                                }
                            )
                        except Exception as e:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Erro ao vetorizar chunk {i} no ChromaDB: {e}")

                    # Merge com variáveis acumuladas
                    accumulated_vars = self._merge_variables(accumulated_vars, chunk_vars)

                    success = True

                    # ⏱️ Delay entre chunks para não sobrecarregar a event loop da API
                    await asyncio.sleep(self.chunk_delay_ms / 1000.0)

                except Exception as e:
                    retry_count += 1
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro no chunk {i} (tentativa {retry_count}/{max_retries + 1}): {e}")

                    if retry_count > max_retries:
                        # Registrar erro mas continuar
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Pulando chunk {i} após {max_retries + 1} tentativas")
                        break

        # ✅ GARANTIR QUE LINK E UUID ESTEJAM PRESENTES
        accumulated_vars["link"] = pdf_url
        accumulated_vars["uuid"] = edital_uuid

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔗 DEBUG: Link do PDF antes de salvar: '{pdf_url}'")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔗 DEBUG: Link em accumulated_vars: '{accumulated_vars.get('link')}'")

        # ✅ SALVAR CONSOLIDADO FINAL NO MONGODB
        await self.edital_repo.save_final_extraction(
            edital_uuid=edital_uuid,
            consolidated_variables=accumulated_vars,
            status="completed"
        )
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Variáveis consolidadas salvas no MongoDB")

        return accumulated_vars

    async def _extract_chunk(self, chunk: str, chunk_index: int, total_chunks: int) -> Dict[str, Any]:
        """
        Extrai variáveis de um único chunk usando OpenAI.

        Args:
            chunk: Texto do chunk
            chunk_index: Índice do chunk atual
            total_chunks: Total de chunks

        Returns:
            Dict[str, Any]: Variáveis extraídas
        """
        prompt = f"""
Você é um especialista em análise de editais de fomento à pesquisa e inovação no Brasil.
Sua tarefa é extrair informações estruturadas de editais de agências como CNPq, FAPESQ, FINEP, CONFAP, CAPES, etc.

INSTRUÇÕES IMPORTANTES:
1. Leia TODO o texto cuidadosamente antes de extrair
2. Se um campo não estiver explícito no texto, preencha com null (não com string vazia)
3. Para datas, use o formato YYYY-MM-DD
4. Para valores monetários, extraia apenas o número (sem R$, pontos ou vírgulas)
5. Para percentuais, extraia apenas o número (sem % ou símbolos)
6. Para durações, converta para MESES (ex: "12 meses", "1 ano" = 12 meses)
7. Para booleanos, use true/false (não strings)

CAMPOS A EXTRAIR:

{{
  "apelido_edital": "Título/nome completo do edital (ex: 'Chamada Pública FAPESQ Nº 01/2025')",
  "financiador_1": "Instituição principal que financia (ex: 'CNPq', 'FAPESQ-PB', 'FINEP', 'CONFAP', 'CAPES')",
  "financiador_2": "Instituição secundária ou parceira (null se não houver)",
  "area_foco": "Área(s) temática(s) do edital (ex: 'Saúde', 'Tecnologia', 'Mudanças Climáticas')",
  "tipo_proponente": "Quem pode se candidatar (ex: 'Pesquisadores doutores', 'Instituições de Ensino', 'Empresas')",
  "empresas_que_podem_submeter": "Tipos específicos de empresas elegíveis (ex: 'PMEs', 'Startups', 'Empresas brasileiras')",
  "duracao_min_meses": "Duração mínima do projeto EM MESES (número inteiro ou null)",
  "duracao_max_meses": "Duração máxima do projeto EM MESES (número inteiro ou null)",
  "valor_min_R$": "Valor mínimo de financiamento em REAIS (número ou null)",
  "valor_max_R$": "Valor máximo de financiamento em REAIS (número ou null)",
  "tipo_recurso": "Tipo de recurso oferecido (ex: 'Bolsas', 'Financiamento não-reembolsável', 'Subvenção econômica')",
  "recepcao_recursos": "Como os recursos serão recebidos (ex: 'Diretamente ao pesquisador', 'Via instituição')",
  "custeio": "Permite gastos de custeio? (true/false/null)",
  "capital": "Permite gastos de capital (equipamentos)? (true/false/null)",
  "contrapartida_min_%": "Percentual mínimo de contrapartida exigida (número ou null)",
  "contrapartida_max_%": "Percentual máximo de contrapartida exigida (número ou null)",
  "tipo_contrapartida": "Tipo de contrapartida aceita (ex: 'Financeira', 'Econômica', 'Não há')",
  "data_inicial_submissao": "Data de ABERTURA das submissões (YYYY-MM-DD ou null)",
  "data_final_submissao": "Data de ENCERRAMENTO/PRAZO das submissões (YYYY-MM-DD ou null)",
  "data_resultado": "Data prevista para divulgação dos RESULTADOS (YYYY-MM-DD ou null)",
  "descricao_completa": "Resumo do objetivo/finalidade do edital em 1-2 frases",
  "origem": "Agência de origem (extraia do texto: 'CNPq', 'FAPESQ', 'FINEP', 'CONFAP', 'CAPES', 'Governo da Paraíba', etc.)",
  "observacoes": "Observações importantes, requisitos especiais ou restrições mencionadas"
}}

IMPORTANTE:
- Este é o chunk {chunk_index} de {total_chunks}. Alguns campos podem estar em outros chunks.
- Retorne APENAS o JSON válido, sem markdown, comentários ou texto adicional.
- Use null para campos ausentes, NÃO use string vazia "" ou "null".

Texto do edital:
---
{chunk}
---

JSON extraído:"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        resposta_llm = response.choices[0].message.content.strip()

        # Limpar markdown code blocks
        if "```json" in resposta_llm:
            match = re.search(r'```json\s*(.*?)\s*```', resposta_llm, re.DOTALL)
            if match:
                resposta_llm = match.group(1).strip()
        elif "```" in resposta_llm:
            resposta_llm = resposta_llm.replace("```", "").strip()

        # Parse JSON
        try:
            variables = json.loads(resposta_llm)

            # Converter strings "null" em None
            for key, value in variables.items():
                if isinstance(value, str) and value.lower() == "null":
                    variables[key] = None

            return variables
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Resposta não é JSON válido: {e}")
            return {"erro": "resposta_invalida", "raw": resposta_llm[:500]}
