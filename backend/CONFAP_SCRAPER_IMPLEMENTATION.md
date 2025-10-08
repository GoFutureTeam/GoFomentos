# 🚀 Implementação do Scraper CONFAP

## ✅ Resumo da Implementação

O scraper CONFAP foi criado seguindo **exatamente os mesmos padrões** dos scrapers existentes (CNPq, FAPESQ, Paraíba Gov), mantendo total consistência com a arquitetura Clean Architecture do projeto.

---

## 📋 Arquivos Criados/Modificados

### ✨ Novos Arquivos

1. **`app/application/services/confap_scraper_service.py`**
   - Scraper principal do CONFAP
   - Implementa raspagem de editais em andamento
   - Extrai links de download de páginas de detalhes
   - Download e extração de PDFs com retry

### 🔧 Arquivos Modificados

2. **`app/core/container.py`**
   - Importado `ConfapScraperService`
   - Adicionado provider Factory para o scraper
   - Injetado no `JobSchedulerService`

3. **`app/application/services/job_scheduler_service.py`**
   - Importado `ConfapScraperService`
   - Adicionado parâmetro `confap_scraper_service` no `__init__`
   - Criado método `execute_confap_job_now()`
   - Criado método privado `_execute_confap_job()`

4. **`app/presentation/api/v1/endpoints/jobs.py`**
   - Adicionado endpoint `POST /jobs/confap/execute`
   - Documentação completa do fluxo do scraper

---

## 🔄 Fluxo de Funcionamento

### **1. Raspagem Inicial**
```
GET https://confap.org.br/pt/editais/status=em-andamento
↓
Extrai todos os links "Ver detalhes"
↓
Filtra por ano (se filter_by_date=True)
```

### **2. Extração de Links de Download**
```
Para cada edital:
  GET {url_detalhes}
  ↓
  Busca links com "download" no href
  ↓
  Fallback: busca links .pdf se não encontrar "download"
```

### **3. Processamento de PDFs**
```
Para cada link de download:
  Download do PDF (com retry)
  ↓
  Extração de texto (ProcessPoolExecutor)
  ↓
  Chunking do texto
  ↓
  Extração de variáveis (OpenAI GPT-4o-mini)
  ↓
  Salvar no MongoDB
  ↓
  Vetorizar no ChromaDB
```

---

## 🎯 Características Implementadas

### **Padrões Seguidos**

✅ **ProcessPoolExecutor** para extração de PDFs (não bloqueia API)  
✅ **Retry com backoff exponencial** (2s, 4s, 6s)  
✅ **Delays configuráveis** entre PDFs (`JOB_PDF_PROCESSING_DELAY_MS`)  
✅ **Logging detalhado** com timestamps e emojis  
✅ **Tratamento de erros** robusto  
✅ **Cancelamento de jobs** em execução  
✅ **Salvamento progressivo** no MongoDB  
✅ **Filtro de data** configurável  

### **Diferencial do CONFAP**

🔹 **Dois níveis de scraping**:
   - Nível 1: Lista de editais
   - Nível 2: Página de detalhes (extrai links de download)

🔹 **Busca inteligente de PDFs**:
   - Prioridade: links com "download" no href
   - Fallback: links que terminam com .pdf

🔹 **Filtro por ano** (não por data limite):
   - Extrai ano do título usando regex
   - Compara com ano atual

---

## 📡 Endpoint da API

### **POST /api/v1/jobs/confap/execute**

**Parâmetros:**
- `filter_by_date` (bool, default=True): Filtra editais por ano

**Resposta:**
```json
{
  "job_id": "uuid-do-job",
  "message": "Job CONFAP iniciado com sucesso (filter_by_date=True)",
  "status_url": "/api/v1/jobs/{job_id}"
}
```

**Exemplo de uso (curl):**
```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}' \
  | jq -r '.access_token')

# Executar job CONFAP
JOB_ID=$(curl -X POST "http://localhost:8000/api/v1/jobs/confap/execute?filter_by_date=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.job_id')

# Monitorar progresso
curl -X GET "http://localhost:8000/api/v1/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧪 Como Testar

### **1. Via Swagger UI**
1. Acesse `http://localhost:8000/docs`
2. Faça login e obtenha o token
3. Execute `POST /api/v1/jobs/confap/execute`
4. Monitore com `GET /api/v1/jobs/{job_id}`

### **2. Verificar Dados Salvos**

**MongoDB:**
```bash
docker-compose exec mongo mongosh -u admin -p password
> use editais_db
> db.editais.find({ origem: "CONFAP" }).pretty()
```

**ChromaDB:**
```bash
# Acessar visualizador
http://localhost:8000/visualizer

# Buscar editais CONFAP
curl "http://localhost:8000/api/chroma/search?query=CONFAP&n_results=10"
```

---

## 📊 Metadata Salvos no MongoDB

Cada edital CONFAP salva os seguintes metadados extras:

```python
{
    'apelido_edital': str,        # Título do edital
    'url_detalhes': str,          # URL da página de detalhes
    'status': str,                # "Em andamento", etc.
    'ano': int,                   # Ano extraído do título
    'financiador_1': 'CONFAP',    # Financiador
    'origem': 'CONFAP',           # Origem do scraper
    # + todas as variáveis extraídas pela OpenAI
}
```

---

## 🔍 Métodos Principais do ConfapScraperService

### **`scrape_confap_editais(filter_by_date: bool = True)`**
- Raspa página de editais em andamento
- Retorna lista de dicionários com metadados básicos
- Filtra por ano se `filter_by_date=True`

### **`extract_download_links(detail_url: str)`**
- Acessa página de detalhes do edital
- Busca links com "download" no href
- Fallback para links .pdf
- Retorna lista de URLs de download

### **`download_and_extract_pdf(url: str, max_retries: int = 3)`**
- Baixa PDF com retry automático
- Extrai texto usando ProcessPoolExecutor
- Retorna texto extraído ou None

---

## ⚙️ Configurações Relevantes (.env)

```env
# Job Processing Performance
JOB_MAX_WORKERS=2                    # Workers para ProcessPoolExecutor
JOB_CHUNK_DELAY_MS=500               # Delay entre chunks OpenAI
JOB_PDF_PROCESSING_DELAY_MS=1000     # Delay entre PDFs

# OpenAI (obrigatório)
OPENAI_API_KEY=sk-proj-...

# PDF Processing
PDF_CHUNK_SIZE=3000                  # Tamanho dos chunks de texto
```

---

## 🎓 Decisões de Design

### **Por que dois níveis de scraping?**
- CONFAP não lista PDFs diretamente na página principal
- Necessário acessar página de detalhes para encontrar downloads
- Padrão similar ao usado em sites de editais governamentais

### **Por que filtrar por ano e não por data limite?**
- CONFAP não exibe data limite na listagem inicial
- Ano é mais fácil de extrair do título
- Mantém consistência com objetivo de pegar editais atuais

### **Por que buscar "download" no href?**
- Padrão comum em sites governamentais
- Links de download geralmente têm essa palavra na URL
- Fallback para .pdf garante cobertura completa

---

## ✅ Checklist de Implementação

- [x] Criar `ConfapScraperService` seguindo padrão existente
- [x] Implementar raspagem de editais em andamento
- [x] Implementar extração de links de download
- [x] Implementar download e extração de PDFs
- [x] Registrar no Container DI
- [x] Adicionar ao `JobSchedulerService`
- [x] Criar endpoint na API
- [x] Documentar fluxo e uso
- [x] Manter consistência com padrões do projeto

---

## 🚀 Próximos Passos (Opcional)

### **Melhorias Futuras**

1. **Extração de data limite da página de detalhes**
   - Parsear HTML da página de detalhes
   - Buscar datas usando regex mais específicos

2. **Cache de páginas de detalhes**
   - Evitar requisições duplicadas
   - Usar Redis ou cache em memória

3. **Paralelização de downloads**
   - Usar `asyncio.gather()` para baixar múltiplos PDFs
   - Respeitar rate limits do servidor

4. **Testes unitários**
   - Mock de requisições HTTP
   - Testes de extração de links
   - Testes de filtros

---

## 📝 Notas Importantes

⚠️ **O scraper CONFAP segue EXATAMENTE o mesmo padrão dos outros scrapers:**
- Mesma estrutura de código
- Mesmas bibliotecas (httpx, BeautifulSoup, pdfplumber)
- Mesmo fluxo de processamento
- Mesma integração com OpenAI e ChromaDB
- Mesma gestão de jobs e progresso

✅ **Código 100% consistente com a arquitetura Clean Architecture do projeto!**

---

**Implementado em: 2025-10-08**  
**Desenvolvedor: Claude (Cascade AI)**
