import pdfplumber
import os
from typing import List, Dict, Any, Optional, Tuple
from ..core.config import settings
import uuid


class PDFExtractor:
    @staticmethod
    def extract_text_with_pdfplumber(file_path: str) -> List[Tuple[str, int]]:
        """
        Extrai texto de um PDF usando pdfplumber
        
        Args:
            file_path: Caminho do arquivo PDF
            
        Returns:
            Lista de tuplas (texto, número da página)
        """
        result = []
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():  # Ignorar páginas vazias
                    result.append((text, i + 1))
        
        return result
    
    @staticmethod
    def extract_text_with_pymupdf(file_path: str) -> List[Tuple[str, int]]:
        """
        Método desabilitado - PyMuPDF não instalado
        Usando pdfplumber como alternativa
        """
        # Redirecionar para pdfplumber
        return PDFExtractor.extract_text_with_pdfplumber(file_path)
    
    @staticmethod
    def extract_text(file_path: str, method: str = "pdfplumber") -> List[Tuple[str, int]]:
        """
        Método principal para extrair texto de PDF
        
        Args:
            file_path: Caminho do arquivo PDF
            method: Método a usar ("pdfplumber" ou "pymupdf")
            
        Returns:
            Lista de tuplas (texto, número da página)
        """
        if method == "pymupdf":
            return PDFExtractor.extract_text_with_pymupdf(file_path)
        else:
            return PDFExtractor.extract_text_with_pdfplumber(file_path)
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = None) -> List[str]:
        """
        Divide o texto em chunks de tamanho aproximado
        
        Args:
            text: Texto a ser dividido
            chunk_size: Tamanho aproximado de cada chunk (em caracteres)
            
        Returns:
            Lista de chunks
        """
        if chunk_size is None:
            chunk_size = settings.PDF_CHUNK_SIZE
        
        # Dividir por parágrafos primeiro
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Se o parágrafo for muito grande, dividi-lo
            if len(paragraph) > chunk_size:
                # Adicionar o que já temos no current_chunk
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # Dividir o parágrafo grande em sentenças
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= chunk_size:
                        current_chunk += sentence + '. '
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence + '. '
            else:
                # Se adicionar este parágrafo exceder o tamanho do chunk, criar um novo
                if len(current_chunk) + len(paragraph) > chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = paragraph + '\n\n'
                else:
                    current_chunk += paragraph + '\n\n'
        
        # Adicionar o último chunk se não estiver vazio
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
