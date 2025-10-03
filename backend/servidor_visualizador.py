"""
Servidor simples para visualizar dados do ChromaDB
Execute: python servidor_visualizador.py
Acesse: http://localhost:5000
"""

from flask import Flask, jsonify, send_file
from flask_cors import CORS
import chromadb
import os

app = Flask(__name__)
CORS(app)

# Configuração do ChromaDB - usar variáveis de ambiente ou padrões locais
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))

def get_chroma_client():
    return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

@app.route('/')
def index():
    return send_file('visualizar_chroma.html')

@app.route('/api/chroma/documents', methods=['GET'])
def get_documents():
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="editais_cnpq")

        # Pegar todos os documentos
        count = collection.count()

        if count == 0:
            return jsonify({
                'total': 0,
                'documents': []
            })

        # Buscar todos os documentos
        results = collection.get(
            limit=count,
            include=['documents', 'metadatas']
        )

        documents = []
        for i in range(len(results['ids'])):
            documents.append({
                'id': results['ids'][i],
                'document': results['documents'][i],
                'metadata': results['metadatas'][i]
            })

        # Ordenar por chunk_index
        documents.sort(key=lambda x: (
            x['metadata'].get('link', ''),
            x['metadata'].get('chunk_index', 0)
        ))

        return jsonify({
            'total': count,
            'documents': documents
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chroma/clear', methods=['POST'])
def clear_collection():
    try:
        client = get_chroma_client()
        client.delete_collection(name="editais_cnpq")
        return jsonify({'message': 'Coleção limpa com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chroma/stats', methods=['GET'])
def get_stats():
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="editais_cnpq")

        count = collection.count()

        if count == 0:
            return jsonify({
                'total': 0,
                'unique_editais': 0,
                'valid_chunks': 0
            })

        results = collection.get(
            limit=count,
            include=['metadatas']
        )

        unique_links = set()
        valid_chunks = 0

        for meta in results['metadatas']:
            if meta.get('link'):
                unique_links.add(meta['link'])
            if not meta.get('erro_extracao'):
                valid_chunks += 1

        return jsonify({
            'total': count,
            'unique_editais': len(unique_links),
            'valid_chunks': valid_chunks
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Servidor Visualizador ChromaDB")
    print("=" * 60)
    print(f"\nAcesse: http://localhost:5000")
    print(f"ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}")
    print("\nPressione Ctrl+C para parar\n")

    app.run(debug=True, port=5000, host='0.0.0.0')
