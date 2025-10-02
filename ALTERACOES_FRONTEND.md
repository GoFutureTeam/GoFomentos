# 📋 DOCUMENTAÇÃO DE ALTERAÇÕES NO FRONTEND

## Data: 2025-10-02
## Responsável: Sistema de IA - Integração Frontend ↔ Backend

---

## 🎯 OBJETIVO DAS ALTERAÇÕES

Integrar o frontend React com o backend FastAPI, substituindo localStorage por chamadas reais à API, atualizando interfaces de dados e implementando autenticação JWT.

---

## ✅ ALTERAÇÕES REALIZADAS

### 1. **CRIAÇÃO DO SERVIÇO DE AUTENTICAÇÃO**

#### **Arquivo CRIADO:** `frontend/src/services/apiAuth.ts`

**Descrição:** Serviço para gerenciar autenticação com o backend (login e registro).

**Código Completo:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}

export const authApi = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao fazer login');
    }

    return response.json();
  },

  async register(userData: RegisterRequest): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao registrar');
    }

    return response.json();
  }
};
```

**Endpoints Utilizados:**
- `POST /login` - Autenticação
- `POST /api/users` - Registro de novo usuário

---

### 2. **ATUALIZAÇÃO DO CONTEXTO DE AUTENTICAÇÃO**

#### **Arquivo MODIFICADO:** `frontend/src/contexts/ContextoAutenticacao.tsx`

**Alterações:**

##### **A. Mudança na chave do token (Linhas 26, 38, 48):**

**Antes:**
```typescript
localStorage.getItem('tokenAutenticacao')
localStorage.setItem('tokenAutenticacao', token)
localStorage.removeItem('tokenAutenticacao')
```

**Depois:**
```typescript
localStorage.getItem('auth_token')
localStorage.setItem('auth_token', token)
localStorage.removeItem('auth_token')
```

**Motivo:** Padronização com o nome usado em todo o sistema.

---

### 3. **ATUALIZAÇÃO DA PÁGINA DE LOGIN**

#### **Arquivo MODIFICADO:** `frontend/src/pages/Login.tsx`

**Alterações:**

##### **A. Importação do serviço de autenticação (Linha 11):**

**Adicionado:**
```typescript
import { authApi } from '@/services/apiAuth';
```

##### **B. Substituição da simulação por chamada real (Linhas 30-63):**

**Antes (Simulação):**
```typescript
const aoEnviar = async (dados: DadosLogin) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const respostaSimulada = {
      usuario: {
        id: '1',
        nome: 'Usuário Teste',
        email: dados.email
      },
      token: 'token-simulado-123456'
    };
    
    entrar(respostaSimulada.usuario, respostaSimulada.token);
    // ...
  }
}
```

**Depois (API Real):**
```typescript
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
    toast({
      title: 'Erro ao fazer login',
      description: erro instanceof Error ? erro.message : 'Verifique suas credenciais e tente novamente.',
      variant: 'destructive'
    });
  }
};
```

---

### 4. **ATUALIZAÇÃO DA PÁGINA DE REGISTRO**

#### **Arquivo MODIFICADO:** `frontend/src/pages/Registro.tsx`

**Alterações:**

##### **A. Importação do serviço de autenticação (Linha 10):**

**Adicionado:**
```typescript
import { authApi } from '@/services/apiAuth';
```

##### **B. Substituição da simulação por chamada real (Linhas 38-75):**

**Antes (Simulação):**
```typescript
const aoEnviar = async (dados: DadosRegistro) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const respostaSimulada = {
      usuario: {
        id: '1',
        nome: `${dados.nome} ${dados.sobrenome}`,
        email: dados.email
      },
      token: 'token-simulado-123456'
    };
    
    entrar(respostaSimulada.usuario, respostaSimulada.token);
    // ...
  }
}
```

**Depois (API Real):**
```typescript
const aoEnviar = async (dados: DadosRegistro) => {
  try {
    // 1. Registrar usuário
    await authApi.register({
      email: dados.email,
      name: `${dados.nome} ${dados.sobrenome}`,
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
```

---

### 5. **ATUALIZAÇÃO DA INTERFACE DE PROJETOS**

#### **Arquivo MODIFICADO:** `frontend/src/services/apiProjeto.ts`

**Alterações:**

##### **A. Interface DadosProjeto completamente reformulada (Linhas 1-23):**

**Antes:**
```typescript
export interface DadosProjeto {
  id?: string;
  nomeProjeto: string;
  descricao: string;
  objetivoPrincipal?: string;
  areaProjeto?: string;
  orcamento?: number;
  dataInicio?: string;
  dataFim?: string;
  usuarioId?: string;
  dataCriacao?: string;
  dataAtualizacao?: string;
}
```

**Depois:**
```typescript
// Interface atualizada para corresponder ao backend
export interface DadosProjeto {
  id?: string;
  
  // Dados do Projeto
  titulo_projeto: string;
  objetivo_principal: string;
  
  // Dados da Empresa
  nome_empresa: string;
  resumo_atividades: string;
  cnae: string;
  
  // REMOVIDO: documento_url - não será usado na primeira versão
  
  // Relacionamentos
  user_id?: string;
  edital_uuid?: string;
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}
```

**Campos Removidos:**
- `nomeProjeto` → `titulo_projeto`
- `descricao` → `resumo_atividades`
- `objetivoPrincipal` → `objetivo_principal`
- `areaProjeto` (removido)
- `orcamento` (removido)
- `dataInicio` (removido - pertence ao edital)
- `dataFim` (removido - pertence ao edital)
- `usuarioId` → `user_id`
- `dataCriacao` → `created_at`
- `dataAtualizacao` → `updated_at`

**Campos Adicionados:**
- `nome_empresa` (novo)
- `cnae` (novo)
- `edital_uuid` (novo)

##### **B. Substituição do localStorage por API real:**

**Antes (localStorage):**
```typescript
class ServicoApiProjeto {
  private urlBase = '/api/v1';
  private projetosLocais: DadosProjeto[] = [];
  
  constructor() {
    const projetosSalvos = localStorage.getItem('projetos');
    if (projetosSalvos) {
      this.projetosLocais = JSON.parse(projetosSalvos);
    }
  }
  
  private salvarNoLocalStorage() {
    localStorage.setItem('projetos', JSON.stringify(this.projetosLocais));
  }
  
  async listarProjetos(): Promise<RespostaApi<DadosProjeto[]>> {
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      dados: this.projetosLocais,
      sucesso: true,
      mensagem: 'Projetos carregados com sucesso'
    };
  }
}
```

**Depois (API Real):**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ServicoApiProjeto {
  private getHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }

  async listarProjetos(): Promise<RespostaApi<DadosProjeto[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects`, {
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Erro ao listar projetos');
      }

      const dados = await response.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: 'Projetos carregados com sucesso'
      };
    } catch (erro) {
      console.error('Erro ao listar projetos:', erro);
      return {
        dados: [],
        sucesso: false,
        mensagem: `Erro ao carregar projetos: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async obterProjeto(id: string): Promise<RespostaApi<DadosProjeto>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Erro ao buscar projeto');
      }

      const dados = await response.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: 'Projeto encontrado com sucesso'
      };
    } catch (erro) {
      console.error(`Erro ao buscar projeto ${id}:`, erro);
      return {
        dados: {} as DadosProjeto,
        sucesso: false,
        mensagem: `Erro ao buscar projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async salvarProjeto(dadosProjeto: DadosProjeto): Promise<RespostaApi<DadosProjeto>> {
    try {
      const url = dadosProjeto.id 
        ? `${API_BASE_URL}/api/projects/${dadosProjeto.id}`
        : `${API_BASE_URL}/api/projects`;
      
      const method = dadosProjeto.id ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: this.getHeaders(),
        body: JSON.stringify(dadosProjeto),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao salvar projeto');
      }

      const dados = await response.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: dadosProjeto.id ? 'Projeto atualizado com sucesso' : 'Projeto criado com sucesso'
      };
    } catch (erro) {
      console.error('Erro ao salvar projeto:', erro);
      return {
        dados: dadosProjeto,
        sucesso: false,
        mensagem: `Erro ao salvar projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }

  async excluirProjeto(id: string): Promise<RespostaApi<void>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Erro ao excluir projeto');
      }

      return {
        dados: undefined,
        sucesso: true,
        mensagem: 'Projeto excluído com sucesso'
      };
    } catch (erro) {
      console.error(`Erro ao excluir projeto ${id}:`, erro);
      return {
        dados: undefined,
        sucesso: false,
        mensagem: `Erro ao excluir projeto: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
}
```

**Endpoints Utilizados:**
- `GET /api/projects` - Listar projetos
- `GET /api/projects/{id}` - Buscar projeto específico
- `POST /api/projects` - Criar projeto
- `PUT /api/projects/{id}` - Atualizar projeto
- `DELETE /api/projects/{id}` - Deletar projeto

---

### 6. **ATUALIZAÇÃO DO HOOK useProjetoPortugues**

#### **Arquivo MODIFICADO:** `frontend/src/hooks/useProjetoPortugues.ts`

**Alterações:**

##### **A. Correção do campo na notificação (Linha 50):**

**Antes:**
```typescript
description: `O projeto "${variaveis.nomeProjeto}" foi ${variaveis.id ? 'atualizado' : 'salvo'} com sucesso.`
```

**Depois:**
```typescript
description: `O projeto "${variaveis.titulo_projeto}" foi ${variaveis.id ? 'atualizado' : 'salvo'} com sucesso.`
```

**Motivo:** Campo `nomeProjeto` não existe mais, foi substituído por `titulo_projeto`.

##### **B. Remoção de comentário desnecessário (Linha 17):**

**Antes:**
```typescript
data: projetos = [], // comentario
```

**Depois:**
```typescript
data: projetos = [],
```

---

### 7. **ATUALIZAÇÃO DO FORMULÁRIO DE PROJETO**

#### **Arquivo MODIFICADO:** `frontend/src/components/match/FormularioProjeto/index.tsx`

**Alterações:**

##### **A. Importações atualizadas (Linhas 10-12):**

**Adicionado:**
```typescript
import { DadosProjeto } from '@/services/apiProjeto';
```

**Comentado:**
```typescript
// REMOVIDO: Upload de documento não será usado na primeira versão
// import { FileUpload } from '../FileUpload';
```

##### **B. Estado de upload removido (Linhas 25-26):**

**Antes:**
```typescript
const [uploadedFile, setUploadedFile] = useState<File | null>(null);
```

**Depois:**
```typescript
// REMOVIDO: Upload de documento não será usado na primeira versão
// const [uploadedFile, setUploadedFile] = useState<File | null>(null);
```

##### **C. Atualização do hook de autenticação (Linha 29):**

**Antes:**
```typescript
const { autenticado } = useAutenticacaoPortugues();
```

**Depois:**
```typescript
const { autenticado, usuario } = useAutenticacaoPortugues();
```

**Motivo:** Necessário para pegar o `usuario.id` ao salvar o projeto.

##### **D. Valores padrão do formulário atualizados (Linhas 40-45):**

**Antes:**
```typescript
defaultValues: {
  projectTitle: projetoInicial?.nomeProjeto || '',
  projectObjective: projetoInicial?.objetivoPrincipal || '',
  companyName: '',
  companyActivities: projetoInicial?.descricao || '',
  cnae: ''
}
```

**Depois:**
```typescript
defaultValues: {
  projectTitle: projetoInicial?.titulo_projeto || '',
  projectObjective: projetoInicial?.objetivo_principal || '',
  companyName: projetoInicial?.nome_empresa || '',
  companyActivities: projetoInicial?.resumo_atividades || '',
  cnae: projetoInicial?.cnae || ''
}
```

##### **E. Reset do formulário atualizado (Linhas 52-57):**

**Antes:**
```typescript
reset({
  projectTitle: projetoInicial.nomeProjeto,
  projectObjective: projetoInicial.objetivoPrincipal || '',
  companyName: '',
  companyActivities: projetoInicial.descricao,
  cnae: ''
});
```

**Depois:**
```typescript
reset({
  projectTitle: projetoInicial.titulo_projeto,
  projectObjective: projetoInicial.objetivo_principal,
  companyName: projetoInicial.nome_empresa,
  companyActivities: projetoInicial.resumo_atividades,
  cnae: projetoInicial.cnae
});
```

##### **F. Função de mapeamento criada (Linhas 63-73):**

**Adicionado:**
```typescript
// Função para mapear dados do formulário para o formato do backend
const mapFormToBackend = (formData: ProjectFormData): DadosProjeto => {
  return {
    ...(projetoInicial?.id ? { id: projetoInicial.id } : {}),
    titulo_projeto: formData.projectTitle,
    objetivo_principal: formData.projectObjective,
    nome_empresa: formData.companyName || '',
    resumo_atividades: formData.companyActivities,
    cnae: formData.cnae,
    user_id: usuario?.id || ''
  };
};
```

##### **G. Função handleSaveProjeto simplificada (Linhas 76-82):**

**Antes:**
```typescript
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
  setProjetoSalvo(true);
};
```

**Depois:**
```typescript
const handleSaveProjeto = () => {
  const formData = getValues();
  const projetoData = mapFormToBackend(formData);
  salvarProjeto(projetoData);
  setProjetoSalvo(true);
};
```

##### **H. Componente de upload comentado (Linhas 208-218):**

**Antes:**
```typescript
<div className="mt-[24px] max-md:mt-5">
  <h4 className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-6 max-md:ml-2.5">
    Envio de documentos
  </h4>
  <p className="text-[rgba(67,80,88,1)] font-medium ml-6 mt-3.5 max-md:max-w-full">
    Caso tenha o descritivo do projeto ou o cartão CNPJ da empresa
  </p>
  <FileUpload onFileSelect={setUploadedFile} />
</div>
```

**Depois:**
```typescript
{/* REMOVIDO: Upload de documento não será usado na primeira versão
<div className="mt-[24px] max-md:mt-5">
  <h4 className="text-[rgba(67,80,88,1)] text-2xl font-bold ml-6 max-md:ml-2.5">
    Envio de documentos
  </h4>
  <p className="text-[rgba(67,80,88,1)] font-medium ml-6 mt-3.5 max-md:max-w-full">
    Caso tenha o descritivo do projeto ou o cartão CNPJ da empresa
  </p>
  <FileUpload onFileSelect={setUploadedFile} />
</div>
*/}
```

---

### 8. **CRIAÇÃO DE VARIÁVEIS DE AMBIENTE**

#### **Arquivo CRIADO:** `frontend/.env.example`

**Conteúdo:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

#### **Arquivo CRIADO:** `frontend/.env`

**Conteúdo:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

**Motivo:** Centralizar a URL base da API para facilitar mudanças entre ambientes.

---

## 📊 MAPEAMENTO DE CAMPOS: FORMULÁRIO → BACKEND

### **PROJETO:**

| Campo do Formulário | Variável React Hook Form | Campo Enviado ao Backend | Tipo |
|---------------------|---------------------------|--------------------------|------|
| Título do projeto | `projectTitle` | `titulo_projeto` | string |
| Objetivo Principal | `projectObjective` | `objetivo_principal` | string |
| Nome da Empresa | `companyName` | `nome_empresa` | string |
| Resumo das Atividades | `companyActivities` | `resumo_atividades` | string |
| CNAE | `cnae` | `cnae` | string |
| - | - | `user_id` | string (auto) |
| - | - | `id` | string (auto) |

### **AUTENTICAÇÃO:**

#### **Login:**
| Campo do Formulário | Variável | Campo Enviado | Endpoint |
|---------------------|----------|---------------|----------|
| Email | `email` | `email` | POST /login |
| Senha | `senha` | `password` | POST /login |

#### **Registro:**
| Campo do Formulário | Variável | Campo Enviado | Endpoint |
|---------------------|----------|---------------|----------|
| Nome | `nome` | `name` (parte 1) | POST /api/users |
| Sobrenome | `sobrenome` | `name` (parte 2) | POST /api/users |
| Email | `email` | `email` | POST /api/users |
| Senha | `senha` | `password` | POST /api/users |

---

## 🔄 FLUXO DE AUTENTICAÇÃO

### **Registro:**
1. Usuário preenche formulário de registro
2. Frontend envia `POST /api/users` com `{ email, name, password }`
3. Backend cria usuário no MongoDB
4. Frontend faz login automático com `POST /login`
5. Backend retorna `{ access_token, token_type, user }`
6. Frontend salva token em `localStorage.auth_token`
7. Frontend salva dados do usuário em `localStorage.usuario`
8. Usuário é redirecionado para home

### **Login:**
1. Usuário preenche formulário de login
2. Frontend envia `POST /login` com `{ email, password }`
3. Backend valida credenciais e retorna JWT
4. Frontend salva token em `localStorage.auth_token`
5. Frontend salva dados do usuário em `localStorage.usuario`
6. Usuário é redirecionado para home

### **Requisições Autenticadas:**
1. Frontend pega token de `localStorage.auth_token`
2. Adiciona header: `Authorization: Bearer <token>`
3. Backend valida token JWT
4. Backend retorna dados solicitados

---

## 🔧 ENDPOINTS UTILIZADOS

### **Autenticação:**
- `POST /login` - Login com email e senha
- `POST /api/users` - Registro de novo usuário
- `GET /api/users/me` - Dados do usuário atual (não implementado ainda)

### **Projetos:**
- `GET /api/projects` - Listar todos os projetos do usuário
- `GET /api/projects/{id}` - Buscar projeto específico
- `POST /api/projects` - Criar novo projeto
- `PUT /api/projects/{id}` - Atualizar projeto existente
- `DELETE /api/projects/{id}` - Deletar projeto

### **Editais:**
- `GET /api/editais` - Listar editais (mapeamento pendente)

---

## 🗑️ FUNCIONALIDADES REMOVIDAS

### **1. Upload de Documento PDF:**
- ❌ Componente `<FileUpload />` comentado
- ❌ Estado `uploadedFile` removido
- ❌ Campo `documento_url` não é enviado
- ❌ Seção de upload no formulário comentada

**Motivo:** Funcionalidade adiada para versão futura.

### **2. Campos de Projeto Removidos:**
- ❌ `areaProjeto` - Não faz parte do escopo
- ❌ `orcamento` - Não faz parte do escopo
- ❌ `dataInicio` - Pertence ao edital, não ao projeto
- ❌ `dataFim` - Pertence ao edital, não ao projeto

---

## ⚙️ VARIÁVEIS DE AMBIENTE

### **Arquivo: `frontend/.env`**

```env
VITE_API_BASE_URL=http://localhost:8000
```

**Uso:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

**Importante:** 
- Vite só carrega variáveis que começam com `VITE_`
- Reiniciar o dev server após alterar `.env`

---

## 🚀 COMO TESTAR AS ALTERAÇÕES

### **1. Configurar ambiente:**
```bash
cd frontend

# Criar .env se não existir
cp .env.example .env

# Instalar dependências (se necessário)
npm install

# Iniciar dev server
npm run dev
```

### **2. Testar fluxo completo:**

#### **A. Registro:**
1. Acessar `http://localhost:5173/registro`
2. Preencher formulário
3. Clicar em "Cadastrar"
4. Verificar se foi redirecionado para home
5. Verificar localStorage: `auth_token` e `usuario`

#### **B. Login:**
1. Fazer logout (se estiver logado)
2. Acessar `http://localhost:5173/login`
3. Preencher email e senha
4. Clicar em "Entrar"
5. Verificar redirecionamento

#### **C. Criar Projeto:**
1. Acessar página de match
2. Preencher formulário do projeto
3. Clicar em "Salvar Projeto"
4. Verificar toast de sucesso
5. Verificar no DevTools → Network → Requisição POST

#### **D. Listar Projetos:**
1. Acessar "Meus Projetos"
2. Verificar se lista os projetos salvos
3. Verificar no DevTools → Network → Requisição GET

---

## 🐛 PROBLEMAS CONHECIDOS E SOLUÇÕES

### **1. ERR_EMPTY_RESPONSE:**
**Problema:** Backend não responde ou crasha.
**Solução:** 
- Verificar se containers estão rodando: `docker-compose ps`
- Ver logs: `docker logs -f gofomentos-api-1`
- Reconstruir: `docker-compose up -d --build`

### **2. Variável de ambiente não carrega:**
**Problema:** `import.meta.env.VITE_API_BASE_URL` retorna `undefined`
**Solução:**
- Reiniciar dev server completamente (Ctrl+C e `npm run dev`)
- Verificar se variável começa com `VITE_`
- Limpar cache: `rm -rf node_modules/.vite`

### **3. Token não é enviado:**
**Problema:** Requisições retornam 401 Unauthorized
**Solução:**
- Verificar se token está em `localStorage.auth_token`
- Verificar header: `Authorization: Bearer <token>`
- Fazer login novamente

### **4. CORS Error:**
**Problema:** Erro de CORS no navegador
**Solução:**
- Backend já tem CORS configurado para `allow_origins=["*"]`
- Verificar se backend está rodando
- Limpar cache do navegador

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [x] Serviço de autenticação criado (`apiAuth.ts`)
- [x] Login conectado com API real
- [x] Registro conectado com API real
- [x] Interface `DadosProjeto` atualizada
- [x] Serviço de projetos usando API real
- [x] Formulário de projeto com mapeamento correto
- [x] Upload de documento removido/comentado
- [x] Hook `useProjetoPortugues` corrigido
- [x] Variáveis de ambiente configuradas
- [x] Token JWT salvo corretamente
- [x] Headers de autorização adicionados

---

## 📝 OBSERVAÇÕES IMPORTANTES

1. **Token JWT:** Salvo em `localStorage.auth_token` (não `tokenAutenticacao`)

2. **Campos Obrigatórios:** Todos os campos do formulário de projeto são obrigatórios exceto `companyName`

3. **Upload Removido:** Funcionalidade de upload de documento foi completamente removida da primeira versão

4. **Mapeamento de Nomes:** Frontend usa camelCase, backend usa snake_case. A conversão é feita na função `mapFormToBackend()`

5. **Autenticação Automática:** Após registro, o usuário é automaticamente logado

6. **Timestamps:** `created_at` e `updated_at` são gerados automaticamente pelo backend

---

## 🔗 PRÓXIMOS PASSOS

1. ✅ Implementar mapeamento de editais (backend → frontend)
2. ✅ Criar serviço para buscar editais
3. ✅ Implementar filtros de editais por status
4. ✅ Adicionar paginação na listagem de projetos
5. ✅ Implementar edição de projetos
6. ✅ Adicionar confirmação antes de deletar projeto

---

## 📞 SUPORTE

Em caso de dúvidas sobre as alterações:
1. Verificar este documento
2. Consultar `ALTERACOES_BACKEND.md` para mudanças no backend
3. Ver logs do navegador (F12 → Console)
4. Ver logs do backend: `docker logs -f gofomentos-api-1`

---

**Documento gerado automaticamente em:** 2025-10-02
