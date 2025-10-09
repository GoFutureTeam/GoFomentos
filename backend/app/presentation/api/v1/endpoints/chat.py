"""
Chat Endpoints - Presentation Layer
API de chat com RAG (Retrieval-Augmented Generation)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.domain.entities.user import User
from app.presentation.api.v1.dependencies import get_current_user
from app.application.services.chat_service import ChatService
from app.presentation.schemas.chat_schema import (
    CreateConversationRequest,
    SendMessageRequest,
    ConversationResponse,
    SendMessageResponse,
    ConversationListResponse,
    DeleteConversationResponse,
    ChatMessageResponse
)

router = APIRouter()


def get_chat_service() -> ChatService:
    """Dependency para obter o ChatService"""
    from app.core.container_instance import container
    return container.chat_service()


@router.post(
    "/chat/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["chat"],
    summary="Criar nova conversa (vazia)"
)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Cria uma nova conversa de chat **VAZIA** (sem mensagens).

    **Importante:** Este endpoint apenas inicializa a conversa.
    Para enviar mensagens, use o endpoint `POST /chat/conversations/{id}/messages`.

    **Request Body:**
    - `edital_uuid` (opcional): UUID do edital para filtrar o contexto das respostas

    **Exemplo de Request:**
    ```json
    {
        "edital_uuid": null
    }
    ```
    """
    try:
        conversation = await chat_service.create_conversation(
            user_id=current_user.email,
            edital_uuid=request.edital_uuid
        )

        # Converter para response
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            edital_uuid=conversation.edital_uuid,
            messages=[]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar conversa: {str(e)}"
        )


@router.post(
    "/chat/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    tags=["chat"],
    summary="Enviar mensagem e receber resposta (RAG)"
)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Envia uma mensagem e recebe resposta gerada via **RAG (Retrieval-Augmented Generation)**.

    **Fluxo RAG:**
    1. 🔍 Busca chunks relevantes no ChromaDB (busca vetorial semântica)
    2. 📝 Monta contexto com os chunks recuperados + histórico da conversa
    3. 🤖 Envia para OpenAI GPT-4o-mini para gerar resposta contextualizada
    4. 💾 Salva mensagem e resposta no MongoDB
    5. ✅ Retorna resposta com fontes citadas

    **Request Body:**
    - `message` **(OBRIGATÓRIO)**: Sua pergunta ou mensagem (1-2000 caracteres)
    - `edital_uuid` (opcional): UUID do edital para filtrar chunks específicos

    **Exemplo de Request:**
    ```json
    {
        "message": "Qual é o prazo de submissão do edital?",
        "edital_uuid": null
    }
    ```

    **Exemplo de Response:**
    ```json
    {
        "conversation_id": "507f1f77bcf86cd799439011",
        "message": "O prazo de submissão do Edital CNPq 01/2025 é 30/12/2025.",
        "sources": ["edital123_chunk_1", "edital123_chunk_5"],
        "chunks_used": 2,
        "timestamp": "2025-01-15T10:30:00"
    }
    ```
    """
    try:
        result = await chat_service.send_message(
            conversation_id=conversation_id,
            user_message=request.message,
            edital_uuid=request.edital_uuid
        )

        return SendMessageResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )


@router.get(
    "/chat/conversations",
    response_model=ConversationListResponse,
    tags=["chat"],
    summary="Listar todas as conversas"
)
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Lista todas as conversas do usuário autenticado (paginado).

    **Query Parameters:**
    - `skip` (opcional): Número de registros a pular (padrão: 0)
    - `limit` (opcional): Máximo de resultados por página (padrão: 20)

    **Retorna:**
    - Lista de conversas ordenadas por data de atualização (mais recentes primeiro)
    - Cada conversa inclui todo o histórico de mensagens
    """
    try:
        conversations = await chat_service.list_conversations(
            user_id=current_user.email,
            skip=skip,
            limit=limit
        )

        total = len(conversations)  # Poderia ser otimizado com count_by_user

        # Converter para response
        conversations_response = [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                edital_uuid=conv.edital_uuid,
                messages=[
                    ChatMessageResponse(
                        role=msg.role,
                        content=msg.content,
                        timestamp=msg.timestamp,
                        sources=msg.sources or []
                    ) for msg in conv.messages
                ]
            ) for conv in conversations
        ]

        return ConversationListResponse(
            total=total,
            conversations=conversations_response
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar conversas: {str(e)}"
        )


@router.get(
    "/chat/conversations/{conversation_id}",
    response_model=ConversationResponse,
    tags=["chat"],
    summary="Buscar conversa por ID"
)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Busca uma conversa específica com todo o histórico de mensagens.

    **Path Parameter:**
    - `conversation_id` **(obrigatório)**: ID da conversa (retornado ao criar a conversa)

    **Retorna:**
    - Conversa completa com todas as mensagens (usuário + assistente)
    - Inclui fontes citadas em cada resposta do assistente
    """
    try:
        conversation = await chat_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada"
            )

        # Verificar se a conversa pertence ao usuário
        if conversation.user_id != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a esta conversa"
            )

        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            edital_uuid=conversation.edital_uuid,
            messages=[
                ChatMessageResponse(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    sources=msg.sources or []
                ) for msg in conversation.messages
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar conversa: {str(e)}"
        )


@router.delete(
    "/chat/conversations/{conversation_id}",
    response_model=DeleteConversationResponse,
    tags=["chat"],
    summary="Deletar conversa permanentemente"
)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Deleta uma conversa **permanentemente** (não pode ser desfeito).

    **Path Parameter:**
    - `conversation_id` **(obrigatório)**: ID da conversa a ser deletada

    **Importante:**
    - Remove a conversa e todo o histórico de mensagens
    - Apenas o dono da conversa pode deletá-la
    - Operação irreversível
    """
    try:
        # Verificar se a conversa existe e pertence ao usuário
        conversation = await chat_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada"
            )

        if conversation.user_id != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a esta conversa"
            )

        # Deletar
        success = await chat_service.delete_conversation(conversation_id)

        if success:
            return DeleteConversationResponse(
                success=True,
                message="Conversa deletada com sucesso"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao deletar conversa"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar conversa: {str(e)}"
        )
