import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { authApi } from '@/services/apiAuth';

// Esquema de validação para o formulário
const esquemaRecuperarSenha = z.object({
  email: z.string().email('Email inválido')
});

type DadosRecuperarSenha = z.infer<typeof esquemaRecuperarSenha>;

const RecuperarSenha: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [enviado, setEnviado] = useState(false);
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<DadosRecuperarSenha>({
    resolver: zodResolver(esquemaRecuperarSenha)
  });
  
  const aoEnviar = async (dados: DadosRecuperarSenha) => {
    try {
      // Implementar chamada real à API quando disponível
      await authApi.requestPasswordReset({
        email: dados.email
      });
      
      setEnviado(true);
      toast({
        title: 'Email enviado',
        description: 'Verifique sua caixa de entrada para redefinir sua senha',
      });
    } catch (erro) {
      console.error('Erro ao solicitar redefinição de senha:', erro);
      toast({
        title: 'Erro ao solicitar redefinição',
        description: erro instanceof Error ? erro.message : 'Não foi possível enviar o email de redefinição. Tente novamente.',
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
            <h2 className="text-[rgba(67,80,88,1)] text-2xl font-extrabold">Recuperar Senha</h2>
            <p className="text-[rgba(67,80,88,0.7)] text-sm font-medium mt-2 text-center">
              {enviado 
                ? 'Email enviado! Verifique sua caixa de entrada.'
                : 'Informe seu email para receber um link de redefinição de senha'
              }
            </p>
          </div>
          
          {!enviado ? (
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
              
              <Button 
                type="submit" 
                className="w-full bg-[#DCF763] text-[rgba(67,80,88,1)] hover:bg-[#DCF763]/90 font-extrabold py-3"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Enviando...' : 'Enviar Link de Recuperação'}
              </Button>
            </form>
          ) : (
            <div className="mt-6">
              <Button 
                onClick={() => setEnviado(false)}
                className="w-full bg-[rgba(67,80,88,0.1)] text-[rgba(67,80,88,1)] hover:bg-[rgba(67,80,88,0.2)] font-medium mb-4"
              >
                Tentar novamente
              </Button>
            </div>
          )}
          
          <div className="mt-6 text-center">
            <p className="text-sm text-[rgba(67,80,88,0.7)] font-medium">
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="text-[rgba(67,80,88,1)] font-extrabold hover:underline"
              >
                Voltar para o login
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecuperarSenha;