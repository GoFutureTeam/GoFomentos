import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';
import { useParams } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatSectionRef = useRef<HTMLElement>(null);

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

    const userMessage: Message = {
      id: Date.now().toString(),
      text: message.trim(),
      isUser: true,
      timestamp: new Date()
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
      // console.log('Enviando mensagem:', currentMessage);
      // console.log('URL do webhook:', 'https://n8n.gofuture.unifacisa.edu.br/webhook/d24303b1-17a9-4223-ab1d-cf80f9396927');
      
      const response = await fetch('https://n8n.gofuture.unifacisa.edu.br/webhook/d24303b1-17a9-4223-ab1d-cf80f9396927', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          editalId: id,
          message: currentMessage,
          timestamp: new Date().toISOString()
        }),
      });

      // console.log('Response status:', response.status);
      // console.log('Response ok:', response.ok);

      if (response.ok) {
        // Check if response is JSON or text
        const contentType = response.headers.get('content-type');
        let responseText = '';
        
        if (contentType && contentType.includes('application/json')) {
          const responseData = await response.json();
          // console.log('Response data (JSON):', responseData);
          
          if (typeof responseData === 'string') {
            responseText = responseData;
          } else if (responseData.response) {
            responseText = responseData.response;
          }
        } else {
          // Handle as plain text
          responseText = await response.text();
          // console.log('Response data (text):', responseText);
        }
        
        // console.log('Final response text:', responseText);
        
        // Only add agent response if there's actually a response from n8n
        if (responseText && responseText.trim()) {
          const agentMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: responseText,
            isUser: false,
            timestamp: new Date()
          };
          
          setMessages(prev => [...prev, agentMessage]);
        }
      } else {
        // console.log('Response não foi ok:', response.status);
        throw new Error('Erro ao enviar mensagem');
      }
    } catch (error) {
      // console.error('Erro no catch:', error);
      toast({
        title: "Erro",
        description: "Não foi possível enviar sua mensagem. Tente novamente.",
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
              className="flex-1 outline-none bg-transparent text-[#435058] placeholder:text-[#435058] text-sm sm:text-base"
            />
            <button
              type="submit"
              disabled={isLoading}
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
            placeholder="Pergunte algo sobre o Edital da Saúde"
            className="flex-1 outline-none bg-transparent text-[#435058] placeholder:text-gray-400 text-sm sm:text-base px-4 py-2"
          />
          <button
            type="submit"
            disabled={isLoading}
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