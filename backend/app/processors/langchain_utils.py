from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from ..core.config import settings
import os
import tempfile


class LangChainProcessor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.PDF_CHUNK_SIZE,
            chunk_overlap=200,
            length_function=len
        )
    
    def process_pdf(self, pdf_path):
        """
        Processa um PDF usando LangChain
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Lista de documentos processados
        """
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Dividir documentos em chunks
        texts = self.text_splitter.split_documents(documents)
        
        return texts
    
    def create_vectorstore(self, texts, collection_name=None):
        """
        Cria um vectorstore a partir de textos
        
        Args:
            texts: Lista de textos
            collection_name: Nome da coleção (opcional)
            
        Returns:
            Vectorstore
        """
        if collection_name:
            vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                collection_name=collection_name
            )
        else:
            vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings
            )
        
        return vectorstore
    
    def create_qa_chain(self, vectorstore):
        """
        Cria uma chain de QA a partir de um vectorstore
        
        Args:
            vectorstore: Vectorstore
            
        Returns:
            Chain de QA
        """
        llm = ChatOpenAI(
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        
        return qa_chain
    
    def query_documents(self, query, vectorstore):
        """
        Consulta documentos usando uma chain de QA
        
        Args:
            query: Consulta
            vectorstore: Vectorstore
            
        Returns:
            Resposta da consulta
        """
        qa_chain = self.create_qa_chain(vectorstore)
        response = qa_chain.run(query)
        
        return response
