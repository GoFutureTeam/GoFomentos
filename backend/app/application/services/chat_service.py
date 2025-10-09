"""
Chat Service - Application Layer
Implementa RAG (Retrieval-Augmented Generation)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import AsyncOpenAI

from ...domain.entities.conversation import Conversation
from ...domain.entities.chat_message import ChatMessage
from ...domain.repositories.conversation_repository import ConversationRepository
from .chromadb_service import ChromaDBService


class ChatService:
    """
    Serviço de chat com RAG.
    Integra ChromaDB (busca vetorial) + OpenAI (geração de resposta).
    """

    def __init__(
        self,
        openai_api_key: str,
        chromadb_service: ChromaDBService,
        conversation_repository: ConversationRepository,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        top_k_chunks: int = 5,
        max_context_length: int = 4000,
        distance_threshold: float = 1.5
    ):
        """
        Inicializa o serviço de chat.

        Args:
            openai_api_key: Chave da API OpenAI
            chromadb_service: Serviço de busca vetorial
            conversation_repository: Repositório de conversas
            model: Modelo OpenAI a ser usado
            temperature: Criatividade da resposta (0-1)
            top_k_chunks: Quantos chunks buscar do ChromaDB
            max_context_length: Limite de tokens do contexto
            distance_threshold: Threshold de relevância (menor = mais restritivo)
        """
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.chromadb = chromadb_service
        self.conversation_repo = conversation_repository
        self.model = model
        self.temperature = temperature
        self.top_k_chunks = top_k_chunks
        self.max_context_length = max_context_length
        self.distance_threshold = distance_threshold

    async def create_conversation(
        self,
        user_id: str,
        edital_uuid: Optional[str] = None
    ) -> Conversation:
        """
        Cria uma nova conversa.

        Args:
            user_id: ID do usuário
            edital_uuid: UUID do edital (opcional, para filtrar contexto)

        Returns:
            Conversation: Nova conversa criada
        """
        conversation = Conversation(
            user_id=user_id,
            title="Nova Conversa",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            edital_uuid=edital_uuid,
            messages=[]
        )

        conversation_id = await self.conversation_repo.create(conversation)
        conversation.id = conversation_id

        return conversation

    def _expand_query(self, user_message: str) -> str:
        """
        Expande a query do usuário de forma MODERADA e INTELIGENTE.

        ESTRATÉGIA:
        - Adiciona apenas 1-2 sinônimos próximos por termo
        - Prioriza manter precisão sobre recall
        - Expansão mais conservadora que a versão anterior

        Args:
            user_message: Pergunta original do usuário

        Returns:
            str: Query expandida moderadamente
        """
        # Mapeamento MODERADO - Apenas sinônimos próximos
        expansions = {
            "prazo": "prazo data",
            "data": "data prazo",
            "submissao": "submissão candidatura",
            "submissão": "submissão candidatura",
            "candidatura": "candidatura submissão",
            "valor": "valor financiamento",
            "financiamento": "financiamento valor recurso",
            "requisito": "requisito critério",
            "documento": "documento anexo",
            "candidato": "candidato proponente",
            "resultado": "resultado divulgação",
            "contato": "contato email telefone",
            "duracao": "duração prazo período",
            "duração": "duração prazo período",
            "area": "área tema",
            "área": "área tema",
            "quando": "quando data",
            "quanto": "quanto valor",
            "cronograma": "cronograma data",
            "etapa": "etapa fase"
        }

        query_lower = user_message.lower()

        # Identificar termos que precisam expansão
        terms_to_expand = []
        for term in expansions.keys():
            if term in query_lower:
                terms_to_expand.append(term)

        # ESTRATÉGIA INTELIGENTE:
        # - Se query já tem 3+ palavras específicas → NÃO expandir muito
        # - Se query é curta (1-2 palavras) → expandir moderadamente
        words_in_query = len(user_message.split())

        if words_in_query >= 3:
            # Query detalhada - manter como está (usuário sabe o que quer)
            return user_message

        # Query curta - adicionar sinônimos próximos
        expanded_terms = [user_message]
        for term in terms_to_expand[:2]:  # Limitar a 2 termos expandidos
            expansion = expansions[term]
            # Adicionar apenas sinônimos que NÃO estão na query original
            synonyms = [s for s in expansion.split() if s not in query_lower]
            if synonyms:
                expanded_terms.append(synonyms[0])  # Apenas o primeiro sinônimo

        return " ".join(expanded_terms)

    async def send_message(
        self,
        conversation_id: str,
        user_message: str,
        edital_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem e obtém resposta via RAG.

        Args:
            conversation_id: ID da conversa
            user_message: Mensagem do usuário
            edital_uuid: Filtrar contexto por edital específico

        Returns:
            Dict com a resposta do assistente e metadados
        """
        # 1. Buscar conversa existente
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ValueError("Conversa não encontrada")

        # 2. EXPANDIR QUERY para melhorar busca
        expanded_query = self._expand_query(user_message)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Query original: '{user_message}'")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Query expandida: '{expanded_query}'")

        # 3. BUSCA VETORIAL - Recuperar chunks relevantes do ChromaDB
        filter_metadata = {"edital_uuid": edital_uuid} if edital_uuid else None
        relevant_chunks = await self.chromadb.search_similar(
            query=expanded_query,  # Usar query expandida
            n_results=self.top_k_chunks * 4,  # Buscar 4x chunks (20 chunks) para garantir recall
            filter_metadata=filter_metadata
        )

        # 4. FILTRAR chunks com baixa relevância (distance muito alto)
        # ChromaDB retorna distance (menor = mais similar)
        filtered_chunks = []
        for chunk in relevant_chunks:
            distance = chunk.get("distance", 999)
            # Usar threshold configurável
            if distance < self.distance_threshold:
                filtered_chunks.append(chunk)
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Chunk descartado (distance: {distance:.3f} > {self.distance_threshold})")

        # Limitar ao top_k_chunks
        filtered_chunks = filtered_chunks[:self.top_k_chunks]

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Encontrados {len(relevant_chunks)} chunks, filtrados para {len(filtered_chunks)} relevantes")

        # 5. CONSTRUIR CONTEXTO com chunks filtrados
        context = self._build_context(filtered_chunks)
        sources = [chunk["id"] for chunk in filtered_chunks]

        # 4. CRIAR MENSAGEM DO USUÁRIO
        user_msg = ChatMessage(
            role="user",
            content=user_message,
            timestamp=datetime.utcnow(),
            sources=[]
        )
        conversation.add_message(user_msg)

        # 5. GERAR RESPOSTA COM OPENAI
        assistant_response = await self._generate_response(
            user_message=user_message,
            context=context,
            conversation_history=conversation.get_messages_history(limit=10)
        )

        # 6. CRIAR MENSAGEM DO ASSISTENTE
        assistant_msg = ChatMessage(
            role="assistant",
            content=assistant_response,
            timestamp=datetime.utcnow(),
            sources=sources
        )
        conversation.add_message(assistant_msg)

        # 7. ATUALIZAR TÍTULO SE FOR A PRIMEIRA MENSAGEM
        if len(conversation.messages) == 2:  # user + assistant
            conversation.title = conversation.generate_title()

        # 8. SALVAR CONVERSA ATUALIZADA
        await self.conversation_repo.update(conversation)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💬 Resposta gerada com sucesso")

        return {
            "conversation_id": conversation_id,
            "message": assistant_response,
            "sources": sources,
            "chunks_used": len(filtered_chunks),
            "timestamp": assistant_msg.timestamp
        }

    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Constrói o contexto a partir dos chunks recuperados.

        Args:
            chunks: Lista de chunks do ChromaDB

        Returns:
            str: Contexto formatado
        """
        if not chunks:
            return "Nenhum documento relevante encontrado na base de conhecimento."

        context_parts = ["DOCUMENTOS RELEVANTES (ordenados por relevância):\n"]

        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            edital_name = metadata.get("edital_name", "Edital")
            chunk_index = metadata.get("chunk_index", "?")
            total_chunks = metadata.get("total_chunks", "?")
            distance = chunk.get("distance", 0)
            text = chunk.get("text", "")

            # NÃO truncar texto - queremos o máximo de contexto possível
            # Apenas remover espaços excessivos
            text = " ".join(text.split())

            # Relevância visual (distance menor = MAIS relevante)
            # ChromaDB pode retornar valores negativos para matches perfeitos
            relevance = "🔥🔥🔥 ALTÍSSIMA RELEVÂNCIA" if distance < 0.3 else "🔥 MUITO RELEVANTE" if distance < 0.7 else "✅ RELEVANTE" if distance < 1.2 else "⚠️ POSSIVELMENTE RELEVANTE"

            context_parts.append(f"\n{'='*70}")
            context_parts.append(f"DOCUMENTO {i} - {relevance}")
            context_parts.append(f"{'='*70}")
            context_parts.append(f"Edital: {edital_name}")
            context_parts.append(f"Trecho: Parte {chunk_index} de {total_chunks}")
            context_parts.append(f"Score de Similaridade: {distance:.4f} (quanto MENOR, mais relevante)")
            context_parts.append(f"\n📄 CONTEÚDO COMPLETO DO TRECHO:")
            context_parts.append(f"{text}")
            context_parts.append(f"--- FIM DO DOCUMENTO {i} ---\n")

        context = "\n".join(context_parts)

        # Limitar tamanho total do contexto (mas com limite maior)
        if len(context) > self.max_context_length:
            # Priorizar primeiros chunks (mais relevantes)
            context = context[:self.max_context_length] + "\n\n[...contexto truncado por limite de tokens...]"

        return context

    async def _generate_response(
        self,
        user_message: str,
        context: str,
        conversation_history: List[ChatMessage]
    ) -> str:
        """
        Gera resposta usando OpenAI com contexto RAG.

        Args:
            user_message: Mensagem do usuário
            context: Contexto recuperado do ChromaDB
            conversation_history: Histórico da conversa

        Returns:
            str: Resposta do assistente
        """
        # Construir histórico de mensagens
        messages = [
            {
                "role": "system",
                "content": f"""Você é um assistente especializado em editais de fomento à pesquisa e inovação no Brasil.
Sua função é ajudar pesquisadores e empresas a entenderem editais de agências como CNPq, FAPESQ, FINEP, CONFAP, CAPES, etc.

INSTRUÇÕES CRÍTICAS - LEIA ANTES DE RESPONDER:

1. **LEIA TODOS OS DOCUMENTOS ABAIXO** - Do primeiro ao último, completamente
2. **ATENÇÃO AOS SCORES**: Documentos com score MENOR ou NEGATIVO são os MAIS RELEVANTES
   - Score negativo ou próximo de zero = ALTÍSSIMA relevância
   - Score > 1.0 = Menor relevância
3. **PRIORIZE DOCUMENTOS COM 🔥🔥🔥** - Estes contêm a resposta que você procura
4. Se encontrar a informação, cite **EXATAMENTE** como aparece no documento
5. **CRONOGRAMAS/DATAS**: Procure por seções com "CRONOGRAMA", "Etapas", "Data", tabelas
6. **VALORES**: Procure por "R$", "reais", "valor", tabelas de financiamento
7. **PRAZOS**: Procure por "submissão", "inscrição", "até", períodos (XX/XX/XXXX a XX/XX/XXXX)

IMPORTANTE:
- NÃO ignore documentos só porque tem score negativo - esses são os MELHORES!
- SEMPRE cite o documento que contém a informação
- Se realmente não encontrar, diga claramente

DOCUMENTOS FORNECIDOS (ORDENADOS POR RELEVÂNCIA):
{context}

LEMBRE-SE: O primeiro documento geralmente contém a resposta. Leia-o com ATENÇÃO TOTAL!
"""
            }
        ]

        # Adicionar histórico (últimas 10 mensagens, excluindo sources)
        for msg in conversation_history[:-1]:  # Excluir a última (é a pergunta atual)
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Adicionar mensagem atual
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Chamar OpenAI
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2000  # Aumentado para respostas mais completas
            )

            answer = response.choices[0].message.content.strip()

            # Log para debug
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🤖 Resposta do LLM ({len(answer)} chars)")

            return answer

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, tente novamente."

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Busca uma conversa por ID.

        Args:
            conversation_id: ID da conversa

        Returns:
            Conversation ou None
        """
        return await self.conversation_repo.get_by_id(conversation_id)

    async def list_conversations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Conversation]:
        """
        Lista conversas de um usuário.

        Args:
            user_id: ID do usuário
            skip: Paginação - registros a pular
            limit: Limite de resultados

        Returns:
            Lista de conversas
        """
        return await self.conversation_repo.get_by_user(user_id, skip, limit)

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Deleta uma conversa.

        Args:
            conversation_id: ID da conversa

        Returns:
            bool: True se deletado com sucesso
        """
        return await self.conversation_repo.delete(conversation_id)
