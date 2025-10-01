import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';
import { useToast } from '@/hooks/use-toast';

// Esquema de validação para o formulário
const esquemaLogin = z.object({
  email: z.string().email('Email inválido'),
  senha: z.string().min(6, 'A senha deve ter pelo menos 6 caracteres')
});

type DadosLogin = z.infer<typeof esquemaLogin>;

const Login: React.FC = () => {
  const { entrar } = useAutenticacaoPortugues();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<DadosLogin>({
    resolver: zodResolver(esquemaLogin)
  });
  
  const aoEnviar = async (dados: DadosLogin) => {
    try {
      // Simulação de chamada à API
      // Em uma aplicação real, isso seria uma chamada à API de autenticação
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simular resposta da API
      const respostaSimulada = {
        usuario: {
          id: '1',
          nome: 'Usuário Teste',
          email: dados.email
        },
        token: 'token-simulado-123456'
      };
      
      entrar(respostaSimulada.usuario, respostaSimulada.token);
      
      // Notificar sucesso
      toast({
        title: 'Login realizado com sucesso!',
        description: `Bem-vindo de volta, ${respostaSimulada.usuario.nome}!`
      });
      
      // Redirecionar para a página inicial
      navigate('/');
    } catch (erro) {
      console.error('Erro ao fazer login:', erro);
      toast({
        title: 'Erro ao fazer login',
        description: 'Verifique suas credenciais e tente novamente.',
        variant: 'destructive'
      });
    }
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Login</CardTitle>
          <CardDescription>
            Entre com suas credenciais para acessar sua conta
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit(aoEnviar)} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">Email</label>
              <Input
                id="email"
                type="email"
                placeholder="seu.email@exemplo.com"
                {...register('email')}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="senha" className="text-sm font-medium">Senha</label>
              <Input
                id="senha"
                type="password"
                placeholder="******"
                {...register('senha')}
                className={errors.senha ? 'border-red-500' : ''}
              />
              {errors.senha && (
                <p className="text-sm text-red-500">{errors.senha.message}</p>
              )}
            </div>
            
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
        </CardContent>
        
        <CardFooter className="flex flex-col space-y-2">
          <div className="text-sm text-center">
            Não tem uma conta?{' '}
            <a 
              href="/registro" 
              className="text-blue-600 hover:underline"
              onClick={(e) => {
                e.preventDefault();
                navigate('/registro');
              }}
            >
              Registre-se
            </a>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;
