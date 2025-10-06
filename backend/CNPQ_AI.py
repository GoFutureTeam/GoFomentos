"""
Script para raspagem de chamadas públicas do CNPq
Executa manualmente e salva resultado em JSON
Foco: Extrair links dos botões 'Chamada' dentro de divs com classe 'links-normas'
Integração com OpenAI e ChromaDB para extração de variáveis
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
import pdfplumber
from io import BytesIO
import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


# =====================================================================
# CONFIG
# =====================================================================
# Obtém a chave da API do OpenAI das variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"[DEBUG] OPENAI_API_KEY encontrada: {'Sim' if OPENAI_API_KEY else 'Não'}")

# Se a chave não estiver definida, tente usar a chave diretamente do arquivo .env
if not OPENAI_API_KEY:
    try:
        with open(os.path.join(os.path.dirname(__file__), '.env'), 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    OPENAI_API_KEY = line.strip().split('=', 1)[1].strip('"\'')
                    print(f"[DEBUG] OPENAI_API_KEY carregada diretamente do arquivo .env")
                    break
    except Exception as e:
        print(f"[DEBUG] Erro ao ler arquivo .env: {e}")

# Inicializar cliente OpenAI
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("[OK] Cliente OpenAI inicializado com sucesso")
else:
    print("[ERRO] OPENAI_API_KEY não encontrada. Configure a variável de ambiente ou o arquivo .env")
    exit(1)

# Configuração do ChromaDB (opcional)
USE_CHROMA = True  # Padrão: ativado
chroma_client = None
collection = None

# Configuração para o ChromaDB dockerizado
CHROMA_HOST = "localhost"  # Use "chroma" se estiver rodando dentro do mesmo docker-compose
CHROMA_PORT = 8001  # Porta mapeada no container Docker

# Processar argumentos de linha de comando
def parse_args():
    parser = argparse.ArgumentParser(description="Raspador de chamadas públicas do CNPq com extração de variáveis")
    parser.add_argument("--chroma", action="store_true", help="Ativar integração com ChromaDB")
    parser.add_argument("--chroma-host", type=str, default="localhost", help="Host do ChromaDB (padrão: localhost)")
    parser.add_argument("--chroma-port", type=int, default=8001, help="Porta do ChromaDB (padrão: 8001)")
    parser.add_argument("--limite", type=int, default=None, help="Limite de chamadas para processar")
    return parser.parse_args()

if USE_CHROMA:
    try:
        # Tentar conexão com retry para garantir que o serviço está disponível
        max_retries = 3
        retry_delay = 2  # segundos
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Tentativa {attempt}/{max_retries} de conexão ao ChromaDB...")
                chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
                
                # Testar conexão
                collections = chroma_client.list_collections()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [OK] Conexão com ChromaDB estabelecida. Collections disponíveis: {len(collections)}")

                # Criar ou obter coleção (versão simplificada)
                try:
                    collection = chroma_client.get_or_create_collection(name="editais_cnpq")
                except Exception as col_err:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro ao criar coleção: {col_err}")
                    # Tentar sem parâmetros extras
                    collection = chroma_client.create_collection(name="editais_cnpq")

                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [OK] Coleção 'editais_cnpq' pronta para uso.")
                break
            except Exception as retry_e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Tentativa {attempt} falhou: {retry_e}")
                if attempt < max_retries:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Aguardando {retry_delay}s antes da próxima tentativa...")
                    import time
                    time.sleep(retry_delay)
                else:
                    raise
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERRO] ERRO ao conectar com ChromaDB após {max_retries} tentativas: {e}")
        print("Continuando sem ChromaDB...")
        USE_CHROMA = False


# =====================================================================
# FUNÇÕES DE SUPORTE
# =====================================================================
def chunk_texto(texto, tamanho_chunk=1200, sobreposicao=200):
    """
    Divide o texto em pedaços (chunks) para enviar à LLM e indexar no ChromaDB.
    """
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho_chunk
        chunk = texto[inicio:fim]
        chunks.append(chunk.strip())
        inicio += tamanho_chunk - sobreposicao
    return chunks


def extrair_variaveis_llm(texto, link):
    """
    Envia os chunks do texto para a LLM e consolida as variáveis em JSON.
    """
    chunks = chunk_texto(texto)
    resultados = []

    for i, chunk in enumerate(chunks, 1):
        prompt = f"""
        Você é um extrator de informações de editais.
        Extraia os seguintes campos em formato JSON válido:

        {{
          "apelido_edital": "STRING",
          "financiador_1": "STRING",
          "financiador_2": "STRING",
          "area_foco": "STRING",
          "tipo_proponente": "STRING",
          "empresas_que_podem_submeter": "STRING",
          "duracao_min_meses": "NUMBER",
          "duracao_max_meses": "NUMBER",
          "valor_min_R$": "NUMBER",
          "valor_max_R$": "NUMBER",
          "tipo_recurso": "STRING",
          "recepcao_recursos": "STRING",
          "custeio": "BOOLEAN",
          "capital": "BOOLEAN",
          "contrapartida_min_%": "NUMBER",
          "contrapartida_max_%": "NUMBER",
          "tipo_contrapartida": "STRING",
          "data_inicial_submissao": "YYYY-MM-DD",
          "data_final_submissao": "YYYY-MM-DD",
          "data_resultado": "YYYY-MM-DD",
          "descricao_completa": "STRING",
          "origem": "STRING",
          "link": "STRING",
          "observacoes": "STRING"
        }}

        Se algum campo não estiver presente neste trecho, preencha com null.

        Texto do edital (chunk {i}/{len(chunks)}):
        {chunk}
        """

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processando chunk {i}/{len(chunks)} do edital {link}")
        
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            resposta_llm = resp.choices[0].message.content

            # Limpar markdown code blocks se existirem (fazer múltiplas vezes para garantir)
            resposta_limpa = resposta_llm.strip()

            # Remover blocos de código markdown
            if "```json" in resposta_limpa:
                # Extrair apenas o conteúdo entre ```json e ```
                import re
                match = re.search(r'```json\s*(.*?)\s*```', resposta_limpa, re.DOTALL)
                if match:
                    resposta_limpa = match.group(1).strip()
            elif "```" in resposta_limpa:
                resposta_limpa = resposta_limpa.replace("```", "").strip()

            print(f"[LLM] Resposta do chunk {i} (primeiros 200 chars):")
            print(f"{resposta_limpa[:200]}...")

            try:
                dados = json.loads(resposta_limpa)
                print(f"[OK] JSON válido extraído do chunk {i}")
            except Exception as e:
                print(f"[ERRO] Resposta não é JSON válido: {e}")
                print(f"[DEBUG] Conteúdo recebido: {resposta_limpa[:300]}")
                dados = {"erro": "resposta inválida", "raw": resposta_limpa[:1000]}

            dados["link"] = link
            dados["chunk_index"] = i
            resultados.append(dados)

            # Inserir no ChromaDB (se estiver ativado)
            if USE_CHROMA and collection:
                try:
                    # Gerar ID único para o documento
                    timestamp = datetime.now().timestamp()
                    doc_id = f"{link.replace('http://', '').replace('https://', '').replace('/', '_')}_chunk_{i}_{timestamp}".replace(".", "_")
                    
                    # Preparar metadados estruturados
                    metadata = {
                        "link": link,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "timestamp": timestamp,
                        "caracteres": len(chunk),
                        "processado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Adicionar variáveis extraídas (se não for erro)
                    if not dados.get("erro"):
                        # Converter variáveis para string JSON para armazenamento
                        metadata["variaveis_extraidas"] = json.dumps(dados)
                        
                        # Adicionar campos específicos para facilitar buscas
                        for campo in ["apelido_edital", "financiador_1", "area_foco", "tipo_proponente", 
                                      "valor_min_R$", "valor_max_R$", "data_final_submissao"]:
                            if dados.get(campo):
                                metadata[f"var_{campo}"] = str(dados.get(campo))
                    else:
                        metadata["erro_extracao"] = dados.get("erro")
                    
                    # Adicionar ao ChromaDB
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SAVE] Salvando chunk {i} no ChromaDB...")
                    collection.add(
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [OK] Chunk {i} processado e adicionado ao ChromaDB com sucesso")
                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERRO] ERRO ao adicionar ao ChromaDB: {e}")
                    print("Continuando sem salvar no ChromaDB...")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [OK] Chunk {i} processado (ChromaDB desativado)")

        except Exception as e:
            print(f"[ERRO] Erro ao processar chunk {i}: {str(e)}")
            resultados.append({"erro": str(e), "link": link, "chunk_index": i})

    return resultados


# =====================================================================
# ETAPA 1: RASPAGEM DO CNPQ
# =====================================================================
def raspar_cnpq():
    """
    Faz scraping das chamadas públicas abertas do CNPq
    Foco em extrair os botões 'Chamada' dentro de divs com classe 'links-normas'
    Retorna os dados estruturados
    """
    url = "http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/"
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando raspagem do CNPq...")
    print(f"URL: {url}")
    
    try:
        # Fazer requisição GET
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Requisição bem-sucedida! Status: {response.status_code}")
        
        # Parse do HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrair chamadas públicas
        chamadas = []
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processando conteúdo...")
        
        # ESTRATÉGIA PRINCIPAL: Buscar botões 'Chamada' dentro de divs com classe 'links-normas'
        botoes_chamada = soup.find_all('div', class_='links-normas')
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Encontrados {len(botoes_chamada)} divs 'links-normas'")
        
        for idx, div_links in enumerate(botoes_chamada, 1):
            # Buscar o link do botão 'Chamada' com classe 'btn'
            link_chamada = div_links.find('a', class_='btn', href=True)
            
            if link_chamada:
                href = link_chamada.get('href', '')
                
                chamada_info = {
                    'id': idx,
                    'link_chamada': href
                }
                
                chamadas.append(chamada_info)
                print(f"  [+] Chamada {idx}: {href}")
        
        # ESTRATÉGIA FALLBACK: Se não encontrou nada, buscar links que apontam para resultado.cnpq.br
        if len(chamadas) == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Usando estratégia alternativa (fallback)...")
            links_resultado = soup.find_all('a', href=lambda x: x and 'resultado.cnpq.br' in x)
            
            for idx, link in enumerate(links_resultado, 1):
                href = link.get('href', '')
                
                chamada_info = {
                    'id': idx,
                    'link_chamada': href
                }
                chamadas.append(chamada_info)
                print(f"  [+] Chamada {idx} (fallback): {href}")
        
        # Estrutura final dos dados
        dados_estruturados = {
            'metadata': {
                'fonte': 'CNPq - Chamadas Públicas Abertas',
                'url': url,
                'data_raspagem': datetime.now().isoformat(),
                'total_chamadas_encontradas': len(chamadas),
                'estrategia_usada': 'links-normas' if len(botoes_chamada) > 0 else 'fallback',
                'status': 'sucesso'
            },
            'chamadas': chamadas
        }
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Raspagem concluída!")
        print(f"Total de chamadas encontradas: {len(chamadas)}")
        
        return dados_estruturados
        
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO na requisição: {e}")
        return {
            'metadata': {
                'fonte': 'CNPq - Chamadas Públicas Abertas',
                'url': url,
                'data_raspagem': datetime.now().isoformat(),
                'status': 'erro',
                'erro': str(e)
            },
            'chamadas': []
        }
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO no processamento: {e}")
        return {
            'metadata': {
                'fonte': 'CNPq - Chamadas Públicas Abertas',
                'url': url,
                'data_raspagem': datetime.now().isoformat(),
                'status': 'erro',
                'erro': str(e)
            },
            'chamadas': []
        }


def buscar_conteudo_chamada(link_chamada):
    """
    Faz GET em um link específico de chamada e retorna o conteúdo
    Detecta se é PDF e extrai o texto
    Retorna a variável conteudo_chamada
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Buscando conteúdo da chamada...")
    print(f"Link: {link_chamada}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(link_chamada, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Requisição bem-sucedida! Status: {response.status_code}")
        
        # Verificar se é PDF pelo Content-Type
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/pdf' in content_type or link_chamada.lower().endswith('.pdf'):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detectado arquivo PDF. Extraindo texto...")
            
            # Extrair texto do PDF usando pdfplumber
            pdf_bytes = BytesIO(response.content)
            texto_completo = ''
            total_paginas = 0
            
            with pdfplumber.open(pdf_bytes) as pdf:
                total_paginas = len(pdf.pages)
                print(f"   Total de páginas: {total_paginas}")
                
                for pagina_num, pagina in enumerate(pdf.pages, 1):
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += f"\n--- Página {pagina_num} ---\n{texto_pagina}\n"
            
            # Estrutura do resultado para PDF
            resultado = {
                'link': link_chamada,
                'tipo': 'PDF',
                'status_code': response.status_code,
                'tamanho_bytes': len(response.content),
                'total_paginas': total_paginas,
                'texto_extraido': texto_completo,
                'preview_texto': texto_completo[:500] + '...' if len(texto_completo) > 500 else texto_completo
            }
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Texto extraído com sucesso!")
            print(f"   Tamanho do PDF: {len(response.content) / 1024:.2f} KB")
            print(f"   Total de páginas: {total_paginas}")
            print(f"   Caracteres extraídos: {len(texto_completo)}")
            
            return resultado
        
        else:
            # Se não for PDF, processar como HTML
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detectado conteúdo HTML.")
            
            conteudo_html = response.text
            soup = BeautifulSoup(conteudo_html, 'html.parser')
            
            resultado = {
                'link': link_chamada,
                'tipo': 'HTML',
                'status_code': response.status_code,
                'tamanho_bytes': len(conteudo_html),
                'titulo_pagina': soup.title.string if soup.title else 'N/A',
                'html_completo': conteudo_html
            }
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Conteúdo HTML capturado!")
            print(f"   Tamanho: {len(conteudo_html) / 1024:.2f} KB")
            print(f"   Título: {resultado['titulo_pagina']}")
            
            return resultado
        
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO na requisição: {e}")
        return {
            'link': link_chamada,
            'tipo': 'ERRO',
            'status_code': 0,
            'erro': str(e)
        }
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO ao processar conteúdo: {e}")
        return {
            'link': link_chamada,
            'tipo': 'ERRO',
            'status_code': response.status_code if 'response' in locals() else 0,
            'erro': str(e)
        }


def main():
    """
    Função principal
    """
    # Processar argumentos de linha de comando
    args = parse_args()
    
    # Configurar ChromaDB com base nos argumentos
    global USE_CHROMA, CHROMA_HOST, CHROMA_PORT
    use_chroma = args.chroma  # Usar variável local
    if args.chroma:
        USE_CHROMA = True
        CHROMA_HOST = args.chroma_host
        CHROMA_PORT = args.chroma_port
    
    print("=" * 80)
    print("RASPADOR DE CHAMADAS PÚBLICAS DO CNPq COM EXTRAÇÃO DE VARIÁVEIS")
    if use_chroma:
        print(f"Integração com OpenAI e ChromaDB ({CHROMA_HOST}:{CHROMA_PORT})")
    else:
        print("Integração com OpenAI (ChromaDB desativado)")
    print("=" * 80)
    print()
    
    # Verificar se a chave da API OpenAI está configurada
    if not OPENAI_API_KEY:
        print("[ERRO] ERRO: OPENAI_API_KEY não está configurada nas variáveis de ambiente.")
        print("   Por favor, configure a variável de ambiente OPENAI_API_KEY.")
        return None, None, None, None

    # Verificar conexão com ChromaDB apenas se estiver ativado
    if use_chroma:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Verificando conexão com ChromaDB...")
            if chroma_client and collection:
                print(f"[OK] Conexão com ChromaDB já estabelecida anteriormente.")
            else:
                print(f"[ERRO] ChromaDB não inicializado corretamente.")
                print("   Continuando sem ChromaDB...")
                use_chroma = False
        except Exception as e:
            print(f"[ERRO] ERRO ao verificar ChromaDB: {e}")
            print("   Continuando sem ChromaDB...")
            use_chroma = False

    # Executar raspagem
    dados_cnpq = raspar_cnpq()

    # Verificar se a raspagem foi bem-sucedida
    if dados_cnpq['metadata']['status'] != 'sucesso':
        print("[ERRO] Erro durante a raspagem. Verifique os logs acima.")
        return dados_cnpq, [], [], []
    
    # Extrair links das chamadas
    links_chamadas = [chamada.get('link_chamada', '') for chamada in dados_cnpq.get('chamadas', [])]
    links_chamadas = [link for link in links_chamadas if link]  # Remover links vazios
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de links extraídos: {len(links_chamadas)}")
    
    # Processar cada chamada
    resultados_chamadas = []
    variaveis_extraidas = []
    
    for idx, link in enumerate(links_chamadas, 1):
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processando chamada {idx}/{len(links_chamadas)}")
        print(f"Link: {link}")
        
        # Buscar conteúdo da chamada
        conteudo = buscar_conteudo_chamada(link)
        resultados_chamadas.append(conteudo)
        
        # Se for PDF, extrair variáveis usando LLM
        if conteudo and conteudo.get('tipo') == 'PDF':
            texto = conteudo.get('texto_extraido', '')
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo variáveis do PDF usando LLM...")
            
            try:
                vars_extraidas = extrair_variaveis_llm(texto, link)
                variaveis_extraidas.append({
                    'link': link,
                    'variaveis': vars_extraidas
                })
                print(f"[OK] Variáveis extraídas com sucesso para {link}")
            except Exception as e:
                print(f"[ERRO] ERRO ao extrair variáveis: {e}")
                variaveis_extraidas.append({
                    'link': link,
                    'erro': str(e)
                })
    
    # Criar diretório para resultados
    Path("resultados").mkdir(exist_ok=True)
    
    # Salvar resultados em JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar dados da raspagem
    with open(f"resultados/cnpq_chamadas_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(dados_cnpq, f, indent=2, ensure_ascii=False)
    
    # Salvar variáveis extraídas
    with open(f"resultados/variaveis_extraidas_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(variaveis_extraidas, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print(f"[OK] PROCESSAMENTO CONCLUÍDO!")
    print(f"Estatísticas:")
    print(f"   - Chamadas encontradas: {len(dados_cnpq.get('chamadas', []))}")
    print(f"   - Chamadas processadas: {len(resultados_chamadas)}")
    print(f"   - PDFs com variáveis extraídas: {len(variaveis_extraidas)}")
    print(f"\nResultados salvos em:")
    print(f"   - resultados/cnpq_chamadas_{timestamp}.json")
    print(f"   - resultados/variaveis_extraidas_{timestamp}.json")
    print("=" * 80)
    
    return dados_cnpq, links_chamadas, resultados_chamadas, variaveis_extraidas


if __name__ == "__main__":
    try:
        # Executar e capturar os retornos
        cnpq_chamadas, cnpq_links_extraidos, conteudos_chamadas, variaveis_extraidas = main()
        print("\n\n" + "=" * 80)
        print("[OK] PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("[CANCELADO] PROCESSAMENTO INTERROMPIDO PELO USUÁRIO")
        print("=" * 80)
    except Exception as e:
        print("\n\n" + "=" * 80)
        print(f"[ERRO] ERRO: {e}")
        print("=" * 80)
