#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilitário para consultar dados no ChromaDB
Permite verificar se os dados foram salvos corretamente
"""

import chromadb
from chromadb.utils import embedding_functions
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import argparse

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do ChromaDB
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000  # Porta padrão do ChromaDB

def conectar_chroma():
    """Conecta ao ChromaDB e retorna o cliente e a coleção"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Conectando ao ChromaDB em {CHROMA_HOST}:{CHROMA_PORT}...")
    
    try:
        # Conectar ao ChromaDB
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        
        # Verificar conexão
        collections = chroma_client.list_collections()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Conexão estabelecida. Collections disponíveis: {len(collections)}")
        
        # Listar coleções disponíveis
        if collections:
            print("\nColeções disponíveis:")
            for i, col in enumerate(collections, 1):
                print(f"  {i}. {col.name}")
        else:
            print("\n⚠️ Nenhuma coleção encontrada no ChromaDB.")
            return None, None
            
        # Obter coleção de editais
        collection = chroma_client.get_collection(name="editais_cnpq")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Coleção 'editais_cnpq' carregada com sucesso.")
        
        return chroma_client, collection
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ ERRO ao conectar com ChromaDB: {e}")
        return None, None

def listar_documentos(collection, limit=10):
    """Lista os documentos na coleção"""
    if not collection:
        return
        
    try:
        # Obter todos os IDs
        result = collection.get()
        ids = result.get("ids", [])
        metadatas = result.get("metadatas", [])
        
        total = len(ids)
        print(f"\n📊 Total de documentos na coleção: {total}")
        
        if total == 0:
            print("⚠️ Nenhum documento encontrado na coleção.")
            return
            
        # Mostrar amostra
        print(f"\n📄 Mostrando {min(limit, total)} documentos de exemplo:")
        for i in range(min(limit, total)):
            doc_id = ids[i]
            metadata = metadatas[i]
            
            # Extrair informações relevantes
            link = metadata.get("link", "N/A")
            chunk_index = metadata.get("chunk_index", "N/A")
            total_chunks = metadata.get("total_chunks", "N/A")
            processado_em = metadata.get("processado_em", "N/A")
            
            # Verificar se há variáveis extraídas
            if "variaveis_extraidas" in metadata:
                try:
                    vars_json = json.loads(metadata["variaveis_extraidas"])
                    apelido = vars_json.get("apelido_edital", "N/A")
                    financiador = vars_json.get("financiador_1", "N/A")
                    area = vars_json.get("area_foco", "N/A")
                    valor_min = vars_json.get("valor_min_R$", "N/A")
                    valor_max = vars_json.get("valor_max_R$", "N/A")
                    data_final = vars_json.get("data_final_submissao", "N/A")
                    
                    print(f"\n--- Documento {i+1}/{min(limit, total)} ---")
                    print(f"ID: {doc_id}")
                    print(f"Link: {link}")
                    print(f"Chunk: {chunk_index}/{total_chunks}")
                    print(f"Processado em: {processado_em}")
                    print(f"Apelido: {apelido}")
                    print(f"Financiador: {financiador}")
                    print(f"Área: {area}")
                    print(f"Valor: R$ {valor_min} a R$ {valor_max}")
                    print(f"Data final submissão: {data_final}")
                except Exception as e:
                    print(f"\n--- Documento {i+1}/{min(limit, total)} ---")
                    print(f"ID: {doc_id}")
                    print(f"Link: {link}")
                    print(f"Chunk: {chunk_index}/{total_chunks}")
                    print(f"Erro ao decodificar variáveis: {e}")
            else:
                print(f"\n--- Documento {i+1}/{min(limit, total)} ---")
                print(f"ID: {doc_id}")
                print(f"Link: {link}")
                print(f"Chunk: {chunk_index}/{total_chunks}")
                print(f"Processado em: {processado_em}")
                print("⚠️ Sem variáveis extraídas")
    except Exception as e:
        print(f"❌ ERRO ao listar documentos: {e}")

def buscar_documentos(collection, query, limit=5):
    """Busca documentos na coleção usando consulta semântica"""
    if not collection:
        return
        
    try:
        # Obter API key
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            print("❌ ERRO: OPENAI_API_KEY não encontrada. Configure a variável de ambiente.")
            return
            
        # Configurar embedding function
        embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
        
        print(f"\n🔍 Buscando por: '{query}'")
        results = collection.query(
            query_texts=[query],
            n_results=limit,
            include=["metadatas", "documents", "distances"]
        )
        
        # Processar resultados
        if results["ids"] and len(results["ids"][0]) > 0:
            print(f"\n✅ Encontrados {len(results['ids'][0])} resultados:")
            
            for i, (doc_id, metadata, document, distance) in enumerate(zip(
                results["ids"][0],
                results["metadatas"][0],
                results["documents"][0],
                results["distances"][0]
            )):
                # Extrair informações relevantes
                link = metadata.get("link", "N/A")
                chunk_index = metadata.get("chunk_index", "N/A")
                
                # Verificar se há variáveis extraídas
                vars_info = ""
                if "variaveis_extraidas" in metadata:
                    try:
                        vars_json = json.loads(metadata["variaveis_extraidas"])
                        apelido = vars_json.get("apelido_edital", "N/A")
                        financiador = vars_json.get("financiador_1", "N/A")
                        area = vars_json.get("area_foco", "N/A")
                        
                        vars_info = f"Apelido: {apelido} | Financiador: {financiador} | Área: {area}"
                    except:
                        vars_info = "Erro ao decodificar variáveis"
                
                print(f"\n--- Resultado {i+1} (Relevância: {1-distance:.2f}) ---")
                print(f"Link: {link} (Chunk {chunk_index})")
                if vars_info:
                    print(f"Info: {vars_info}")
                print(f"Trecho: {document[:200]}...")
        else:
            print("⚠️ Nenhum resultado encontrado.")
    except Exception as e:
        print(f"❌ ERRO ao buscar documentos: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Consulta dados no ChromaDB")
    parser.add_argument("--listar", action="store_true", help="Listar documentos na coleção")
    parser.add_argument("--buscar", type=str, help="Buscar documentos por consulta semântica")
    parser.add_argument("--limit", type=int, default=10, help="Limite de resultados")
    
    args = parser.parse_args()
    
    # Conectar ao ChromaDB
    client, collection = conectar_chroma()
    
    if not collection:
        print("❌ Não foi possível conectar à coleção. Verifique se o ChromaDB está em execução.")
        return
    
    # Executar ação solicitada
    if args.buscar:
        buscar_documentos(collection, args.buscar, args.limit)
    elif args.listar or (not args.buscar and not args.listar):
        listar_documentos(collection, args.limit)

if __name__ == "__main__":
    main()
