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
Você é um extrator de informações de editais do CNPq.
Extraia os seguintes campos em formato JSON válido:

{{
  "apelido_edital": "STRING",
  "financiador_1": "STRING",
  "financiador_2": "STRING",
  "area_foco": "STRING",
  "tipo_proponente": "STRING",
  "empresas_que_podem_submeter": "STRING",
  "duracao_min_meses": "NUMBER",
  "duracao_max_meses": "NUMBER",
  "valor_min_R$": "NUMBER",
  "valor_max_R$": "NUMBER",
  "tipo_recurso": "STRING",
  "recepcao_recursos": "STRING",
  "custeio": "BOOLEAN",
  "capital": "BOOLEAN",
  "contrapartida_min_%": "NUMBER",
  "contrapartida_max_%": "NUMBER",
  "tipo_contrapartida": "STRING",
  "data_inicial_submissao": "YYYY-MM-DD",
  "data_final_submissao": "YYYY-MM-DD",
  "data_resultado": "YYYY-MM-DD",
  "descricao_completa": "STRING",
  "origem": "CNPq",
  "observacoes": "STRING"
}}

Se algum campo não estiver presente neste trecho, preencha com null.
Retorne APENAS o JSON, sem texto adicional.

Texto do edital (chunk {chunk_index}/{total_chunks}):
{chunk}
"""

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
            return variables
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Resposta não é JSON válido: {e}")
            return {"erro": "resposta_invalida", "raw": resposta_llm[:500]}
