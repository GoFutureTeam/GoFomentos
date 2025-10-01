import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from ..core.config import settings


class DataExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def extract_data_from_chunk(self, chunk: str, edital_uuid: str, pdf_url: str) -> Dict[str, Any]:
        """
        Extrai dados estruturados de um chunk de texto usando OpenAI
        
        Args:
            chunk: Texto do chunk
            edital_uuid: UUID do edital
            pdf_url: URL do PDF
            
        Returns:
            Dicionário com dados extraídos
        """
        prompt = f"""
        Analise o seguinte trecho de um edital e extraia as informações solicitadas.
        Se não encontrar a informação, deixe o campo como null.
        
        Trecho do edital:
        {chunk}
        
        Extraia os seguintes dados no formato JSON:
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
          "observacoes": "STRING"
        }}
        
        Responda APENAS com o JSON, sem texto adicional.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em extrair informações estruturadas de editais."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Extrair o JSON da resposta
            content = response.choices[0].message.content.strip()
            
            try:
                extracted_data = json.loads(content)
                # Adicionar campos fixos
                extracted_data["uuid"] = edital_uuid
                extracted_data["link"] = pdf_url
                extracted_data["origem"] = pdf_url
                
                return extracted_data
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON da resposta: {content}")
                return {"uuid": edital_uuid, "link": pdf_url, "origem": pdf_url}
                
        except Exception as e:
            print(f"Erro ao extrair dados com OpenAI: {e}")
            return {"uuid": edital_uuid, "link": pdf_url, "origem": pdf_url}
    
    def consolidate_data(self, extracted_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolida dados extraídos de múltiplos chunks
        
        Args:
            extracted_data_list: Lista de dicionários com dados extraídos
            
        Returns:
            Dicionário consolidado
        """
        if not extracted_data_list:
            return {}
        
        # Inicializar com os campos fixos do primeiro item
        result = {
            "uuid": extracted_data_list[0].get("uuid", ""),
            "link": extracted_data_list[0].get("link", ""),
            "origem": extracted_data_list[0].get("origem", "")
        }
        
        # Campos de texto que devem ser concatenados
        text_fields = ["descricao_completa", "observacoes"]
        
        # Campos que devem ser preenchidos com o primeiro valor não nulo encontrado
        priority_fields = [
            "apelido_edital", "financiador_1", "financiador_2", "area_foco",
            "tipo_proponente", "empresas_que_podem_submeter", "tipo_recurso",
            "recepcao_recursos", "tipo_contrapartida"
        ]
        
        # Campos numéricos que devem ser preenchidos com o valor mínimo/máximo encontrado
        min_fields = ["duracao_min_meses", "valor_min_R$", "contrapartida_min_%"]
        max_fields = ["duracao_max_meses", "valor_max_R$", "contrapartida_max_%"]
        
        # Campos booleanos que devem ser True se qualquer chunk tiver True
        bool_fields = ["custeio", "capital"]
        
        # Campos de data que devem ser preenchidos com o primeiro valor não nulo encontrado
        date_fields = ["data_inicial_submissao", "data_final_submissao", "data_resultado"]
        
        # Processar cada tipo de campo
        for field in text_fields:
            values = [data.get(field, "") for data in extracted_data_list if data.get(field)]
            result[field] = "\n\n".join(values)
        
        for field in priority_fields:
            for data in extracted_data_list:
                if data.get(field):
                    result[field] = data[field]
                    break
        
        for field in min_fields:
            values = [data.get(field) for data in extracted_data_list if data.get(field) is not None]
            if values:
                result[field] = min(values)
        
        for field in max_fields:
            values = [data.get(field) for data in extracted_data_list if data.get(field) is not None]
            if values:
                result[field] = max(values)
        
        for field in bool_fields:
            result[field] = any(data.get(field, False) for data in extracted_data_list)
        
        for field in date_fields:
            for data in extracted_data_list:
                if data.get(field):
                    result[field] = data[field]
                    break
        
        return result
