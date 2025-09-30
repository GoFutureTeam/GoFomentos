import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { ProjetoProps } from './types';
import { useProjetoPortugues } from '@/hooks/useProjetoPortugues';
import { useAutenticacaoPortugues } from '@/hooks/useAutenticacaoPortugues';
import { Button } from '@/components/ui/button';
import { FileUpload } from '../FileUpload';

const projectFormSchema = z.object({
  projectTitle: z.string().min(1, 'Título do projeto é obrigatório'),
  projectObjective: z.string().min(1, 'Objetivo do projeto é obrigatório'),
  companyName: z.string().optional(),
  companyActivities: z.string().min(1, 'Resumo das atividades é obrigatório'),
  cnae: z.string().min(1, 'CNAE é obrigatório')
});

type ProjectFormData = z.infer<typeof projectFormSchema>;

export const ProjectForm: React.FC<ProjetoProps> = ({ projetoInicial }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const { autenticado } = useAutenticacaoPortugues();
  const { salvarProjeto, salvando } = useProjetoPortugues();
  
  const {
    register,
    handleSubmit,
    getValues,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectFormSchema),
    defaultValues: {
      projectTitle: projetoInicial?.nomeProjeto || '',
      projectObjective: projetoInicial?.objetivoPrincipal || '',
      companyName: '',
      companyActivities: projetoInicial?.descricao || '',
      cnae: ''
    }
  });
  
  // Atualizar o formulário quando um projeto for selecionado
  useEffect(() => {
    if (projetoInicial) {
      reset({
        projectTitle: projetoInicial.nomeProjeto,
        projectObjective: projetoInicial.objetivoPrincipal || '',
        companyName: '',
        companyActivities: projetoInicial.descricao,
        cnae: ''
      });
    }
  }, [projetoInicial, reset]);
  
  const handleSaveProjeto = () => {
    const formData = getValues();
    const projetoData = {
      ...(projetoInicial || {}),
      nomeProjeto: formData.projectTitle,
      descricao: formData.companyActivities,
      objetivoPrincipal: formData.projectObjective,
      areaProjeto: projetoInicial?.areaProjeto || 'Geral',
      dataCriacao: projetoInicial?.dataCriacao || new Date().toISOString(),
      dataAtualizacao: new Date().toISOString()
    };
    salvarProjeto(projetoData);
    
    // Redirecionar para a página de Meus Projetos após salvar
    setTimeout(() => {
      navigate('/meus-projetos');
    }, 500);
  };
  
  const onSubmit = async (data: ProjectFormData) => {
    console.log('Analisando compatibilidade...', data);
    // Implementar lógica de análise de compatibilidade aqui
  };

  return (
    <div className="bg-white flex flex-col items-stretch max-md:max-w-full relative pb-0">
      <header className="text-center pt-[5px]">
        <h2 className="text-[rgba(67,80,88,1)] text-4xl font-extrabold">
          {projetoInicial ? 'Editar Projeto' : 'Faça o match do seu projeto'}
        </h2>
        <p className="text-black text-2xl font-medium leading-[30px] mt-3.5 max-md:max-w-full">
          Preencha os dados abaixo para encontrar os editais mais compatíveis com seu projeto.
        </p>
      </header>

      <div className="flex flex-col relative min-h-[1400px] w-full items-center mt-[60px] pb-[59px] px-20 max-md:max-w-full max-md:mt-10 max-md:px-5">
        <div className="relative z-10 mt-[-50px] w-[900px] max-w-full">
          <form onSubmit={handleSubmit(onSubmit)} className="bg-white shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] text-xl pb-[32px] rounded-[39px] max-md:max-w-full overflow-hidden">
            <div className="w-full h-[23px] bg-[#DCF763] rounded-t-[39px] -mx-0"></div>
            
            <div className="flex flex-col mt-6 px-[40px] max-md:max-w-full max-md:mt-5 max-md:px-5">
              <h3 className="text-[rgba(67,80,88,1)] ml-[25px] max-md:ml-2.5 text-3xl font-extrabold mb-4">
                Dados do Projeto
              </h3>
              <div className="mt-[16px]">
                <label htmlFor="projectTitle" className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-[25px] max-md:ml-2.5 block">
                  Título do projeto
                </label>
                <div className="bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] self-stretch flex flex-col items-stretch text-[#000001] font-medium justify-center mt-[12px] px-[20px] py-[12px] rounded-[25px] max-md:max-w-full max-md:px-5">
                  <input 
                    id="projectTitle"
                    type="text" 
                    {...register('projectTitle')}
                    className="bg-transparent border-none outline-none w-full text-[#000001] placeholder:text-[rgba(67,80,88,1)]"
                    placeholder="Informe o nome oficial ou provisório do seu projeto"
                  />
                </div>
                {errors.projectTitle && (
                  <p className="text-red-500 text-sm mt-2 ml-[25px]">{errors.projectTitle.message}</p>
                )}
              </div>

              <div className="mt-[24px] max-md:mt-5">
                <label htmlFor="projectObjective" className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-[25px] max-md:ml-2.5 block">
                  Objetivo Principal do Projeto
                </label>
                <div className="bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] self-stretch flex flex-col text-[#000001] font-medium mt-[12px] pt-[12px] pb-[12px] px-[20px] rounded-[25px] max-md:max-w-full max-md:px-5">
                  <textarea 
                    id="projectObjective"
                    {...register('projectObjective')}
                    className="bg-transparent border-none outline-none w-full resize-none text-[#000001] placeholder:text-[rgba(67,80,88,1)] min-h-[60px]"
                    placeholder="Resuma a principal meta que o projeto deseja alcançar"
                  />
                </div>
                {errors.projectObjective && (
                  <p className="text-red-500 text-sm mt-2 ml-[25px]">{errors.projectObjective.message}</p>
                )}
              </div>

              <h3 className="text-[rgba(67,80,88,1)] ml-6 mt-6 max-md:ml-2.5 max-md:mt-5 font-extrabold text-3xl">
                Dados da Empresa
              </h3>

              <div className="mt-[16px]">
                <label htmlFor="companyName" className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-[25px] max-md:ml-2.5 block">
                  Nome da Empresa
                </label>
                <div className="bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] self-stretch flex flex-col text-[#000001] font-medium justify-center mt-[12px] px-[20px] py-[12px] rounded-[25px] max-md:max-w-full max-md:px-5">
                  <input 
                    id="companyName"
                    type="text" 
                    {...register('companyName')}
                    className="bg-transparent border-none outline-none w-full text-[#000001] placeholder:text-[rgba(67,80,88,1)]"
                    placeholder="Preencha com a razão social ou nome fantasia da empresa"
                  />
                </div>
              </div>

              <div className="mt-[24px] max-md:mt-5">
                <label htmlFor="companyActivities" className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-[25px] max-md:ml-2.5 block">
                  Resumo das Atividades da Empresa <span className="text-red-500">*</span>
                </label>
                <div className="bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] self-stretch text-[#000001] font-medium mt-[12px] pt-[12px] pb-[12px] px-[20px] rounded-[25px] max-md:max-w-full max-md:px-5">
                  <textarea 
                    id="companyActivities"
                    {...register('companyActivities')}
                    className="bg-transparent border-none outline-none w-full resize-none text-[#000001] placeholder:text-[rgba(67,80,88,1)] min-h-[60px]"
                    placeholder="Descreva brevemente o que sua empresa faz"
                  />
                </div>
                {errors.companyActivities && (
                  <p className="text-red-500 text-sm mt-2 ml-[25px]">{errors.companyActivities.message}</p>
                )}
              </div>

              <div className="mt-[24px] max-md:mt-5">
                <label htmlFor="cnae" className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-[25px] max-md:ml-2.5 block">
                  CNAE <span className="text-red-500">*</span>
                </label>
                <div className="bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] self-stretch flex flex-col items-stretch text-[#000001] font-medium justify-center mt-[12px] px-[20px] py-[12px] rounded-[25px] max-md:max-w-full max-md:px-5">
                  <input 
                    id="cnae"
                    type="text" 
                    {...register('cnae')}
                    className="bg-transparent border-none outline-none w-full text-[#000001] placeholder:text-[rgba(67,80,88,1)]"
                    placeholder="Informe o código CNAE da sua empresa"
                  />
                </div>
                {errors.cnae && (
                  <p className="text-red-500 text-sm mt-2 ml-[25px]">{errors.cnae.message}</p>
                )}
              </div>
          
              <div className="mt-[24px] max-md:mt-5">
                <h4 className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-6 max-md:ml-2.5">
                  Envio de documentos
                </h4>
                <p className="text-[rgba(67,80,88,1)] font-medium ml-6 mt-3.5 max-md:max-w-full">
                  Caso tenha o descritivo do projeto ou o cartão CNPJ da empresa
                </p>
                <FileUpload onFileSelect={setUploadedFile} />
              </div>

              <p className="text-[rgba(67,80,88,1)] text-lg font-semibold ml-6 mt-6 max-md:ml-2.5">
                Os campos com <span className="font-extrabold text-red-500">*</span> na descrição são obrigatórios
              </p>
          
              <div className="flex flex-col sm:flex-row gap-4 justify-center mt-9">
                {autenticado && (
                  <button 
                    type="button" 
                    onClick={handleSaveProjeto}
                    disabled={isSubmitting || salvando}
                    className="bg-[rgba(67,80,88,1)] self-center flex items-center text-white font-semibold text-center justify-center px-[24px] py-[16px] rounded-[24px] max-md:px-4 hover:bg-[rgba(67,80,88,0.9)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-base"
                  >
                    {salvando ? 'Salvando...' : projetoInicial ? 'Atualizar Projeto' : 'Salvar Projeto'}
                  </button>
                )}
                
                <button 
                  type="submit"
                  disabled={isSubmitting}
                  className="bg-[#DCF763] self-center flex items-center text-black font-extrabold text-center justify-center px-[30px] py-[21px] rounded-[28px] max-md:px-5 hover:bg-[#DCF763]/90 transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? 'Analisando...' : 'Analisar Compatibilidade'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};