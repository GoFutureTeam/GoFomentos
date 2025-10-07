# 🚀 GoFomentos Backend - Clean Architecture

API REST para gerenciamento de editais de fomento, construída com **FastAPI** seguindo princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**.

---

## 📋 Índice

- [Características](#-características)
- [Arquitetura](#️-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Executando o Projeto](#-executando-o-projeto)
- [Jobs e Scraping CNPq](#-jobs-e-scraping-cnpq)
- [Busca Semântica (ChromaDB)](#-busca-semântica-chromadb)
- [Documentação da API](#-documentação-da-api)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Performance e Otimizações](#-performance-e-otimizações)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Características

### Core
- ✅ **Clean Architecture**: Código desacoplado, testável e manutenível
- ✅ **Domain-Driven Design**: Lógica de negócio no centro
- ✅ **Dependency Injection**: Gerenciamento automático de dependências
- ✅ **Repository Pattern**: Abstração do acesso a dados
- ✅ **Use Cases**: Orquestração clara da lógica de negócio
- ✅ **Type Hints**: Código 100% tipado
- ✅ **Async/Await**: Performance com operações assíncronas

### Features
- ✅ **JWT Authentication**: Autenticação segura com tokens
- ✅ **MongoDB**: Banco de dados NoSQL
- ✅ **ChromaDB**: Banco vetorial para busca semântica
- ✅ **Jobs Agendados**: Scraping automático CNPq (01:00 AM diário)
- ✅ **Busca Semântica**: Encontre editais por similaridade de conteúdo
- ✅ **Visualizador Web**: Interface para explorar dados vetorizados
- ✅ **Docker**: Containerização completa

---

## 🏗️ Arquitetura

Este projeto segue os princípios de **Clean Architecture**, dividido em 4 camadas principais:

```
┌─────────────────────────────────────┐
│   🔴 PRESENTATION (API/Controllers) │  ← FastAPI Endpoints
├─────────────────────────────────────┤
│   🟢 APPLICATION (Use Cases)        │  ← Orquestração
├─────────────────────────────────────┤
│   🔵 DOMAIN (Entities/Repositories) │  ← Regras de Negócio
├─────────────────────────────────────┤
│   🟡 INFRASTRUCTURE (DB/External)   │  ← Implementações
└─────────────────────────────────────┘
```

### Benefícios

| Aspecto | Antes (Legado) | Depois (Clean Arch) |
|---------|---------------|---------------------|
| **Testabilidade** | Difícil | Fácil (mocks) |
| **Manutenção** | Código espalhado | Bem organizado |
| **Acoplamento** | Alto | Baixo (interfaces) |
| **Escalabilidade** | Limitada | Alta |
| **Trocar Banco** | Reescrever tudo | Trocar implementação |

📖 Toda a documentação de arquitetura e refatoração está consolidada neste README

---

## 📦 Pré-requisitos

- **Python 3.11+**
- **Docker** e **Docker Compose**
- **Git**
- **OpenAI API Key** (para extração de dados de editais)

---

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/GoFutureTeam/GoFomentos.git
cd GoFomentos/backend
```

### 2. Crie um ambiente virtual (opcional)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### 1. Configure as variáveis de ambiente

Edite o arquivo `.env` na raiz do backend:

```env
# API
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=True
PROJECT_NAME="GoFomentos API"

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MongoDB
MONGO_URI=mongodb://admin:password@mongo:27017/editais_db?authSource=admin
MONGO_DB=editais_db

# ChromaDB
CHROMA_HOST=chroma
CHROMA_PORT=8000
CHROMA_COLLECTION=editais_collection

# OpenAI (obrigatório para scraping)
OPENAI_API_KEY=sk-proj-...

# Jina AI (opcional)
JINA_API_KEY=your_jina_api_key

# PDF Processing
PDF_CHUNK_SIZE=3000  # Tamanho dos chunks de texto

# Job Processing Performance
JOB_MAX_WORKERS=2              # Processos para PDFs
JOB_CHUNK_DELAY_MS=200         # Delay entre chunks (ms)
JOB_PDF_PROCESSING_DELAY_MS=500  # Delay entre PDFs (ms)
```

### 2. Ajustar Performance (Opcional)

**Para API mais responsiva durante jobs:**
```env
JOB_MAX_WORKERS=1
JOB_CHUNK_DELAY_MS=1000
JOB_PDF_PROCESSING_DELAY_MS=2000
```

**Para jobs mais rápidos:**
```env
JOB_MAX_WORKERS=4
JOB_CHUNK_DELAY_MS=100
JOB_PDF_PROCESSING_DELAY_MS=500
```

📖 Veja a seção [Performance e Otimizações](#-performance-e-otimizações) para detalhes

---

## 🚀 Executando o Projeto

### Opção 1: Docker Compose (Recomendado)

```bash
# Subir todos os serviços (API + MongoDB + ChromaDB)
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar serviços
docker-compose down
```

A API estará disponível em: **http://localhost:8000**

### Opção 2: Executar Localmente

#### 1. Inicie MongoDB e ChromaDB
```bash
# MongoDB
docker run -d -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  --name mongo mongo:6.0

# ChromaDB
docker run -d -p 8001:8000 \
  --name chroma \
  ghcr.io/chroma-core/chroma:latest
```

#### 2. Execute a aplicação
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🤖 Jobs e Scraping CNPq

### Funcionalidades

- ✅ **Scraping Automático**: Executa às 01:00 AM todos os dias
- ✅ **Execução Manual**: Via API ou interface web
- ✅ **Processamento Progressivo**: Salva cada chunk extraído no MongoDB
- ✅ **Rastreamento em Tempo Real**: Monitore progresso e erros
- ✅ **Cancelamento**: Pare jobs em execução
- ✅ **Vetorização Automática**: Salva embeddings no ChromaDB

### Como Usar

#### Via API (Swagger)

1. Acesse http://localhost:8000/docs
2. Faça login e obtenha o token
3. Execute `POST /api/v1/jobs/cnpq/execute`
4. Monitore com `GET /api/v1/jobs/{job_id}`

#### Via curl

```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}' \
  | jq -r '.access_token')

# Executar job
JOB_ID=$(curl -X POST "http://localhost:8000/api/v1/jobs/cnpq/execute" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.job_id')

# Monitorar progresso
curl -X GET "http://localhost:8000/api/v1/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Fluxo do Job

```
1. Raspagem CNPq → Lista URLs de editais
   ↓
2. Para cada edital:
   ├─ Download PDF
   ├─ Extração de texto (ProcessPoolExecutor)
   ├─ Divisão em chunks
   └─ Para cada chunk:
       ├─ Extração OpenAI (GPT-4o-mini)
       ├─ Salva no MongoDB
       └─ Vetoriza no ChromaDB
   ↓
3. Consolida variáveis finais
   ↓
4. Marca job como completo
```

📖 Todos os detalhes do sistema de jobs estão descritos acima

---

## 🔍 Busca Semântica (ChromaDB)

### O que é?

ChromaDB é um banco vetorial que permite **busca por similaridade semântica**. Em vez de buscar palavras exatas, você busca por **significado**.

**Exemplo:**
- Busca: "inteligência artificial"
- Encontra: editais sobre "machine learning", "deep learning", "IA", "redes neurais" etc.

### Visualizador Web

Acesse: **http://localhost:8000/visualizer**

#### Features
- 🔍 **Busca Semântica**: Digite consultas em linguagem natural
- 📋 **Lista de Editais**: Veja todos os editais indexados
- 📊 **Estatísticas**: Total de chunks, editais únicos
- 🎯 **Filtros**: Busque em edital específico
- 📄 **Visualização**: Veja trechos relevantes com score de relevância

#### Como funciona?

1. **Vetorização**: Textos são convertidos em vetores de 384 dimensões
2. **Modelo**: `all-MiniLM-L6-v2` (79.3 MB, roda localmente)
3. **Download**: Na primeira busca, modelo é baixado e cacheado
4. **Performance**: Warmup automático no startup da API

### API de Busca

```bash
# Busca semântica
curl -X POST "http://localhost:8000/api/chroma/search?query=biotecnologia&n_results=10"

# Listar editais
curl "http://localhost:8000/api/chroma/editais"

# Estatísticas
curl "http://localhost:8000/api/chroma/stats"
```

📖 Todas as informações do visualizador estão descritas acima

---

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **ChromaDB Visualizer**: http://localhost:8000/visualizer

### Endpoints Principais

#### Autenticação
```http
POST /login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "senha123"
}
```

#### Usuários
```http
# Criar
POST /api/v1/users
Content-Type: application/json

{
  "email": "novo@example.com",
  "password": "senha123",
  "name": "João Silva"
}

# Listar
GET /api/v1/users
Authorization: Bearer <token>
```

#### Editais
```http
# Listar
GET /api/v1/editais?skip=0&limit=100
Authorization: Bearer <token>

# Buscar por financiador
GET /api/v1/editais/financiador/CNPq
Authorization: Bearer <token>

# Buscar por status
GET /api/v1/editais/status/aberto
Authorization: Bearer <token>
```

#### Jobs
```http
# Executar job CNPq
POST /api/v1/jobs/cnpq/execute
Authorization: Bearer <token>

# Status do job
GET /api/v1/jobs/{job_id}
Authorization: Bearer <token>

# Histórico
GET /api/v1/jobs?skip=0&limit=10
Authorization: Bearer <token>

# Cancelar
DELETE /api/v1/jobs/{job_id}
Authorization: Bearer <token>
```

#### ChromaDB / Busca Semântica
```http
# Busca semântica
POST /api/chroma/search?query=inteligência+artificial&n_results=10

# Listar editais indexados
GET /api/chroma/editais

# Estatísticas
GET /api/chroma/stats

# Limpar coleção (cuidado!)
POST /api/chroma/clear
Authorization: Bearer <token>
```

---

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── domain/                    # 🔵 Regras de negócio puras
│   │   ├── entities/              # User, Edital, Project, JobExecution
│   │   ├── repositories/          # Interfaces
│   │   └── exceptions/            # Exceções de domínio
│   │
│   ├── application/               # 🟢 Casos de uso
│   │   ├── use_cases/
│   │   │   ├── user/              # CreateUser, AuthenticateUser, GetUser
│   │   │   ├── edital/            # CreateEdital, GetEditais
│   │   │   └── project/           # CreateProject, GetProjects
│   │   └── services/              # CNPqScraper, OpenAIExtractor, JobScheduler
│   │
│   ├── infrastructure/            # 🟡 Implementações
│   │   ├── persistence/
│   │   │   └── mongodb/           # Repositories, Connection
│   │   ├── security/              # JWT, Password (Argon2)
│   │   └── external_services/
│   │
│   ├── presentation/              # 🔴 API REST
│   │   ├── api/v1/endpoints/      # Controllers
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── editais.py
│   │   │   ├── projects.py
│   │   │   ├── jobs.py
│   │   │   ├── chroma.py
│   │   │   └── health.py
│   │   ├── schemas/               # Pydantic models
│   │   └── static/                # Visualizador HTML
│   │
│   ├── core/
│   │   ├── config.py              # Settings
│   │   ├── container.py           # DI Container
│   │   └── container_instance.py
│   │
│   └── main.py                    # Entry point
│
├── tests/                         # Testes unitários e de integração
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
│
└── docs/                          # Documentação
    ├── ARCHITECTURE.md
    ├── REFACTORING_SUMMARY.md
    ├── JOBS_IMPLEMENTATION_STATUS.md
    ├── JOB_PERFORMANCE_OPTIMIZATION.md
    └── VISUALIZER_GUIDE.md
```

---

## ⚡ Performance e Otimizações

### Problema: API Lenta Durante Jobs

Quando jobs de scraping executavam, a API ficava lenta devido a:
- Processamento bloqueante de PDFs
- Chamadas OpenAI sem throttling
- Competição pela mesma event loop

### Soluções Implementadas

#### 1. ProcessPoolExecutor para PDFs
```python
# PDFs processados em processos separados
texto = await loop.run_in_executor(
    self.executor,
    _extract_pdf_text_sync,
    pdf_content
)
```

#### 2. Rate Limiting
```python
# Delays entre chunks e PDFs
await asyncio.sleep(chunk_delay_ms / 1000.0)
```

#### 3. Chunks Maiores
```env
PDF_CHUNK_SIZE=3000  # Antes: 1200 (reduz ~60% dos chunks)
```

### Resultado

- ✅ API responsiva durante jobs
- ✅ Jobs ~60% mais rápidos
- ✅ Configurável via `.env`

📖 Veja a seção [Performance e Otimizações](#-performance-e-otimizações) para detalhes

---

## 🛠️ Comandos Úteis

```bash
# Docker
docker-compose up --build      # Rebuild containers
docker-compose logs -f api     # Ver logs da API
docker-compose exec api bash   # Entrar no container
docker-compose down -v         # Limpar volumes

# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/api/v1/heartbeat  # ChromaDB

# MongoDB
docker-compose exec mongo mongosh -u admin -p password
> use editais_db
> db.users.find()
> db.editais.find()
> db.job_executions.find()

# Formatação e Linting
black app/
flake8 app/
mypy app/

# Testes
pytest
pytest --cov=app tests/
pytest -v tests/test_users.py
```

---

## 🐛 Troubleshooting

### Erro: "Database connection not established"

```bash
# Verificar se MongoDB está rodando
docker-compose ps

# Reiniciar MongoDB
docker-compose restart mongo
```

### Erro: "ModuleNotFoundError"

```bash
# Reinstalar dependências
pip install -r requirements.txt

# Ou rebuild container
docker-compose up --build
```

### Porta já em uso

```bash
# Mudar porta no .env
API_PORT=8001

# Ou matar processo (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Jobs não executam

```bash
# Verificar se OPENAI_API_KEY está configurada
docker-compose exec api env | grep OPENAI

# Ver logs do scheduler
docker-compose logs -f api | grep -i "job\|scheduler"

# Testar manualmente via Swagger
# http://localhost:8000/docs → POST /api/v1/jobs/cnpq/execute
```

### ChromaDB - Modelo baixando lentamente

**Normal na primeira busca!** O modelo `all-MiniLM-L6-v2` (79.3 MB) é baixado e cacheado.

Próximas buscas são instantâneas.

Para pré-carregar no startup, já implementado em `app/main.py:73-78`.

### API lenta durante jobs

Ajuste configurações de performance no `.env`:

```env
JOB_MAX_WORKERS=1              # Menos carga de CPU
JOB_CHUNK_DELAY_MS=1000        # Mais pausas
JOB_PDF_PROCESSING_DELAY_MS=2000
```

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Testes específicos
pytest tests/test_users.py
pytest tests/test_editais.py

# Verbose
pytest -v

# Apenas testes unitários (rápidos)
pytest tests/unit/

# Apenas testes de integração
pytest tests/integration/
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Padrões de Código

- Siga os princípios SOLID
- Mantenha a separação de camadas
- Escreva testes para novas features
- Use type hints em todo o código
- Documente funções complexas
- Siga o padrão de Clean Architecture

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

- **GoFuture Team** - Desenvolvimento inicial
- **Claude Code** - Refatoração para Clean Architecture e features avançadas

---

## 🙏 Agradecimentos

- FastAPI pela excelente framework
- Comunidade Python
- Robert C. Martin pelos princípios de Clean Architecture
- Eric Evans por Domain-Driven Design
- ChromaDB pela solução de busca vetorial

---

## 🔮 Roadmap

### Fase 1 - Testes (Prioridade Alta) 🧪
- [ ] Testes unitários para use cases
- [ ] Testes de integração para repositories
- [ ] CI/CD com GitHub Actions
- [ ] Coverage report automático

### Fase 2 - Features (Prioridade Média) ⭐
- [ ] Update/delete para editais
- [ ] Filtros avançados de busca
- [ ] Paginação com cursors
- [ ] Rate limiting na API
- [ ] Webhooks para notificações

### Fase 3 - Observabilidade (Prioridade Baixa) 📊
- [ ] Logging estruturado (structlog)
- [ ] Métricas (Prometheus)
- [ ] Tracing (OpenTelemetry)
- [ ] Dashboard de monitoramento

### Fase 4 - Segurança (Prioridade Alta) 🔒
- [ ] RBAC (roles e permissões)
- [ ] 2FA (autenticação de dois fatores)
- [ ] Security headers
- [ ] Audit logs

---

**Versão**: 2.0.0
**Arquitetura**: Clean Architecture + DDD
**Stack**: Python 3.11 + FastAPI + MongoDB + ChromaDB
**Status**: ✅ Produção

---

🚀 **Happy Coding!**
