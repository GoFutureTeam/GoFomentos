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
import { DadosProjeto } from '@/services/apiProjeto';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';

// Esquema de validação para o formulário
const esquemaProjeto = z.object({
  titulo_projeto: z.string().min(3, 'O título do projeto deve ter pelo menos 3 caracteres'),
  objetivo_principal: z.string().min(10, 'O objetivo deve ter pelo menos 10 caracteres'),
  nome_empresa: z.string().min(2, 'O nome da empresa deve ser informado'),
  resumo_atividades: z.string().min(10, 'O resumo das atividades deve ter pelo menos 10 caracteres'),
  cnae: z.string().min(1, 'O CNAE deve ser informado')
});

type FormularioProjeto = z.infer<typeof esquemaProjeto>;

const NovoProjeto: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { salvarProjeto, salvando } = useProjetoPortugues();
  const { usuario } = useAutenticacaoPortugues();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormularioProjeto>({
    resolver: zodResolver(esquemaProjeto)
  });
  
  const aoEnviar = async (dados: FormularioProjeto) => {
    try {
      // Criar objeto com todos os dados necessários
      const dadosCompletos: DadosProjeto = {
        titulo_projeto: dados.titulo_projeto,
        objetivo_principal: dados.objetivo_principal,
        nome_empresa: dados.nome_empresa,
        resumo_atividades: dados.resumo_atividades,
        cnae: dados.cnae,
        user_id: usuario?.id || ''
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
                {/* Título do Projeto */}
                <div className="space-y-2">
                  <label htmlFor="titulo_projeto" className="text-sm font-medium">
                    Título do Projeto <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="titulo_projeto"
                    placeholder="Digite o título do seu projeto"
                    {...register('titulo_projeto')}
                    className={errors.titulo_projeto ? 'border-red-500' : ''}
                  />
                  {errors.titulo_projeto && (
                    <p className="text-sm text-red-500">{errors.titulo_projeto.message}</p>
                  )}
                </div>
                
                {/* Objetivo Principal */}
                <div className="space-y-2">
                  <label htmlFor="objetivo_principal" className="text-sm font-medium">
                    Objetivo Principal <span className="text-red-500">*</span>
                  </label>
                  <Textarea
                    id="objetivo_principal"
                    placeholder="Descreva o objetivo principal do seu projeto"
                    {...register('objetivo_principal')}
                    className={`min-h-[100px] ${errors.objetivo_principal ? 'border-red-500' : ''}`}
                  />
                  {errors.objetivo_principal && (
                    <p className="text-sm text-red-500">{errors.objetivo_principal.message}</p>
                  )}
                </div>
                
                {/* Nome da Empresa */}
                <div className="space-y-2">
                  <label htmlFor="nome_empresa" className="text-sm font-medium">
                    Nome da Empresa <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="nome_empresa"
                    placeholder="Digite o nome da empresa"
                    {...register('nome_empresa')}
                    className={errors.nome_empresa ? 'border-red-500' : ''}
                  />
                  {errors.nome_empresa && (
                    <p className="text-sm text-red-500">{errors.nome_empresa.message}</p>
                  )}
                </div>
                
                {/* Resumo das Atividades */}
                <div className="space-y-2">
                  <label htmlFor="resumo_atividades" className="text-sm font-medium">
                    Resumo das Atividades da Empresa <span className="text-red-500">*</span>
                  </label>
                  <Textarea
                    id="resumo_atividades"
                    placeholder="Descreva as atividades da empresa"
                    {...register('resumo_atividades')}
                    className={`min-h-[150px] ${errors.resumo_atividades ? 'border-red-500' : ''}`}
                  />
                  {errors.resumo_atividades && (
                    <p className="text-sm text-red-500">{errors.resumo_atividades.message}</p>
                  )}
                </div>
                
                {/* CNAE */}
                <div className="space-y-2">
                  <label htmlFor="cnae" className="text-sm font-medium">
                    CNAE <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="cnae"
                    placeholder="Digite o código CNAE"
                    {...register('cnae')}
                    className={errors.cnae ? 'border-red-500' : ''}
                  />
                  {errors.cnae && (
                    <p className="text-sm text-red-500">{errors.cnae.message}</p>
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
