import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useProjetoPortugues } from '@/hooks/useProjetoPortugues';
import CommonHeader from '@/components/CommonHeader';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';

// Esquema de validação para o formulário
const esquemaProjeto = z.object({
  nomeProjeto: z.string().min(3, 'O nome do projeto deve ter pelo menos 3 caracteres'),
  descricao: z.string().min(10, 'A descrição deve ter pelo menos 10 caracteres'),
  objetivoPrincipal: z.string().min(10, 'O objetivo deve ter pelo menos 10 caracteres'),
  areaProjeto: z.string().min(2, 'A área do projeto deve ser informada')
});

type DadosProjeto = z.infer<typeof esquemaProjeto>;

const EditarProjeto: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { projetos, carregando, erro, salvarProjeto, salvando } = useProjetoPortugues();
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<DadosProjeto>({
    resolver: zodResolver(esquemaProjeto),
    defaultValues: {
      areaProjeto: 'Geral'
    }
  });
  
  // Encontrar o projeto atual pelo ID
  const projetoAtual = projetos.find(p => p.id === id);
  
  // Preencher o formulário com os dados do projeto quando estiverem disponíveis
  useEffect(() => {
    if (projetoAtual) {
      reset({
        nomeProjeto: projetoAtual.nomeProjeto,
        descricao: projetoAtual.descricao,
        objetivoPrincipal: projetoAtual.objetivoPrincipal || '',
        areaProjeto: projetoAtual.areaProjeto || 'Geral'
      });
    }
  }, [projetoAtual, reset]);
  
  const aoEnviar = async (dados: DadosProjeto) => {
    if (!projetoAtual) return;
    
    try {
      // Manter os dados originais que não estão no formulário
      const dadosAtualizados = {
        ...projetoAtual,
        ...dados,
        dataAtualizacao: new Date().toISOString()
      };
      
      // Salvar o projeto atualizado
      await salvarProjeto(dadosAtualizados);
      
      // Mostrar notificação de sucesso
      toast({
        title: 'Projeto atualizado com sucesso!',
        description: 'Você será redirecionado para a lista de projetos.'
      });
      
      // Redirecionar para a lista de projetos após um breve delay
      setTimeout(() => {
        navigate('/meus-projetos');
      }, 1500);
    } catch (erro) {
      // Mostrar notificação de erro
      toast({
        title: 'Erro ao atualizar projeto',
        description: erro instanceof Error ? erro.message : 'Ocorreu um erro ao atualizar o projeto.',
        variant: 'destructive'
      });
    }
  };
  
  // Se estiver carregando, mostrar esqueleto
  if (carregando) {
    return (
      <div className="min-h-screen bg-gray-50">
        <CommonHeader title="Editar Projeto" description="Atualizando informações do projeto" />
        
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-3xl mx-auto">
            <Card>
              <CardHeader>
                <Skeleton className="h-8 w-3/4 mb-2" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-1/4 mb-2" />
                  <Skeleton className="h-10 w-full" />
                </div>
                
                <div className="space-y-2">
                  <Skeleton className="h-4 w-1/4 mb-2" />
                  <Skeleton className="h-24 w-full" />
                </div>
                
                <div className="space-y-2">
                  <Skeleton className="h-4 w-1/4 mb-2" />
                  <Skeleton className="h-32 w-full" />
                </div>
                
                <div className="space-y-2">
                  <Skeleton className="h-4 w-1/4 mb-2" />
                  <Skeleton className="h-10 w-full" />
                </div>
              </CardContent>
              
              <CardFooter className="flex justify-between">
                <Skeleton className="h-10 w-24" />
                <Skeleton className="h-10 w-32" />
              </CardFooter>
            </Card>
          </div>
        </main>
      </div>
    );
  }
  
  // Se houver erro ou o projeto não for encontrado
  if (erro || !projetoAtual) {
    return (
      <div className="min-h-screen bg-gray-50">
        <CommonHeader title="Erro" description="Não foi possível carregar o projeto" />
        
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Projeto não encontrado</h1>
            <p className="text-gray-600 mb-6">
              {erro ? String(erro) : 'O projeto solicitado não existe ou foi removido.'}
            </p>
            <Button onClick={() => navigate('/meus-projetos')}>
              Voltar para Meus Projetos
            </Button>
          </div>
        </main>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <CommonHeader title="Editar Projeto" description="Atualize as informações do seu projeto" />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Editar Projeto</CardTitle>
              <CardDescription>
                Atualize os dados do seu projeto para encontrar editais mais compatíveis
              </CardDescription>
            </CardHeader>
            
            <form onSubmit={handleSubmit(aoEnviar)}>
              <CardContent className="space-y-6">
                {/* Nome do Projeto */}
                <div className="space-y-2">
                  <label htmlFor="nomeProjeto" className="text-sm font-medium">
                    Nome do Projeto <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="nomeProjeto"
                    placeholder="Digite o nome do seu projeto"
                    {...register('nomeProjeto')}
                    className={errors.nomeProjeto ? 'border-red-500' : ''}
                  />
                  {errors.nomeProjeto && (
                    <p className="text-sm text-red-500">{errors.nomeProjeto.message}</p>
                  )}
                </div>
                
                {/* Objetivo Principal */}
                <div className="space-y-2">
                  <label htmlFor="objetivoPrincipal" className="text-sm font-medium">
                    Objetivo Principal <span className="text-red-500">*</span>
                  </label>
                  <Textarea
                    id="objetivoPrincipal"
                    placeholder="Descreva o objetivo principal do seu projeto"
                    {...register('objetivoPrincipal')}
                    className={`min-h-[100px] ${errors.objetivoPrincipal ? 'border-red-500' : ''}`}
                  />
                  {errors.objetivoPrincipal && (
                    <p className="text-sm text-red-500">{errors.objetivoPrincipal.message}</p>
                  )}
                </div>
                
                {/* Descrição */}
                <div className="space-y-2">
                  <label htmlFor="descricao" className="text-sm font-medium">
                    Descrição Detalhada <span className="text-red-500">*</span>
                  </label>
                  <Textarea
                    id="descricao"
                    placeholder="Descreva detalhadamente o seu projeto"
                    {...register('descricao')}
                    className={`min-h-[150px] ${errors.descricao ? 'border-red-500' : ''}`}
                  />
                  {errors.descricao && (
                    <p className="text-sm text-red-500">{errors.descricao.message}</p>
                  )}
                </div>
                
                {/* Área do Projeto */}
                <div className="space-y-2">
                  <label htmlFor="areaProjeto" className="text-sm font-medium">
                    Área do Projeto <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="areaProjeto"
                    {...register('areaProjeto')}
                    className={`w-full p-2 border rounded-md ${errors.areaProjeto ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="Geral">Geral</option>
                    <option value="Educação">Educação</option>
                    <option value="Saúde">Saúde</option>
                    <option value="Meio Ambiente">Meio Ambiente</option>
                    <option value="Tecnologia">Tecnologia</option>
                    <option value="Cultura">Cultura</option>
                    <option value="Esporte">Esporte</option>
                    <option value="Assistência Social">Assistência Social</option>
                    <option value="Outro">Outro</option>
                  </select>
                  {errors.areaProjeto && (
                    <p className="text-sm text-red-500">{errors.areaProjeto.message}</p>
                  )}
                </div>
                
                {/* Informações adicionais */}
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-sm text-gray-500">
                    <strong>Data de Criação:</strong> {projetoAtual.dataCriacao ? new Date(projetoAtual.dataCriacao).toLocaleDateString('pt-BR') : 'Não informada'}
                  </p>
                  {projetoAtual.dataAtualizacao && (
                    <p className="text-sm text-gray-500">
                      <strong>Última Atualização:</strong> {new Date(projetoAtual.dataAtualizacao).toLocaleDateString('pt-BR')}
                    </p>
                  )}
                </div>
              </CardContent>
              
              <CardFooter className="flex justify-between">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/meus-projetos')}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  className="bg-[#DCF763] text-black hover:bg-[#DCF763]/90"
                  disabled={isSubmitting || salvando}
                >
                  {salvando ? 'Salvando...' : 'Atualizar Projeto'}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default EditarProjeto;
