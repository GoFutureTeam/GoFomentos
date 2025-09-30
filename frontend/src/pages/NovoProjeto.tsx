import React from 'react';
import { useNavigate } from 'react-router-dom';
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

// Esquema de validação para o formulário
const esquemaProjeto = z.object({
  nomeProjeto: z.string().min(3, 'O nome do projeto deve ter pelo menos 3 caracteres'),
  descricao: z.string().min(10, 'A descrição deve ter pelo menos 10 caracteres'),
  objetivoPrincipal: z.string().min(10, 'O objetivo deve ter pelo menos 10 caracteres'),
  areaProjeto: z.string().min(2, 'A área do projeto deve ser informada')
});

type DadosProjeto = z.infer<typeof esquemaProjeto>;

const NovoProjeto: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { salvarProjeto, salvando } = useProjetoPortugues();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<DadosProjeto>({
    resolver: zodResolver(esquemaProjeto),
    defaultValues: {
      areaProjeto: 'Geral'
    }
  });
  
  const aoEnviar = async (dados: DadosProjeto) => {
    try {
      // Adicionar data de criação
      const dadosCompletos = {
        ...dados,
        dataCriacao: new Date().toISOString()
      };
      
      // Salvar o projeto
      await salvarProjeto(dadosCompletos);
      
      // Mostrar notificação de sucesso
      toast({
        title: 'Projeto criado com sucesso!',
        description: 'Você será redirecionado para a lista de projetos.'
      });
      
      // Redirecionar para a lista de projetos após um breve delay
      setTimeout(() => {
        navigate('/meus-projetos');
      }, 1500);
    } catch (erro) {
      // Mostrar notificação de erro
      toast({
        title: 'Erro ao criar projeto',
        description: erro instanceof Error ? erro.message : 'Ocorreu um erro ao criar o projeto.',
        variant: 'destructive'
      });
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <CommonHeader title="Novo Projeto" description="Crie um novo projeto para encontrar editais compatíveis" />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Criar Novo Projeto</CardTitle>
              <CardDescription>
                Preencha os dados do seu projeto para encontrar editais compatíveis
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
                  {salvando ? 'Salvando...' : 'Criar Projeto'}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default NovoProjeto;
