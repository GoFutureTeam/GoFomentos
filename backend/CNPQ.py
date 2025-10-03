"""
Script para raspagem de chamadas públicas do CNPq
Executa manualmente e salva resultado em JSON
Foco: Extrair links dos botões 'Chamada' dentro de divs com classe 'links-normas'
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
import pdfplumber
from io import BytesIO
import os
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions


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
        
        # Armazenar conteúdo HTML bruto
        conteudo_raspado = response.text
        
        # Parse do HTML
        soup = BeautifulSoup(conteudo_raspado, 'html.parser')
        
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
                print(f"  ✓ Chamada {idx}: {href}")
        
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
                print(f"  ✓ Chamada {idx} (fallback): {href}")
        
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
            'chamadas': chamadas,
            'html_bruto': {
                'tamanho_bytes': len(conteudo_raspado),
                'titulo_pagina': soup.title.string if soup.title else 'N/A',
                'conteudo_preview': conteudo_raspado[:1000]
            }
        }
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Raspagem concluída!")
        print(f"Total de chamadas encontradas: {len(chamadas)}")
        
        return dados_estruturados, conteudo_raspado
        
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
            'chamadas': [],
            'html_bruto': {}
        }, ""
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
            'chamadas': [],
            'html_bruto': {}
        }, ""


def processar_resultado(dados):
    """
    Processa os resultados e retorna a variável cnpq_chamadas
    """
    cnpq_chamadas = dados
    
    print(f"\n✅ Dados processados com sucesso!")
    print(f"   Total de chamadas: {len(cnpq_chamadas.get('chamadas', []))}")
    
    return cnpq_chamadas


def extrair_links_chamadas(cnpq_chamadas):
    """
    Extrai apenas os links das chamadas do resultado da raspagem
    Retorna a variável cnpq_links_extraidos
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo links das chamadas...")
    
    cnpq_links_extraidos = []
    
    # Iterar sobre as chamadas e extrair apenas o link_chamada
    for chamada in cnpq_chamadas.get('chamadas', []):
        link = chamada.get('link_chamada', '')
        if link:
            cnpq_links_extraidos.append(link)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de links extraídos: {len(cnpq_links_extraidos)}")
    
    return cnpq_links_extraidos


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




# =====================================================================
# CONFIG
# =====================================================================
# Obtém a chave da API do OpenAI das variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Configuração do ChromaDB
chroma_client = chromadb.HttpClient(host="localhost", port=8001)
embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

# Criar ou obter a coleção para os editais
try:
    collection = chroma_client.get_or_create_collection(
        name="editais_cnpq",
        embedding_function=embedding_fn
    )
    print(f"\n✅ Conexão com ChromaDB estabelecida. Coleção 'editais_cnpq' pronta.")
except Exception as e:
    print(f"\n❌ ERRO ao conectar com ChromaDB: {e}")
    print("   Verifique se o serviço ChromaDB está em execução na porta 8001.")


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
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Texto dividido em {len(chunks)} chunks")
    
    resultados = []

    for i, chunk in enumerate(chunks, 1):
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processando chunk {i}/{len(chunks)} do edital {link}")
        
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
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💬 Enviando chunk para OpenAI (modelo: gpt-4o-mini)...")
        
        try:
            # Enviar para OpenAI
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Resposta recebida da OpenAI")

            # Processar resposta
            try:
                dados = json.loads(resp.choices[0].message.content)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ JSON válido extraído")
            except json.JSONDecodeError as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao decodificar JSON: {e}")
                print(f"Resposta bruta: {resp.choices[0].message.content[:200]}...")
                dados = {"erro": "resposta inválida", "raw": resp.choices[0].message.content}

            # Adicionar metadados
            dados["link"] = link
            dados["chunk_index"] = i
            resultados.append(dados)

            # Gerar ID único para o ChromaDB
            doc_id = f"{link.replace('http://', '').replace('https://', '').replace('/', '_').replace('.', '_')}_chunk_{i}_{datetime.now().timestamp()}"
            
            # Inserir no ChromaDB
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💾 Salvando no ChromaDB (ID: {doc_id})...")
            collection.add(
                documents=[chunk],
                metadatas=[{
                    "link": link,
                    "chunk_index": i,
                    "variaveis_extraidas": json.dumps(dados)
                }],
                ids=[doc_id]
            )
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Chunk {i} processado e adicionado ao ChromaDB")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar chunk {i}: {str(e)}")
            resultados.append({"erro": str(e), "link": link, "chunk_index": i})

    return resultados


def buscar_conteudo_todas_chamadas(links_chamadas):
    """
    Processa todos os links de chamadas, fazendo GET em cada um
    Detecta se são PDFs e extrai o texto
    Retorna uma lista com o conteúdo de todas as chamadas
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processando {len(links_chamadas)} links de chamadas...")
    
    resultados = []
    textos_extraidos = []
    variaveis_extraidas = []
    
    for idx, link in enumerate(links_chamadas, 1):
        print(f"\n{'-' * 80}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📂 PROCESSANDO CHAMADA {idx}/{len(links_chamadas)}")
        print(f"Link: {link}")
        print(f"{'-' * 80}")
        
        # ETAPA 1: Buscar conteúdo da chamada
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💾 ETAPA 1: Buscando conteúdo da chamada...")
        conteudo = buscar_conteudo_chamada(link)
        
        # Adicionar ao resultado
        resultados.append(conteudo)
        
        # Exibir preview do edital processado
        print(f"\n📄 PREVIEW DO EDITAL #{idx}:")
        print(f"  Status: {conteudo.get('status_code', 'N/A')}")
        print(f"  Tipo: {conteudo.get('tipo', 'N/A')}")
        print(f"  Tamanho: {conteudo.get('tamanho_bytes', 0) / 1024:.2f} KB")
        
        # Se for PDF, processar completamente antes de ir para o próximo link
        if conteudo and conteudo.get('tipo') == 'PDF':
            texto = conteudo.get('texto_extraido', '')
            total_paginas = conteudo.get('total_paginas', 0)
            
            print(f"  Páginas: {total_paginas}")
            print(f"  Caracteres extraídos: {len(texto)}")
            print(f"\n  📖 Preview do texto (primeiros 300 caracteres):")
            preview = conteudo.get('preview_texto', '')[:300]
            print(f"  {preview}...\n")
            
            # Adicionar à lista de textos extraídos
            textos_extraidos.append({
                'link': link,
                'texto': texto,
                'tamanho': len(texto),
                'paginas': total_paginas
            })
            
            # ETAPA 2: Extrair variáveis usando LLM e salvar no ChromaDB
            if len(texto) > 0:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💾 ETAPA 2: Extraindo variáveis e salvando no ChromaDB...")
                try:
                    vars_extraidas = extrair_variaveis_llm(texto, link)
                    variaveis_extraidas.append({
                        'link': link,
                        'variaveis': vars_extraidas
                    })
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Variáveis extraídas e salvas com sucesso para {link}")
                except Exception as e:
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ ERRO ao extrair variáveis: {e}")
                    variaveis_extraidas.append({
                        'link': link,
                        'erro': str(e)
                    })
            else:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Texto vazio, pulando extração de variáveis")
        elif conteudo and conteudo.get('tipo') == 'HTML':
            print(f"  Título: {conteudo.get('titulo_pagina', 'N/A')}")
            print(f"  HTML: {len(conteudo.get('html_completo', ''))} caracteres")
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Conteúdo HTML não processado para extração de variáveis")
        elif conteudo and conteudo.get('tipo') == 'ERRO':
            print(f"  ❌ ERRO: {conteudo.get('erro', 'Erro desconhecido')}")
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Processamento completo da chamada {idx}/{len(links_chamadas)}")
        print(f"{'-' * 80}")
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎉 Processamento de todas as chamadas concluído!")
    print(f"Total de chamadas processadas: {len(resultados)}")
    print(f"Total de PDFs extraídos: {len(textos_extraidos)}")
    print(f"Total de chamadas com variáveis extraídas: {len(variaveis_extraidas)}")
    
    return resultados, textos_extraidos, variaveis_extraidas


def main():
    """
    Função principal
    """
    print("=" * 80)
    print("RASPADOR DE CHAMADAS PÚBLICAS DO CNPq COM EXTRAÇÃO DE VARIÁVEIS")
    print("Integração com OpenAI e ChromaDB")
    print("=" * 80)
    print()
    
    # Verificar se a chave da API OpenAI está configurada
    if not OPENAI_API_KEY:
        print("❌ ERRO: OPENAI_API_KEY não está configurada nas variáveis de ambiente.")
        print("   Por favor, configure a variável de ambiente OPENAI_API_KEY.")
        return None, None, None, None
    
    # Executar raspagem
    dados = raspar_cnpq()
    
    # Verificar se a raspagem foi bem-sucedida
    if dados['metadata']['status'] != 'sucesso':
        print("❌ Erro durante a raspagem. Verifique os logs acima.")
        return dados, [], [], []
    
    # Extrair links das chamadas
    links_chamadas = [chamada.get('link_chamada', '') for chamada in dados.get('chamadas', [])]
    links_chamadas = [link for link in links_chamadas if link]  # Remover links vazios
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total de links extraídos: {len(links_chamadas)}")
    
    # Processar todos os links
    conteudos_chamadas = []
    pdfs_textos_extraidos = []
    variaveis_extraidas = []
    
    if links_chamadas:
        # Processar todos os links sequencialmente
        conteudos_chamadas, pdfs_textos_extraidos, variaveis_extraidas = buscar_conteudo_todas_chamadas(links_chamadas)
        
        print(f"\n✅ Variável conteudos_chamadas criada com {len(conteudos_chamadas)} itens")
        print(f"✅ Variável pdfs_textos_extraidos criada com {len(pdfs_textos_extraidos)} itens")
        print(f"✅ Variável variaveis_extraidas criada com {len(variaveis_extraidas)} itens")
    
    # Mostrar resumo final
    print("\n✅ Raspagem executada com sucesso!")
    
    # Mostrar resumo das chamadas
    if dados.get('chamadas', []):
        print("\n📋 RESUMO DAS CHAMADAS ENCONTRADAS:")
        for chamada in dados.get('chamadas', []):
            print(f"  ID {chamada.get('id', '')}: {chamada.get('link_chamada', 'N/A')}")
    
    # Mostrar resumo dos PDFs processados
    if pdfs_textos_extraidos:
        print("\n📖 RESUMO DOS PDFs PROCESSADOS:")
        for idx, pdf in enumerate(pdfs_textos_extraidos, 1):
            print(f"  PDF #{idx}: {pdf.get('link', '')}")
            print(f"    Páginas: {pdf.get('paginas', 0)}")
            print(f"    Tamanho do texto: {pdf.get('tamanho', 0)} caracteres")
    
    # Criar diretório para resultados
    Path("resultados").mkdir(exist_ok=True)
    
    # Salvar resultados em JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar dados da raspagem
    with open(f"resultados/cnpq_chamadas_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    # Salvar variáveis extraídas
    with open(f"resultados/variaveis_extraidas_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(variaveis_extraidas, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print(f"✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"📊 Estatísticas:")
    print(f"   - Chamadas encontradas: {len(dados.get('chamadas', []))}")
    print(f"   - Chamadas processadas: {len(conteudos_chamadas)}")
    print(f"   - PDFs com variáveis extraídas: {len(variaveis_extraidas)}")
    print(f"\n📁 Resultados salvos em:")
    print(f"   - resultados/cnpq_chamadas_{timestamp}.json")
    print(f"   - resultados/variaveis_extraidas_{timestamp}.json")
    print("=" * 80)
    
    # RETORNAR AS VARIÁVEIS
    return dados, links_chamadas, conteudos_chamadas, variaveis_extraidas

if __name__ == "__main__":
    # Executar e capturar os retornos
    cnpq_chamadas, cnpq_links_extraidos, conteudos_chamadas, variaveis_extraidas = main()
