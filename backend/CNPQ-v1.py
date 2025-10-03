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


def salvar_resultado(dados, conteudo_raspado):
    """
    Salva os resultados em arquivos JSON
    """
    # Criar pasta de output se não existir
    output_dir = Path(__file__).parent / 'output' / 'cnpq'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Salvar dados estruturados
    arquivo_json = output_dir / f'cnpq_chamadas_{timestamp}.json'
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Arquivo salvo: {arquivo_json}")
    print(f"   Tamanho: {arquivo_json.stat().st_size / 1024:.2f} KB")
    
    # Salvar HTML bruto (opcional)
    if conteudo_raspado:
        arquivo_html = output_dir / f'cnpq_html_bruto_{timestamp}.html'
        with open(arquivo_html, 'w', encoding='utf-8') as f:
            f.write(conteudo_raspado)
        
        print(f"✅ HTML bruto salvo: {arquivo_html}")
        print(f"   Tamanho: {arquivo_html.stat().st_size / 1024:.2f} KB")
    
    return arquivo_json


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
    
    # Salvar resultados
    arquivo_salvo = salvar_resultado(dados, conteudo_raspado)
    
    print()
    print("=" * 80)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 80)
    print(f"Status: {dados['metadata']['status']}")
    print(f"Chamadas encontradas: {dados['metadata'].get('total_chamadas_encontradas', 0)}")
    print(f"Estratégia usada: {dados['metadata'].get('estrategia_usada', 'N/A')}")
    print(f"Arquivo principal: {arquivo_salvo}")
    print()
    
    if dados['metadata']['status'] == 'sucesso':
        print("✅ Raspagem executada com sucesso!")
        
        # Mostrar preview das primeiras chamadas
        if dados['chamadas']:
            print("\n📋 Preview das chamadas encontradas:")
            for chamada in dados['chamadas'][:5]:  # Mostrar apenas as 5 primeiras
                print(f"  ID {chamada['id']}: {chamada.get('link_chamada', 'N/A')}")
    else:
        print("❌ Erro durante a raspagem. Verifique os logs acima.")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
