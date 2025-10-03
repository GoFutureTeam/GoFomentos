import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';
import { useToast } from '@/hooks/use-toast';
import { authApi } from '@/services/apiAuth';

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
      // Chamada real à API
      const resposta = await authApi.login({
        email: dados.email,
        password: dados.senha
      });
      
      // Usar dados reais do backend
      entrar(
        {
          id: resposta.user.id,
          nome: resposta.user.name,
          email: resposta.user.email
        },
        resposta.access_token
      );
      
      toast({
        title: 'Login realizado com sucesso!',
        description: `Bem-vindo de volta, ${resposta.user.name}!`
      });
      
      navigate('/');
    } catch (erro) {
      console.error('Erro ao fazer login:', erro);
      toast({
        title: 'Erro ao fazer login',
        description: erro instanceof Error ? erro.message : 'Verifique suas credenciais e tente novamente.',
        variant: 'destructive'
      });
    }
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-[rgba(217,217,217,0.15)]">
      <div className="w-full max-w-md bg-[rgba(217,217,217,0.15)] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] rounded-[39px] overflow-hidden">
        {/* Barra superior verde */}
        <div className="bg-[#DCF763] h-[15px] w-full"></div>
        
        <div className="p-8">
          <div className="flex flex-col items-center mb-6">
            <h2 className="text-[rgba(67,80,88,1)] text-2xl font-extrabold">Login</h2>
            <p className="text-[rgba(67,80,88,0.7)] text-sm font-medium mt-2">
              Entre com suas credenciais para acessar sua conta
            </p>
          </div>
          
          <form onSubmit={handleSubmit(aoEnviar)} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="email" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">Email</label>
              <Input
                id="email"
                type="email"
                placeholder="seu.email@exemplo.com"
                {...register('email')}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="senha" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">Senha</label>
              <Input
                id="senha"
                type="password"
                placeholder="••••••"
                {...register('senha')}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                  errors.senha ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.senha && (
                <p className="text-sm text-red-500">{errors.senha.message}</p>
              )}
            </div>
            
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => navigate('/recuperar-senha')}
                className="text-[rgba(67,80,88,1)] text-sm font-medium hover:underline"
              >
                Esqueceu sua senha?
              </button>
            </div>
            
            <Button 
              type="submit" 
              className="w-full bg-[#DCF763] text-[rgba(67,80,88,1)] hover:bg-[#DCF763]/90 font-extrabold py-3"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-[rgba(67,80,88,0.7)] font-medium">
              Não tem uma conta?{' '}
              <button
                type="button"
                onClick={() => navigate('/registro')}
                className="text-[rgba(67,80,88,1)] font-extrabold hover:underline"
              >
                Registre-se
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
