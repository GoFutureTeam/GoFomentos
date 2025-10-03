import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { apiProjeto, DadosProjeto } from '../services/apiProjeto';
import { useToast } from './use-toast';

/**
 * Hook para gerenciar projetos
 * 
 * Nota: Este hook mantém o prefixo "use" para compatibilidade com o React,
 * mas usa o sufixo "Portugues" para indicar que segue as convenções de nomenclatura em português.
 */
export const useProjetoPortugues = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const navigate = useNavigate();
  
  // Consulta para listar projetos
  const { 
    data: projetos = [], // comentario 
    isLoading: carregando, 
    error: erro 
  } = useQuery({
    queryKey: ['projetos'],
    queryFn: async () => {
      const resposta = await apiProjeto.listarProjetos();
      if (!resposta.sucesso) {
        // Se a sessão expirou, redireciona para login
        if (resposta.mensagem.includes('Sessão expirada') || resposta.mensagem.includes('login')) {
          toast({
            title: 'Sessão expirada',
            description: 'Por favor, faça login novamente.',
            variant: 'destructive'
          });
          navigate('/login');
        }
        throw new Error(resposta.mensagem);
      }
      return resposta.dados;
    }
  });
  
  // Mutação para salvar projeto
  const { 
    mutate: salvarProjeto, 
    isPending: salvando 
  } = useMutation({
    mutationFn: async (dados: DadosProjeto) => {
      const resposta = await apiProjeto.salvarProjeto(dados);
      if (!resposta.sucesso) {
        // Se a sessão expirou, redireciona para login
        if (resposta.mensagem.includes('Sessão expirada') || resposta.mensagem.includes('login')) {
          toast({
            title: 'Sessão expirada',
            description: 'Por favor, faça login novamente.',
            variant: 'destructive'
          });
          navigate('/login');
        }
        throw new Error(resposta.mensagem);
      }
      return resposta.dados;
    },
    onSuccess: (_, variaveis) => {
      // Invalidar a consulta para atualizar a lista
      queryClient.invalidateQueries({ queryKey: ['projetos'] });
      
      // Mostrar notificação de sucesso
      toast({
        title: variaveis.id ? 'Projeto atualizado com sucesso!' : 'Projeto salvo com sucesso!',
        description: `O projeto "${variaveis.titulo_projeto}" foi ${variaveis.id ? 'atualizado' : 'salvo'} com sucesso.`
      });
    },
    onError: (erro) => {
      // Mostrar notificação de erro
      toast({
        title: 'Erro ao salvar projeto',
        description: erro instanceof Error ? erro.message : 'Ocorreu um erro ao salvar o projeto.',
        variant: 'destructive'
      });
    }
  });
  
  // Mutação para excluir projeto
  const { 
    mutate: excluirProjeto, 
    isPending: excluindo 
  } = useMutation({
    mutationFn: async (id: string) => {
      const resposta = await apiProjeto.excluirProjeto(id);
      if (!resposta.sucesso) {
        throw new Error(resposta.mensagem);
      }
      return id;
    },
    onSuccess: (id) => {
      // Invalidar a consulta para atualizar a lista
      queryClient.invalidateQueries({ queryKey: ['projetos'] });
      
      // Mostrar notificação de sucesso
      toast({
        title: 'Projeto excluído com sucesso!',
        description: 'O projeto foi excluído com sucesso.'
      });
    },
    onError: (erro) => {
      // Mostrar notificação de erro
      toast({
        title: 'Erro ao excluir projeto',
        description: erro instanceof Error ? erro.message : 'Ocorreu um erro ao excluir o projeto.',
        variant: 'destructive'
      });
    }
  });
  
  return {
    projetos,
    carregando,
    erro,
    salvando,
    excluindo,
    salvarProjeto,
    excluirProjeto
  };
};
