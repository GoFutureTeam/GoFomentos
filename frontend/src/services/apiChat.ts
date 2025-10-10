import TokenService from './tokenService';
import logger from '@/utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

// ============= INTERFACES =============

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: string[];
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  edital_uuid: string | null;
  messages: ChatMessage[];
}

export interface CreateConversationRequest {
  edital_uuid?: string | null;
}

export interface SendMessageRequest {
  message: string;
  edital_uuid?: string | null;
}

export interface SendMessageResponse {
  conversation_id: string;
  message: string;
  sources: string[];
  chunks_used: number;
  timestamp: string;
}

export interface ConversationListResponse {
  total: number;
  conversations: Conversation[];
}

// ============= SERVIÇO =============

class ChatService {
  /**
   * Retorna headers com autenticação
   */
  private getAuthHeaders(): HeadersInit {
    const token = TokenService.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  /**
   * Cria uma nova conversa (vazia)
   * Endpoint: POST /api/v1/chat/conversations
   */
  async createConversation(editalUuid?: string | null): Promise<Conversation> {
    try {
      const url = `${API_BASE_URL}/api/v1/chat/conversations`;
      logger.log('🆕 Criando nova conversa:', { editalUuid, url });

      const response = await fetch(url, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          edital_uuid: editalUuid || null,
        } as CreateConversationRequest),
      });

      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao criar conversa');
      }

      const conversation: Conversation = await response.json();
      logger.log('✅ Conversa criada:', conversation.id);

      return conversation;
    } catch (error) {
      logger.error('❌ Erro ao criar conversa:', error);
      throw error;
    }
  }

  /**
   * Envia mensagem e recebe resposta via RAG
   * Endpoint: POST /api/v1/chat/conversations/{conversation_id}/messages
   */
  async sendMessage(
    conversationId: string,
    message: string,
    editalUuid?: string | null
  ): Promise<SendMessageResponse> {
    try {
      const url = `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages`;
      logger.log('💬 Enviando mensagem:', { conversationId, message: message.substring(0, 50) + '...', url });

      const response = await fetch(url, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          message,
          edital_uuid: editalUuid || null,
        } as SendMessageRequest),
      });

      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (response.status === 404) {
        throw new Error('Conversa não encontrada. Crie uma nova conversa.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao enviar mensagem');
      }

      const result: SendMessageResponse = await response.json();
      logger.log('✅ Resposta recebida:', {
        chunks_used: result.chunks_used,
        sources: result.sources.length,
        message_length: result.message.length,
      });

      return result;
    } catch (error) {
      logger.error('❌ Erro ao enviar mensagem:', error);
      throw error;
    }
  }

  /**
   * Lista todas as conversas do usuário
   * Endpoint: GET /api/v1/chat/conversations
   */
  async listConversations(skip: number = 0, limit: number = 20): Promise<ConversationListResponse> {
    try {
      const url = `${API_BASE_URL}/api/v1/chat/conversations?skip=${skip}&limit=${limit}`;
      logger.log('📋 Listando conversas:', { skip, limit, url });

      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao listar conversas');
      }

      const result: ConversationListResponse = await response.json();
      logger.log('✅ Conversas listadas:', result.total);

      return result;
    } catch (error) {
      logger.error('❌ Erro ao listar conversas:', error);
      throw error;
    }
  }

  /**
   * Busca uma conversa específica por ID
   * Endpoint: GET /api/v1/chat/conversations/{conversation_id}
   */
  async getConversation(conversationId: string): Promise<Conversation> {
    try {
      const url = `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}`;
      logger.log('🔍 Buscando conversa:', { conversationId, url });

      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (response.status === 404) {
        throw new Error('Conversa não encontrada');
      }

      if (response.status === 403) {
        throw new Error('Acesso negado a esta conversa');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao buscar conversa');
      }

      const conversation: Conversation = await response.json();
      logger.log('✅ Conversa encontrada:', {
        id: conversation.id,
        messages: conversation.messages.length,
      });

      return conversation;
    } catch (error) {
      logger.error('❌ Erro ao buscar conversa:', error);
      throw error;
    }
  }

  /**
   * Deleta uma conversa permanentemente
   * Endpoint: DELETE /api/v1/chat/conversations/{conversation_id}
   */
  async deleteConversation(conversationId: string): Promise<void> {
    try {
      const url = `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}`;
      logger.log('🗑️ Deletando conversa:', { conversationId, url });

      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });

      if (response.status === 401) {
        TokenService.clearTokens();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      }

      if (response.status === 404) {
        throw new Error('Conversa não encontrada');
      }

      if (response.status === 403) {
        throw new Error('Acesso negado a esta conversa');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao deletar conversa');
      }

      logger.log('✅ Conversa deletada');
    } catch (error) {
      logger.error('❌ Erro ao deletar conversa:', error);
      throw error;
    }
  }
}

// Exportar instância única
export const chatService = new ChatService();
export default chatService;
