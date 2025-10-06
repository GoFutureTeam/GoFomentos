import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';
import { useToast } from '@/hooks/use-toast';
import { authApi } from '@/services/apiAuth';
import { validarSenha, obterForcaSenha } from '@/utils/validacoes';

const esquemaRegistro = z.object({
  nome: z.string().min(2, 'O nome deve ter pelo menos 2 caracteres'),
  sobrenome: z.string().min(2, 'O sobrenome deve ter pelo menos 2 caracteres'),
  email: z.string().email('Email inválido'),
  confirmarEmail: z.string().email('Email inválido'),
  senha: z.string()
    .min(8, 'A senha deve ter no mínimo 8 caracteres')
    .regex(/[a-z]/, 'A senha deve conter pelo menos uma letra minúscula (a-z)')
    .regex(/[A-Z]/, 'A senha deve conter pelo menos uma letra MAIÚSCULA (A-Z)')
    .regex(/[0-9]/, 'A senha deve conter pelo menos um número (0-9)')
    .regex(/[@$!%*?&]/, 'A senha deve conter pelo menos um caractere especial (@$!%*?&)'),
  confirmarSenha: z.string().min(8, 'A confirmação de senha deve ter pelo menos 8 caracteres')
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
  
  const [senhaAtual, setSenhaAtual] = useState('');
  const [forcaSenha, setForcaSenha] = useState<{ forca: 'fraca' | 'média' | 'forte'; porcentagem: number; cor: string }>({ 
    forca: 'fraca', 
    porcentagem: 0, 
    cor: '#ef4444' 
  });
  
  const { register, handleSubmit, formState: { errors, isSubmitting }, watch } = useForm<DadosRegistro>({
    resolver: zodResolver(esquemaRegistro)
  });
  
  // Observa mudanças na senha para atualizar o indicador de força
  const senha = watch('senha');
  
  React.useEffect(() => {
    if (senha) {
      setSenhaAtual(senha);
      setForcaSenha(obterForcaSenha(senha));
    }
  }, [senha]);
  
  const aoEnviar = async (dados: DadosRegistro) => {
    try {
      // 1. Registrar usuário (concatenando nome e sobrenome)
      await authApi.register({
        email: dados.email,
        name: `${dados.nome} ${dados.sobrenome}`,  // Backend espera nome completo
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
    <div className="flex items-center justify-center min-h-screen bg-[rgba(217,217,217,0.15)] p-4">
      <div className="w-full max-w-lg bg-[rgba(217,217,217,0.15)] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] rounded-[39px] overflow-hidden">
        {/* Barra superior verde */}
        <div className="bg-[#DCF763] h-[15px] w-full"></div>
        
        <div className="p-8">
          <div className="flex flex-col items-center mb-6">
            <h2 className="text-[rgba(67,80,88,1)] text-2xl font-extrabold">Criar conta</h2>
            <p className="text-[rgba(67,80,88,0.7)] text-sm font-medium mt-2 text-center">
              Preencha os dados abaixo para se cadastrar
            </p>
          </div>
          
          <form onSubmit={handleSubmit(aoEnviar)} className="space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="nome" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">
                  Nome
                </label>
                <Input
                  id="nome"
                  type="text"
                  {...register('nome')}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                    errors.nome ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="João"
                />
                {errors.nome && (
                  <p className="text-red-500 text-xs">{errors.nome.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <label htmlFor="sobrenome" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">
                  Sobrenome
                </label>
                <Input
                  id="sobrenome"
                  type="text"
                  {...register('sobrenome')}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                    errors.sobrenome ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Silva"
                />
                {errors.sobrenome && (
                  <p className="text-red-500 text-xs">{errors.sobrenome.message}</p>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="email" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">
                Email
              </label>
              <Input
                id="email"
                type="email"
                {...register('email')}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="seu@email.com"
              />
              {errors.email && (
                <p className="text-red-500 text-xs">{errors.email.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="confirmarEmail" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">
                Confirmar Email
              </label>
              <Input
                id="confirmarEmail"
                type="email"
                {...register('confirmarEmail')}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                  errors.confirmarEmail ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="seu@email.com"
              />
              {errors.confirmarEmail && (
                <p className="text-red-500 text-xs">{errors.confirmarEmail.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="senha" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">
                Senha
              </label>
              <Input
                id="senha"
                type="password"
                {...register('senha')}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                  errors.senha ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="••••••••"
              />
              
              {/* Barra de força da senha */}
              {senhaAtual && (
                <div className="mt-2 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full transition-all duration-300 ease-in-out"
                        style={{ 
                          width: `${forcaSenha.porcentagem}%`,
                          backgroundColor: forcaSenha.cor
                        }}
                      />
                    </div>
                    <span className="text-xs font-semibold capitalize" style={{ color: forcaSenha.cor }}>
                      {forcaSenha.forca}
                    </span>
                  </div>
                </div>
              )}
              
              {/* Lista de requisitos */}
              {senhaAtual && (
                <div className="mt-2 p-3 bg-gray-50 rounded-md border border-gray-200">
                  <p className="text-xs font-semibold text-gray-700 mb-2">A senha deve conter:</p>
                  <ul className="space-y-1 text-xs">
                    <li className={`flex items-center gap-2 ${senhaAtual.length >= 8 ? 'text-green-600' : 'text-gray-500'}`}>
                      <span className="font-bold">{senhaAtual.length >= 8 ? '✓' : '○'}</span>
                      Mínimo 8 caracteres
                    </li>
                    <li className={`flex items-center gap-2 ${/[a-z]/.test(senhaAtual) ? 'text-green-600' : 'text-gray-500'}`}>
                      <span className="font-bold">{/[a-z]/.test(senhaAtual) ? '✓' : '○'}</span>
                      1 letra minúscula (a-z)
                    </li>
                    <li className={`flex items-center gap-2 ${/[A-Z]/.test(senhaAtual) ? 'text-green-600' : 'text-gray-500'}`}>
                      <span className="font-bold">{/[A-Z]/.test(senhaAtual) ? '✓' : '○'}</span>
                      1 letra MAIÚSCULA (A-Z)
                    </li>
                    <li className={`flex items-center gap-2 ${/[0-9]/.test(senhaAtual) ? 'text-green-600' : 'text-gray-500'}`}>
                      <span className="font-bold">{/[0-9]/.test(senhaAtual) ? '✓' : '○'}</span>
                      1 número (0-9)
                    </li>
                    <li className={`flex items-center gap-2 ${/[@$!%*?&]/.test(senhaAtual) ? 'text-green-600' : 'text-gray-500'}`}>
                      <span className="font-bold">{/[@$!%*?&]/.test(senhaAtual) ? '✓' : '○'}</span>
                      1 caractere especial (@$!%*?&)
                    </li>
                  </ul>
                </div>
              )}
              
              {errors.senha && (
                <p className="text-red-500 text-xs mt-1">{errors.senha.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="confirmarSenha" className="text-[rgba(67,80,88,1)] text-sm font-extrabold">
                Confirmar Senha
              </label>
              <Input
                id="confirmarSenha"
                type="password"
                {...register('confirmarSenha')}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#DCF763] ${
                  errors.confirmarSenha ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="••••••••"
              />
              {watch('confirmarSenha') && watch('senha') && (
                <p className={`text-xs flex items-center gap-1 ${
                  watch('senha') === watch('confirmarSenha') ? 'text-green-600' : 'text-red-500'
                }`}>
                  <span className="font-bold">
                    {watch('senha') === watch('confirmarSenha') ? '✓' : '✗'}
                  </span>
                  {watch('senha') === watch('confirmarSenha') ? 'Senhas coincidem' : 'Senhas não coincidem'}
                </p>
              )}
              {errors.confirmarSenha && (
                <p className="text-red-500 text-xs">{errors.confirmarSenha.message}</p>
              )}
            </div>
            
            <Button
              type="submit"
              disabled={isSubmitting || (senhaAtual && !validarSenha(senhaAtual).valida)}
              className="w-full bg-[#DCF763] text-[rgba(67,80,88,1)] hover:bg-[#DCF763]/90 font-extrabold py-3 mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Cadastrando...' : 'Cadastrar'}
            </Button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-[rgba(67,80,88,0.7)] font-medium">
              Já tem uma conta?{' '}
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="text-[rgba(67,80,88,1)] font-extrabold hover:underline"
              >
                Fazer login
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Registro;