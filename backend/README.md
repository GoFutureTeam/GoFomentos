# GoFomentos - Backend

## Raspador de Chamadas Públicas do CNPq

Este projeto contém scripts para raspagem de chamadas públicas do CNPq, extração de texto de PDFs e análise de variáveis usando OpenAI e ChromaDB.

## Requisitos

- Python 3.9+
- Docker (para ChromaDB)
- Chave de API da OpenAI

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure a variável de ambiente `OPENAI_API_KEY` ou crie um arquivo `.env` na pasta `backend/` com o seguinte conteúdo:
```
OPENAI_API_KEY=sk-sua-chave-aqui
```

3. Inicie o ChromaDB (opcional, apenas se quiser usar a funcionalidade de armazenamento vetorial):
```bash
docker compose up -d
```

## Uso

### Raspagem básica (sem ChromaDB)

```bash
python backend/CNPQ_AI.py
```

### Raspagem com armazenamento no ChromaDB

```bash
python backend/CNPQ_AI.py --chroma
```

### Opções avançadas

```bash
# Especificar host e porta do ChromaDB
python backend/CNPQ_AI.py --chroma --chroma-host localhost --chroma-port 8000

# Limitar o número de chamadas a processar
python backend/CNPQ_AI.py --limite 2
```

### Consultar dados no ChromaDB

```bash
# Listar documentos armazenados
python backend/consulta_chroma.py --listar

# Buscar documentos por consulta semântica
python backend/consulta_chroma.py --buscar "financiamento para pesquisa em saúde"

# Limitar o número de resultados
python backend/consulta_chroma.py --buscar "bolsas de estudo" --limit 3
```

## Arquivos Principais

- `CNPQ_AI.py`: Script principal para raspagem e extração de variáveis
- `consulta_chroma.py`: Utilitário para consultar dados armazenados no ChromaDB
- `requirements.txt`: Dependências do projeto

## Estrutura de Dados

As chamadas públicas são processadas e as seguintes informações são extraídas:

- Apelido do edital
- Financiadores
- Área de foco
- Tipo de proponente
- Valores mínimo e máximo
- Datas de submissão
- E outros campos relevantes

## Integração com ChromaDB

O ChromaDB é usado para armazenar os textos extraídos dos PDFs junto com seus metadados e embeddings, permitindo:

- Busca semântica por conteúdo similar
- Filtragem por metadados (financiador, área, valores, etc.)
- Recuperação rápida de informações específicas

## Problemas Comuns

- **Erro de conexão com ChromaDB**: Verifique se o container Docker está rodando (`docker ps`)
- **Erro de API Key inválida**: Verifique se a chave da OpenAI está correta no arquivo `.env`
- **Timeout nas requisições**: O processamento de PDFs grandes pode demorar, seja paciente
