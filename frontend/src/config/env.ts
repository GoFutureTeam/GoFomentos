/**
 * Validação e configuração de variáveis de ambiente
 * Garante que a aplicação não inicie com configuração inválida
 */

interface EnvConfig {
  apiUrl: string;
  environment: 'development' | 'production' | 'test';
  appName: string;
  version: string;
}

function validateEnv(): EnvConfig {
  const apiUrl = import.meta.env.VITE_API_URL;
  
  // Validar URL da API
  if (!apiUrl) {
    throw new Error(
      '❌ ERRO DE CONFIGURAÇÃO: VITE_API_URL não está definida no arquivo .env\n' +
      'Crie um arquivo .env na raiz do projeto com:\n' +
      'VITE_API_URL=http://localhost:8002'
    );
  }

  // Validar formato da URL
  try {
    new URL(apiUrl);
  } catch {
    throw new Error(
      `❌ ERRO DE CONFIGURAÇÃO: VITE_API_URL inválida: ${apiUrl}\n` +
      'Deve ser uma URL completa, ex: http://localhost:8002'
    );
  }

  const environment = (import.meta.env.MODE || 'development') as EnvConfig['environment'];

  console.log('✅ Configuração validada:');
  console.log(`   - API URL: ${apiUrl}`);
  console.log(`   - Ambiente: ${environment}`);

  return {
    apiUrl,
    environment,
    appName: import.meta.env.VITE_APP_NAME || 'GoFomentos',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  };
}

export const env = validateEnv();
