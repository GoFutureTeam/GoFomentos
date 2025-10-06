import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';
import { useToast } from '@/hooks/use-toast';
import { authApi } from '@/services/apiAuth';

const esquemaRegistro = z.object({
  nome: z.string().min(2, 'O nome deve ter pelo menos 2 caracteres'),
  sobrenome: z.string().min(2, 'O sobrenome deve ter pelo menos 2 caracteres'),
  email: z.string().email('Email inválido'),
  confirmarEmail: z.string().email('Email inválido'),
  senha: z.string().min(6, 'A senha deve ter pelo menos 6 caracteres'),
  confirmarSenha: z.string().min(6, 'A confirmação de senha deve ter pelo menos 6 caracteres')
}).refine((dados) => dados.email === dados.confirmarEmail, {
  message: 'Os emails não coincidem',
  path: ['confirmarEmail']
}).refine((dados) => dados.senha === dados.confirmarSenha, {
  message: 'As senhas não coincidem',
  path: ['confirmarSenha']
});

type DadosRegistro = z.infer<typeof esquemaRegistro>;

const Registro: React.FC = () => {
  const { entrar } = useAutenticacaoPortugues();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<DadosRegistro>({
    resolver: zodResolver(esquemaRegistro)
  });
  
  const aoEnviar = async (dados: DadosRegistro) => {
    try {
      // 1. Registrar usuário
      await authApi.register({
        email: dados.email,
        name: `${dados.nome} ${dados.sobrenome}`,
        password: dados.senha
      });
      
      // 2. Fazer login automaticamente
      const resposta = await authApi.login({
        email: dados.email,
        password: dados.senha
      });
      
      entrar(
        {
          id: resposta.user.id,
          nome: resposta.user.name,
          email: resposta.user.email
        },
        resposta.access_token
      );
      
      toast({
        title: 'Cadastro realizado!',
        description: 'Bem-vindo ao GoFomentos!',
      });
      
      navigate('/');
    } catch (erro) {
      toast({
        title: 'Erro no cadastro',
        description: erro instanceof Error ? erro.message : 'Não foi possível realizar o cadastro. Tente novamente.',
        variant: 'destructive',
      });
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-8">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Criar conta</CardTitle>
          <CardDescription className="text-center">
            Preencha os dados abaixo para se cadastrar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(aoEnviar)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="nome" className="text-sm font-medium">Nome</label>
                <input
                  id="nome"
                  type="text"
                  {...register('nome')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763]"
                  placeholder="João"
                />
                {errors.nome && (
                  <p className="text-red-500 text-sm">{errors.nome.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <label htmlFor="sobrenome" className="text-sm font-medium">Sobrenome</label>
                <input
                  id="sobrenome"
                  type="text"
                  {...register('sobrenome')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763]"
                  placeholder="Silva"
                />
                {errors.sobrenome && (
                  <p className="text-red-500 text-sm">{errors.sobrenome.message}</p>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">Email</label>
              <input
                id="email"
                type="email"
                {...register('email')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763]"
                placeholder="seu@email.com"
              />
              {errors.email && (
                <p className="text-red-500 text-sm">{errors.email.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="confirmarEmail" className="text-sm font-medium">Confirmar Email</label>
              <input
                id="confirmarEmail"
                type="email"
                {...register('confirmarEmail')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763]"
                placeholder="seu@email.com"
              />
              {errors.confirmarEmail && (
                <p className="text-red-500 text-sm">{errors.confirmarEmail.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="senha" className="text-sm font-medium">Senha</label>
              <input
                id="senha"
                type="password"
                {...register('senha')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763]"
                placeholder="••••••"
              />
              {errors.senha && (
                <p className="text-red-500 text-sm">{errors.senha.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="confirmarSenha" className="text-sm font-medium">Confirmar Senha</label>
              <input
                id="confirmarSenha"
                type="password"
                {...register('confirmarSenha')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763]"
                placeholder="••••••"
              />
              {errors.confirmarSenha && (
                <p className="text-red-500 text-sm">{errors.confirmarSenha.message}</p>
              )}
            </div>
            
            <Button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#DCF763] text-black hover:bg-[#DCF763]/90 font-semibold"
            >
              {isSubmitting ? 'Cadastrando...' : 'Cadastrar'}
            </Button>
            
            <div className="text-center">
              <span className="text-sm text-gray-600">Já tem uma conta? </span>
              <a href="/login" className="text-sm text-gray-900 font-medium hover:underline">
                Fazer login
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Registro;