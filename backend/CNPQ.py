"""
Script para raspagem de chamadas públicas do CNPq
Executa manualmente e salva resultado em JSON
Foco: Extrair links dos botões 'Chamada' dentro de divs com classe 'links-normas'
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from pathlib import Path
import pdfplumber
from io import BytesIO


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




def main():
    """
    Função principal
    """
    print("=" * 80)
    print("RASPADOR DE CHAMADAS PÚBLICAS DO CNPq")
    print("Foco: Botões 'Chamada' em divs com classe 'links-normas'")
    print("=" * 80)
    print()
    
    # Executar raspagem
    dados, conteudo_raspado = raspar_cnpq()
    
    # Processar resultados e criar variável cnpq_chamadas
    cnpq_chamadas = processar_resultado(dados)
    
    # Extrair links e criar variável cnpq_links_extraidos
    cnpq_links_extraidos = extrair_links_chamadas(cnpq_chamadas)
    
    # Buscar conteúdo de uma chamada específica (primeira da lista)
    conteudo_chamada = None
    pdf_texto_extraido = None
    
    if cnpq_links_extraidos:
        primeiro_link = cnpq_links_extraidos[0]
        conteudo_chamada = buscar_conteudo_chamada(primeiro_link)
        
        # Se for PDF, criar variável separada com o texto extraído
        if conteudo_chamada and conteudo_chamada.get('tipo') == 'PDF':
            pdf_texto_extraido = conteudo_chamada.get('texto_extraido', '')
            print(f"\n✅ Variável pdf_texto_extraido criada com {len(pdf_texto_extraido)} caracteres")
    
    # Mostrar apenas o resultado final
    if cnpq_chamadas['metadata']['status'] == 'sucesso':
        print("\n✅ Raspagem executada com sucesso!")
        
        # Mostrar preview das chamadas
        if cnpq_chamadas['chamadas']:
            print("\n📋 Preview de cnpq_chamadas:")
            for chamada in cnpq_chamadas['chamadas']:
                print(f"  ID {chamada['id']}: {chamada.get('link_chamada', 'N/A')}")
        
        # Mostrar preview do conteúdo da chamada
        if conteudo_chamada:
            print("\n📝 Preview de conteudo_chamada:")
            print(f"  Link: {conteudo_chamada.get('link', 'N/A')}")
            print(f"  Tipo: {conteudo_chamada.get('tipo', 'N/A')}")
            print(f"  Status: {conteudo_chamada.get('status_code', 'N/A')}")
            print(f"  Tamanho: {conteudo_chamada.get('tamanho_bytes', 0) / 1024:.2f} KB")
            
            if conteudo_chamada.get('tipo') == 'PDF':
                print(f"  Páginas: {conteudo_chamada.get('total_paginas', 'N/A')}")
                print(f"  Caracteres: {len(conteudo_chamada.get('texto_extraido', ''))}")
                print(f"\n  📖 Preview do texto (primeiros 300 caracteres):")
                preview = conteudo_chamada.get('preview_texto', '')[:300]
                print(f"  {preview}...")
            elif conteudo_chamada.get('tipo') == 'HTML':
                print(f"  Título: {conteudo_chamada.get('titulo_pagina', 'N/A')}")
    else:
        print("❌ Erro durante a raspagem. Verifique os logs acima.")
    
    # RETORNAR AS VARIÁVEIS
    return cnpq_chamadas, cnpq_links_extraidos, conteudo_chamada, pdf_texto_extraido


if __name__ == "__main__":
    # Executar e capturar os retornos
    cnpq_chamadas, cnpq_links_extraidos, conteudo_chamada, pdf_texto_extraido = main()
