import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';
import { useParams } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import chatService from '@/services/apiChat';
import logger from '@/utils/logger';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  sources?: string[]; // IDs dos chunks (apenas para assistant)
}

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);
  const { id } = useParams<{ id: string }>(); // UUID do edital
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatSectionRef = useRef<HTMLElement>(null);

  // Criar conversa ao montar o componente
  useEffect(() => {
    const initializeConversation = async () => {
      if (conversationId || isCreatingConversation) return;

      setIsCreatingConversation(true);
      try {
        logger.log('🎬 Inicializando conversa para edital:', id);
        const conversation = await chatService.createConversation(id);
        setConversationId(conversation.id);
        logger.log('✅ Conversa criada:', conversation.id);
      } catch (error) {
        logger.error('❌ Erro ao criar conversa:', error);
        toast({
          title: "Erro",
          description: "Não foi possível iniciar o chat. Tente recarregar a página.",
          variant: "destructive",
        });
      } finally {
        setIsCreatingConversation(false);
      }
    };

    initializeConversation();
  }, [id, conversationId, isCreatingConversation, toast]);

  // Auto scroll to bottom when new messages are added
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Smooth scroll to chat when it expands
  useEffect(() => {
    if (isExpanded && chatSectionRef.current) {
      setTimeout(() => {
        chatSectionRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 100);
    }
  }, [isExpanded]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Verificar se tem conversa criada
    if (!conversationId) {
      toast({
        title: "Erro",
        description: "Chat ainda não está pronto. Aguarde um momento.",
        variant: "destructive",
      });
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      text: message.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    // Add user message and expand chat
    setMessages(prev => [...prev, userMessage]);
    if (!isExpanded) {
      setIsExpanded(true);
    }

    const currentMessage = message.trim();
    setMessage('');
    setIsLoading(true);
    
    try {
      logger.log('💬 Enviando mensagem para backend:', currentMessage);
      
      // Chamar backend RAG
      const result = await chatService.sendMessage(
        conversationId,
        currentMessage,
        id // edital UUID
      );

      logger.log('✅ Resposta recebida do backend:', {
        message_length: result.message.length,
        sources: result.sources.length,
        chunks_used: result.chunks_used,
      });

      // Adicionar resposta do assistente
      const assistantMessage: Message = {
        id: result.timestamp,
        text: result.message,
        isUser: false,
        timestamp: new Date(result.timestamp),
        sources: result.sources, // IDs dos chunks usados
      };
      
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      logger.error('❌ Erro ao enviar mensagem:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Não foi possível enviar sua mensagem. Tente novamente.';
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
      
      // Remove user message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  if (!isExpanded) {
    // Initial compact state
    return (
      <section 
        ref={chatSectionRef}
        className="bg-[rgba(217,217,217,0.15)] rounded-[39px] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] p-6 sm:p-8 transition-all duration-500 ease-in-out max-w-3xl mx-auto"
      >
        <h2 className="text-[rgba(67,80,88,1)] text-lg sm:text-xl font-extrabold text-center mb-2">
          Ficou com alguma dúvida?
        </h2>
        <p className="text-black font-medium text-center mb-6 text-sm">
          Pergunte ao nosso chat sobre editais, especificações e normas
        </p>
        
        <form onSubmit={handleSubmit}>
          <div className="bg-white rounded-[35px] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] flex items-center p-3 sm:p-4">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Pergunte algo sobre o Edital"
              disabled={isLoading || !conversationId}
              className="flex-1 outline-none bg-transparent text-[#435058] placeholder:text-[#435058] text-sm sm:text-base disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !conversationId}
              className="ml-3 sm:ml-4 hover:opacity-80 transition-opacity flex-shrink-0 p-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5 text-[#435058]" />
            </button>
          </div>
        </form>
      </section>
    );
  }

  // Expanded chat state
  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header - Outside the chat card */}
      <div className="text-center mb-6 font-archivo">
        <h2 className="text-[rgba(67,80,88,1)] text-xl sm:text-2xl font-extrabold mb-2">
          Ficou com alguma dúvida?
        </h2>
        <h3 className="text-[rgba(67,80,88,1)] text-lg sm:text-xl font-bold mb-2">
          Conheça nosso especialista em editais
        </h3>
        <p className="text-[rgba(67,80,88,1)] font-medium text-sm sm:text-base">
          Pergunte ao nosso chat sobre prazos, especificações e normas
        </p>
      </div>

      <section 
        ref={chatSectionRef}
        className="bg-white rounded-[20px] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] p-6 sm:p-8 transition-all duration-500 ease-in-out animate-fade-in"
      >

      {/* Chat Messages Container */}
      <div className="bg-[#F8F8F8] rounded-[20px] p-6 mb-6 max-h-96 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div
                className={`max-w-[70%] p-4 text-sm sm:text-base ${
                  msg.isUser
                    ? 'bg-[#C4D626] text-black rounded-[20px_20px_8px_20px] font-medium'
                    : 'bg-white text-black rounded-[20px_20px_20px_8px] shadow-sm border border-gray-100'
                }`}
              >
                <div className="leading-relaxed space-y-2">
                  {msg.text.split('\n').map((line, index) => {
                    const trimmedLine = line.trim();
                    
                    // Handle numbered lists
                    if (/^\d+\.\s*\*\*/.test(trimmedLine)) {
                      const match = trimmedLine.match(/^(\d+\.\s*)(\*\*[^*]+\*\*):?\s*(.*)$/);
                      if (match) {
                        return (
                          <div key={index} className="flex gap-2">
                            <span className="font-medium text-gray-600 flex-shrink-0">{match[1]}</span>
                            <div>
                              <span className="font-bold">{match[2].replace(/\*\*/g, '')}</span>
                              {match[3] && <span>: {match[3]}</span>}
                            </div>
                          </div>
                        );
                      }
                    }
                    
                    // Handle simple numbered lists
                    if (/^\d+\./.test(trimmedLine)) {
                      return (
                        <div key={index} className="flex gap-2">
                          <span className="font-medium text-gray-600 flex-shrink-0">{trimmedLine.match(/^\d+\./)?.[0]}</span>
                          <span>{trimmedLine.replace(/^\d+\.\s*/, '')}</span>
                        </div>
                      );
                    }
                    
                    // Handle bold text
                    if (trimmedLine.includes('**')) {
                      const parts = trimmedLine.split(/(\*\*[^*]+\*\*)/g);
                      return (
                        <p key={index}>
                          {parts.map((part, partIndex) => 
                            part.startsWith('**') && part.endsWith('**') ? (
                              <span key={partIndex} className="font-bold">
                                {part.replace(/\*\*/g, '')}
                              </span>
                            ) : (
                              part
                            )
                          )}
                        </p>
                      );
                    }
                    
                    // Regular text or empty lines
                    return trimmedLine ? (
                      <p key={index}>{trimmedLine}</p>
                    ) : (
                      <div key={index} className="h-2"></div>
                    );
                  })}
                </div>

                {/* Fontes ocultas - dados disponíveis mas não exibidos */}
                {/* {!msg.isUser && msg.sources && msg.sources.length > 0 && (...)} */}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start animate-pulse">
              <div className="bg-white text-black p-4 rounded-[20px_20px_20px_8px] shadow-sm border border-gray-100">
                <p className="text-sm sm:text-base">...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit}>
        <div className="bg-[#F8F8F8] rounded-full border border-gray-200 flex items-center p-2 sm:p-3">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Pergunte algo sobre o Edital"
            disabled={isLoading || !conversationId}
            className="flex-1 outline-none bg-transparent text-[#435058] placeholder:text-gray-400 text-sm sm:text-base px-4 py-2 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !conversationId}
            className="ml-2 hover:opacity-80 transition-opacity flex-shrink-0 p-2 bg-white rounded-full shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5 text-[#435058]" />
          </button>
        </div>
      </form>
      </section>
    </div>
  );
};

export default ChatInterface;