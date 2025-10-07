import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

const EsqueciSenha: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-screen bg-[rgba(217,217,217,0.15)]">
      <div className="w-full max-w-md bg-white shadow-lg rounded-[39px] overflow-hidden">
        <div className="bg-[#DCF763] h-[15px] w-full"></div>
        <div className="p-8">
          <div className="flex flex-col items-center mb-6">
            <h2 className="text-[rgba(67,80,88,1)] text-2xl font-extrabold">Esqueci minha senha</h2>
          </div>
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Funcionalidade Temporariamente Indisponível</AlertTitle>
            <AlertDescription className="mt-2 space-y-2">
              <p>A recuperação de senha ainda não está implementada no backend.</p>
              <p>Por favor, entre em contato com o administrador do sistema para redefinir sua senha.</p>
            </AlertDescription>
          </Alert>
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-[rgba(67,80,88,1)] text-white font-bold py-3 px-4 rounded-[17px] hover:bg-[rgba(67,80,88,0.9)] transition-colors"
          >
            Voltar para Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default EsqueciSenha;
