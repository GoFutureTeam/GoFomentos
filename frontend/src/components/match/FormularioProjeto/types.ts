import { DadosProjeto } from '@/services/apiProjeto';
import { UseFormRegister, FieldErrors } from 'react-hook-form';

export interface ProjetoProps {
  projetoInicial?: DadosProjeto;
}

export interface FormularioProjetoData {
  projectTitle: string;
  projectObjective: string;
  companyName?: string;
  companyActivities: string;
  cnae: string;
}

export interface FormFieldProps {
  register: UseFormRegister<FormularioProjetoData>;
  errors: FieldErrors<FormularioProjetoData>;
}
