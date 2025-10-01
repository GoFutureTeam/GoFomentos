import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

const esquemaEsqueciSenha = z.object({
  email: z.string().email('Email inválido')
});

type DadosEsqueciSenha = z.infer<typeof esquemaEsqueciSenha>;

const EsqueciSenha: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<DadosEsqueciSenha>({
    resolver: zodResolver(esquemaEsqueciSenha)
  });
  
  const aoEnviar = async (dados: DadosEsqueciSenha) => {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: 'Email enviado!',
        description: 'Verifique sua caixa de entrada para redefinir sua senha.',
      });
      
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (erro) {
      toast({
        title: 'Erro',
        description: 'Não foi possível enviar o email. Tente novamente.',
        variant: 'destructive',
      });
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Esqueci minha senha</CardTitle>
          <CardDescription className="text-center">
            Digite seu email para receber instruções de recuperação
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(aoEnviar)} className="space-y-4">
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
            
            <Button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#DCF763] text-black hover:bg-[#DCF763]/90 font-semibold"
            >
              {isSubmitting ? 'Enviando...' : 'Enviar instruções'}
            </Button>
            
            <div className="text-center">
              <a href="/login" className="text-sm text-gray-600 hover:text-gray-900">
                Voltar para o login
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default EsqueciSenha;