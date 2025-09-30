import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useToast } from '@/hooks/use-toast';
import { SuccessMessage } from '../SuccessMessage';
import { ProjectData } from '@/hooks/useMatching';
import { useLocation, useNavigate } from 'react-router-dom';

const emailSignupSchema = z.object({
  email: z.string().email('Email inválido').min(1, 'Email é obrigatório')
});

type EmailSignupData = z.infer<typeof emailSignupSchema>;

export const EmailSignup: React.FC = () => {
  const location = useLocation();
  const projectData = location.state?.projectData as ProjectData | undefined;
  const { toast } = useToast();
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    reset,
    formState: {
      errors,
      isSubmitting
    }
  } = useForm<EmailSignupData>({
    resolver: zodResolver(emailSignupSchema)
  });
  const onSubmit = async (data: EmailSignupData) => {
    try {
      const formData = new FormData();
      formData.append('email', data.email);
      
      // Se há dados do projeto, incluí-los no envio
      if (projectData) {
        formData.append('projectTitle', projectData.projectTitle);
        formData.append('projectObjective', projectData.projectObjective);
        formData.append('companyName', projectData.companyName || '');
        formData.append('companyActivities', projectData.companyActivities);
        formData.append('cnae', projectData.cnae);
        if (projectData.file) {
          formData.append('file', projectData.file);
        }
      }

      const response = await fetch('https://n8n.gofuture.unifacisa.edu.br/webhook/9cf3feef-832b-4bb7-b60a-04513055d2f6', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Falha na requisição');
      }

      // console.log('Email cadastrado:', data.email);
      
      reset(); // Limpa o formulário
      setShowSuccessModal(true);
    } catch (error) {
      // console.error('Error registering email:', error);
      toast({
        variant: "destructive",
        title: "Erro",
        description: "Erro ao cadastrar email. Tente novamente.",
      });
    }
  };

  const closeModalAndRedirect = () => {
    setShowSuccessModal(false);
    navigate('/');
  };

  return (
    <>
      <section className="bg-white px-4 py-[48px]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-black text-2xl md:text-3xl font-bold mb-6">
            Seja avisado automaticamente sempre que um novo<br />
            edital compatível com o seu projeto for publicado.
          </h2>
          
          <div className="bg-[rgba(67,80,88,1)] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] w-[900px] max-w-full text-xl font-extrabold mt-[58px] pb-[34px] rounded-[39px] max-md:mt-10 overflow-hidden mx-auto">
            <div className="w-full h-[23px] bg-[#DCF763] rounded-t-[39px] -mx-0"></div>
            <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col items-stretch mt-[35px] px-[61px] max-md:max-w-full max-md:px-5">
              <label htmlFor="email" className="text-white text-[32px] text-left mx-[32px]">
                E-mail corporativo
              </label>
              <div className="mt-[33px]">
                <input 
                  {...register('email')}
                  id="email" 
                  type="email" 
                  placeholder="Preencha com o email que deseja receber as notificações" 
                  aria-describedby={errors.email ? 'email-error' : undefined} 
                  className="shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] w-full text-[#FAFAFA] font-medium rounded-[35px] focus:outline-none focus:ring-2 focus:ring-white bg-gray-600 px-[38px] py-[18px] placeholder-[#FAFAFA] [&:-webkit-autofill]:!bg-gray-600 [&:-webkit-autofill]:!text-[#FAFAFA] [&:-webkit-autofill]:shadow-[inset_0_0_0px_1000px_rgb(75,85,99)]"
                  style={{
                    WebkitTextFillColor: '#FAFAFA'
                  }}
                />
                {errors.email && <p id="email-error" className="text-red-300 text-sm mt-2 ml-[37px] max-md:ml-2.5" role="alert">
                    {errors.email.message}
                  </p>}
              </div>
              <button type="submit" disabled={isSubmitting} className="bg-white self-center flex w-96 max-w-full flex-col items-stretch text-black text-center justify-center mt-9 rounded-[28px] hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap py-[18px] px-[38px] my-[3px]">
                {isSubmitting ? "Cadastrando..." : "Cadastrar para monitoramento"}
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Modal de Sucesso */}
      {showSuccessModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
          onClick={closeModalAndRedirect}
        >
          <div 
            className="relative"
            onClick={(e) => e.stopPropagation()}
          >
            <SuccessMessage 
              title="Projeto salvo com sucesso!"
              description="Você será avisado por e-mail assim que surgirem oportunidades."
            />
            <button
              onClick={closeModalAndRedirect}
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 text-2xl font-bold p-2"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </>
  );
};