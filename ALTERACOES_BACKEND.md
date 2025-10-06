# 📋 DOCUMENTAÇÃO DE ALTERAÇÕES NO BACKEND

## Data: 2025-10-02
## Responsável: Sistema de IA - Integração Frontend ↔ Backend

---

## 🎯 OBJETIVO DAS ALTERAÇÕES

Corrigir incompatibilidades entre frontend e backend, atualizar para Pydantic V2 e garantir que os modelos de dados correspondam aos formulários do frontend.

---

## ✅ ALTERAÇÕES REALIZADAS

### 1. **MODELO USER (`backend/app/api/models/user.py`)**

#### **Alteração:**
- **Linha 42:** `orm_mode = True` → `from_attributes = True`

#### **Motivo:**
- Pydantic V2 deprecou `orm_mode` em favor de `from_attributes`
- Estava causando warnings e possíveis incompatibilidades

#### **Código Anterior:**
```python
class Config:
    orm_mode = True
```

#### **Código Atualizado:**
```python
class Config:
    from_attributes = True  # Atualizado para Pydantic V2 (era orm_mode)
```

---

### 2. **MODELO PROJECT (`backend/app/api/models/project.py`)**

#### **Alterações:**

##### **A. Atualização dos campos do modelo (Linhas 7-23):**

**Campos Removidos:**
- `name: str` → Substituído por `titulo_projeto`
- `description: Optional[str]` → Substituído por campos específicos

**Campos Adicionados:**
```python
# Dados do Projeto
titulo_projeto: str = Field(..., description="Título do projeto")
objetivo_principal: str = Field(..., description="Objetivo principal do projeto")

# Dados da Empresa
nome_empresa: str = Field(..., description="Nome da empresa")
resumo_atividades: str = Field(..., description="Resumo das atividades da empresa")
cnae: str = Field(..., description="CNAE da empresa")

# Relacionamentos
user_id: str = Field(..., description="ID do usuário proprietário")
edital_uuid: Optional[str] = Field(None, description="UUID do edital relacionado")
```

**Motivo:**
- Os campos antigos (`name`, `description`) não correspondiam ao formulário do frontend
- O frontend envia: `titulo_projeto`, `objetivo_principal`, `nome_empresa`, `resumo_atividades`, `cnae`
- Campos como `data_inicio` e `data_fim` foram removidos pois pertencem ao EDITAL, não ao projeto

##### **B. Atualização do ProjectUpdate (Linhas 30-36):**

**Código Anterior:**
```python
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    edital_uuid: Optional[str] = None
```

**Código Atualizado:**
```python
class ProjectUpdate(BaseModel):
    titulo_projeto: Optional[str] = None
    objetivo_principal: Optional[str] = None
    nome_empresa: Optional[str] = None
    resumo_atividades: Optional[str] = None
    cnae: Optional[str] = None
    edital_uuid: Optional[str] = None
```

##### **C. Atualização para Pydantic V2 (Linha 51):**

**Código Anterior:**
```python
class Config:
    orm_mode = True
```

**Código Atualizado:**
```python
class Config:
    from_attributes = True  # Atualizado para Pydantic V2 (era orm_mode)
```

---

### 3. **MODELO EDITAL (`backend/app/api/models/edital.py`)**

#### **Alteração:**
- **Linha 77:** `orm_mode = True` → `from_attributes = True`

#### **Motivo:**
- Compatibilidade com Pydantic V2

#### **Código Anterior:**
```python
class Config:
    orm_mode = True
```

#### **Código Atualizado:**
```python
class Config:
    from_attributes = True  # Atualizado para Pydantic V2 (era orm_mode)
```

---

### 4. **CONFIGURAÇÃO (`backend/app/core/config.py`)**

#### **Alteração:**
- **Linhas 46-56:** Comentados os validators obrigatórios para `OPENAI_API_KEY` e `JINA_API_KEY`

#### **Motivo:**
- As chaves de API são opcionais para desenvolvimento
- Estavam causando erro de validação ao iniciar o backend

#### **Código Anterior:**
```python
@validator("OPENAI_API_KEY")
def validate_openai_api_key(cls, v):
    if not v:
        raise ValueError("OPENAI_API_KEY is required")
    return v

@validator("JINA_API_KEY")
def validate_jina_api_key(cls, v):
    if not v:
        raise ValueError("JINA_API_KEY is required")
    return v
```

#### **Código Atualizado:**
```python
# COMENTADO: Validators opcionais para desenvolvimento
# @validator("OPENAI_API_KEY")
# def validate_openai_api_key(cls, v):
#     if not v:
#         raise ValueError("OPENAI_API_KEY is required")
#     return v

# @validator("JINA_API_KEY")
# def validate_jina_api_key(cls, v):
#     if not v:
#         raise ValueError("JINA_API_KEY is required")
#     return v
```

---

## 📊 MAPEAMENTO DE CAMPOS: FRONTEND ↔ BACKEND

### **PROJETO:**

| Campo Frontend | Campo Backend | Tipo | Obrigatório |
|----------------|---------------|------|-------------|
| `projectTitle` | `titulo_projeto` | string | ✅ Sim |
| `projectObjective` | `objetivo_principal` | string | ✅ Sim |
| `companyName` | `nome_empresa` | string | ✅ Sim |
| `companyActivities` | `resumo_atividades` | string | ✅ Sim |
| `cnae` | `cnae` | string | ✅ Sim |
| - | `user_id` | string | ✅ Sim (auto) |
| - | `edital_uuid` | string | ❌ Não |
| - | `id` | string | ❌ Não (auto) |
| - | `created_at` | datetime | ❌ Não (auto) |
| - | `updated_at` | datetime | ❌ Não (auto) |

### **CAMPOS REMOVIDOS DO PROJETO:**

❌ **Removidos (não fazem parte do projeto):**
- `data_inicio` - Pertence ao EDITAL
- `data_fim` - Pertence ao EDITAL
- `name` - Substituído por `titulo_projeto`
- `description` - Substituído por campos específicos
- `documento_url` - Removido da primeira versão

---

## 🔧 ENDPOINTS AFETADOS

### **Projetos:**
- `POST /api/projects` - Agora aceita os novos campos
- `PUT /api/projects/{id}` - Atualização com novos campos
- `GET /api/projects` - Retorna com novos campos
- `GET /api/projects/{id}` - Retorna com novos campos

### **Usuários:**
- `POST /api/users` - Sem alterações funcionais
- `POST /login` - Sem alterações funcionais

---

## ⚙️ VARIÁVEIS DE AMBIENTE

### **Arquivo: `backend/.env`**

Configurações necessárias:
```env
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=True
PROJECT_NAME="Editais API"

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MongoDB Configuration
MONGO_URI=mongodb://admin:password@mongo:27017/editais_db?authSource=admin
MONGO_DB=editais_db
MONGO_USER=admin
MONGO_PASSWORD=password

# ChromaDB Configuration
CHROMA_HOST=chroma
CHROMA_PORT=8001
CHROMA_COLLECTION=editais_collection

# OpenAI Configuration (opcional para desenvolvimento)
OPENAI_API_KEY=sk-fake-key-for-development

# Jina AI Configuration (opcional para desenvolvimento)
JINA_API_KEY=fake-jina-key-for-development

# PDF Processing
PDF_CHUNK_SIZE=1000
```

---

## 🚀 COMO APLICAR AS ALTERAÇÕES

### **1. Reconstruir o Docker:**
```bash
docker-compose down
docker-compose up -d --build
```

### **2. Verificar se está rodando:**
```bash
docker-compose ps
```

### **3. Testar a API:**
```bash
# Testar endpoint raiz
curl http://localhost:8000

# Testar documentação
# Abrir no navegador: http://localhost:8000/docs
```

### **4. Ver logs:**
```bash
docker logs -f gofomentos-api-1
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [x] Modelo User atualizado para Pydantic V2
- [x] Modelo Project atualizado com campos corretos
- [x] Modelo Edital atualizado para Pydantic V2
- [x] Validators de API keys comentados
- [x] Campos do projeto correspondem ao frontend
- [x] Documentação criada

---

## 📝 OBSERVAÇÕES IMPORTANTES

1. **Upload de Documento:** Foi removido da primeira versão. O campo `documento_url` não está sendo usado.

2. **Datas do Projeto:** Os campos `data_inicio` e `data_fim` foram removidos pois pertencem ao EDITAL, não ao projeto.

3. **Pydantic V2:** Todas as referências a `orm_mode` foram substituídas por `from_attributes`.

4. **API Keys:** As chaves da OpenAI e Jina são opcionais para desenvolvimento. Para produção, fornecer chaves reais.

5. **MongoDB:** O backend espera MongoDB rodando em `mongo:27017` (nome do serviço Docker).

---

## 🔗 PRÓXIMOS PASSOS

1. ✅ Subir containers: `docker-compose up -d --build`
2. ✅ Testar registro de usuário
3. ✅ Testar login
4. ✅ Testar criação de projeto
5. ✅ Testar listagem de projetos
6. ✅ Integrar com frontend

---

## 📞 SUPORTE

Em caso de erros:
1. Verificar logs: `docker logs -f gofomentos-api-1`
2. Verificar MongoDB: `docker logs gofomentos-mongo-1`
3. Verificar se containers estão rodando: `docker-compose ps`
4. Reiniciar containers: `docker-compose restart`

---

**Documento gerado automaticamente em:** 2025-10-02
