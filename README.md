# GoFomentos - Sistema de Gerenciamento de Editais

Sistema backend em Python com FastAPI para gerenciamento de editais, utilizando MongoDB para dados estruturados e ChromaDB para armazenamento vetorial.

## Arquitetura

O sistema é composto por:

- **Backend FastAPI**: API RESTful para gerenciamento de usuários, editais e projetos
- **MongoDB**: Armazenamento de dados estruturados (usuários, editais, projetos)
- **ChromaDB**: Armazenamento vetorial para chunks de editais com embeddings

## Funcionalidades

- Download e processamento automático de editais a partir de URLs
- Extração de texto de PDFs usando LangChain e pdfplumber/PyMuPDF
- Extração de dados estruturados usando OpenAI
- Geração de embeddings e armazenamento no ChromaDB
- Busca semântica em editais
- Gerenciamento de usuários e projetos

## Estrutura do Projeto

```
/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   ├── models/
│   │   │   └── services/
│   │   ├── core/
│   │   ├── db/
│   │   ├── processors/
│   │   ├── tests/
│   │   └── main.py
│   ├── docker/
│   │   └── Dockerfile
│   ├── .env.example
│   └── requirements.txt
└── docker-compose.yml
```

## Configuração e Execução

### Pré-requisitos

- Docker e Docker Compose
- Python 3.10+
- PowerShell (para scripts .ps1 no Windows)

### Configuração

1. Clone o repositório:
   ```bash
   git clone <repository-url>
   cd GoFomentos
   ```

2. Configure as variáveis de ambiente:
   ```bash
   cp backend/.env.example backend/.env
   # Edite o arquivo .env com suas configurações
   ```

3. Inicie os serviços com o script de inicialização (Windows):
   ```powershell
   .\start.ps1
   ```
   
   Ou diretamente com Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Inicialize o banco de dados com dados de exemplo:
   ```bash
   docker-compose exec api python init_db.py
   ```

5. Acesse a API em http://localhost:8000

6. Para parar os serviços (Windows):
   ```powershell
   .\stop.ps1
   ```
   
   Ou diretamente com Docker Compose:
   ```bash
   docker-compose down
   ```

### Desenvolvimento Local

Para desenvolvimento local sem Docker:

1. Instale as dependências:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Execute a API:
   ```bash
   cd backend
   python run.py
   ```
   
   Ou diretamente com uvicorn:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. Execute os testes:
   ```bash
   cd backend
   python run_tests.py
   ```

## API Endpoints

### Autenticação
- `POST /token` - Obter token de acesso

### Saúde da API
- `GET /health` - Verificar status da API e conexões com bancos de dados

### Usuários
- `POST /api/users` - Criar usuário
- `GET /api/users/me` - Obter usuário atual
- `GET /api/users/{user_id}` - Obter usuário específico
- `PUT /api/users/{user_id}` - Atualizar usuário
- `DELETE /api/users/{user_id}` - Deletar usuário

### Editais
- `POST /api/editais/fetch` - Buscar e processar editais de uma URL
- `GET /api/editais` - Listar editais
- `GET /api/editais/{edital_uuid}` - Obter edital específico
- `PUT /api/editais/{edital_uuid}` - Atualizar edital
- `DELETE /api/editais/{edital_uuid}` - Deletar edital
- `POST /api/editais/query` - Busca semântica em editais

### Projetos
- `POST /api/projects` - Criar projeto
- `GET /api/projects` - Listar projetos do usuário atual
- `GET /api/projects/{project_id}` - Obter projeto específico
- `PUT /api/projects/{project_id}` - Atualizar projeto
- `DELETE /api/projects/{project_id}` - Deletar projeto

## Documentação da API

A documentação completa da API está disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
