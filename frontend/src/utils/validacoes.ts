/**
 * Utilitários de validação para formulários
 */

export interface ResultadoValidacaoSenha {
  valida: boolean;
  erros: string[];
  requisitos: {
    tamanho: boolean;
    minuscula: boolean;
    maiuscula: boolean;
    numero: boolean;
    especial: boolean;
  };
}

/**
 * Valida se a senha atende aos requisitos de segurança
 * - Mínimo 8 caracteres
 * - 1 letra minúscula (a-z)
 * - 1 letra MAIÚSCULA (A-Z)
 * - 1 número (0-9)
 * - 1 caractere especial (@$!%*?&)
 */
export const validarSenha = (senha: string): ResultadoValidacaoSenha => {
  const erros: string[] = [];
  
  const requisitos = {
    tamanho: senha.length >= 8,
    minuscula: /[a-z]/.test(senha),
    maiuscula: /[A-Z]/.test(senha),
    numero: /[0-9]/.test(senha),
    especial: /[@$!%*?&]/.test(senha),
  };

  if (!requisitos.tamanho) {
    erros.push('A senha deve ter no mínimo 8 caracteres');
  }

  if (!requisitos.minuscula) {
    erros.push('A senha deve conter pelo menos uma letra minúscula (a-z)');
  }

  if (!requisitos.maiuscula) {
    erros.push('A senha deve conter pelo menos uma letra MAIÚSCULA (A-Z)');
  }

  if (!requisitos.numero) {
    erros.push('A senha deve conter pelo menos um número (0-9)');
  }

  if (!requisitos.especial) {
    erros.push('A senha deve conter pelo menos um caractere especial (@$!%*?&)');
  }

  return {
    valida: erros.length === 0,
    erros,
    requisitos,
  };
};

/**
 * Valida se o email está em formato válido
 */
export const validarEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Calcula a força da senha baseada nos requisitos atendidos
 */
export const obterForcaSenha = (senha: string): {
  forca: 'fraca' | 'média' | 'forte';
  porcentagem: number;
  cor: string;
} => {
  let pontos = 0;

  // Tamanho
  if (senha.length >= 8) pontos += 20;
  if (senha.length >= 12) pontos += 10;
  if (senha.length >= 16) pontos += 10;

  // Variedade de caracteres
  if (/[a-z]/.test(senha)) pontos += 15;
  if (/[A-Z]/.test(senha)) pontos += 15;
  if (/[0-9]/.test(senha)) pontos += 15;
  if (/[@$!%*?&]/.test(senha)) pontos += 15;

  let forca: 'fraca' | 'média' | 'forte' = 'fraca';
  let cor = '#ef4444'; // vermelho

  if (pontos >= 80) {
    forca = 'forte';
    cor = '#10b981'; // verde
  } else if (pontos >= 50) {
    forca = 'média';
    cor = '#f59e0b'; // amarelo/laranja
  }

  return { forca, porcentagem: Math.min(pontos, 100), cor };
};

/**
 * Remove caracteres especiais de CPF/CNPJ
 */
export const limparDocumento = (documento: string): string => {
  return documento.replace(/\D/g, '');
};

/**
 * Valida CPF
 */
export const validarCPF = (cpf: string): boolean => {
  const cpfLimpo = limparDocumento(cpf);
  
  if (cpfLimpo.length !== 11) return false;
  
  // Verifica se todos os dígitos são iguais
  if (/^(\d)\1{10}$/.test(cpfLimpo)) return false;
  
  // Valida primeiro dígito verificador
  let soma = 0;
  for (let i = 0; i < 9; i++) {
    soma += parseInt(cpfLimpo.charAt(i)) * (10 - i);
  }
  let resto = 11 - (soma % 11);
  const digitoVerificador1 = resto >= 10 ? 0 : resto;
  
  if (digitoVerificador1 !== parseInt(cpfLimpo.charAt(9))) return false;
  
  // Valida segundo dígito verificador
  soma = 0;
  for (let i = 0; i < 10; i++) {
    soma += parseInt(cpfLimpo.charAt(i)) * (11 - i);
  }
  resto = 11 - (soma % 11);
  const digitoVerificador2 = resto >= 10 ? 0 : resto;
  
  return digitoVerificador2 === parseInt(cpfLimpo.charAt(10));
};

/**
 * Formata CPF: 000.000.000-00
 */
export const formatarCPF = (cpf: string): string => {
  const cpfLimpo = limparDocumento(cpf);
  return cpfLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

/**
 * Formata telefone: (00) 00000-0000 ou (00) 0000-0000
 */
export const formatarTelefone = (telefone: string): string => {
  const telefoneLimpo = limparDocumento(telefone);
  
  if (telefoneLimpo.length === 11) {
    return telefoneLimpo.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  }
  
  if (telefoneLimpo.length === 10) {
    return telefoneLimpo.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
  }
  
  return telefone;
};
