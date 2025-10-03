# Script de Raspagem CNPq

## 📋 Descrição

Script Python para raspagem automática de chamadas públicas abertas do CNPq.

## 🚀 Como Executar

### Manualmente (Desenvolvimento)

```bash
cd backend
python CNPQ.py
```

### Com Docker

```bash
docker build -f Dockerfile.cnpq -t cnpq-scraper .
docker run -v $(pwd)/output:/app/output cnpq-scraper
```

## 📂 Output

Os resultados são salvos em `backend/output/cnpq/`:

- **`cnpq_chamadas_YYYYMMDD_HHMMSS.json`** - Dados estruturados das chamadas
- **`cnpq_html_bruto_YYYYMMDD_HHMMSS.html`** - HTML bruto da página (backup)

## 📊 Estrutura do JSON

```json
{
  "metadata": {
    "fonte": "CNPq - Chamadas Públicas Abertas",
    "url": "...",
    "data_raspagem": "2025-10-02T08:17:00",
    "total_chamadas_encontradas": 10,
    "status": "sucesso"
  },
  "chamadas": [
    {
      "id": 1,
      "titulo": "Chamada CNPq/MIR nº 18/2025",
      "descricao": "...",
      "periodo_inscricao": "12/09/2025 a 29/10/2025",
      "links": [
        {
          "texto": "Chamada",
          "url": "http://..."
        }
      ]
    }
  ]
}
```

## 🔄 Agendamento Futuro (Job Diário)

Para implementar como job diário, você pode usar:

1. **Cron (Linux/Docker)**
2. **Task Scheduler (Windows)**
3. **Celery Beat (Python)**
4. **Kubernetes CronJob**

Exemplo de cron para executar 1x ao dia às 8h:
```cron
0 8 * * * cd /app && python CNPQ.py
```

## 📦 Dependências

- `requests` - Requisições HTTP
- `beautifulsoup4` - Parse de HTML
- `lxml` - Parser XML/HTML (opcional, melhora performance)

Já incluídas no `requirements.txt` do projeto.

## ⚙️ Variável Principal

- **`conteudo_raspado`** - Contém o HTML bruto retornado pelo GET
