"""
Cliente para la API de Notion - Adaptado del código original
"""
import requests # type: ignore
import logging
from typing import Dict, Any
from app.config import Config

logger = logging.getLogger(__name__)

class NotionAPI:
    """
    Clase centralizada para operaciones con Notion API
    Adaptada del código original con mejor manejo de errores
    """
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.notion.com/v1"
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Obtiene información de una página"""
        if not Config.NOTION_TOKEN:
            return {"error": "Token de Notion no configurado"}
        
        url = f"{self.base_url}/pages/{page_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo página {page_id}: {response.status_code}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Notion API: {str(e)}")
            return {"error": f"Error de conexión: {str(e)}"}
    
    def get_blocks(self, page_id: str) -> Dict[str, Any]:
        """Obtiene bloques de una página"""
        if not Config.NOTION_TOKEN:
            return {"error": "Token de Notion no configurado"}
        
        if not page_id:
            return {"error": "ID de página requerido"}
        
        url = f"{self.base_url}/blocks/{page_id}/children"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Obtenidos {len(data.get('results', []))} bloques de la página {page_id}")
                return data
            else:
                logger.error(f"Error obteniendo bloques de {page_id}: {response.status_code}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Notion API: {str(e)}")
            return {"error": f"Error de conexión: {str(e)}"}
    
    def add_block(self, page_id: str, block_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un bloque a la página"""
        if not Config.NOTION_TOKEN:
            return {"error": "Token de Notion no configurado"}
        
        if not page_id or not block_data:
            return {"error": "ID de página y datos del bloque son requeridos"}
        
        url = f"{self.base_url}/blocks/{page_id}/children"
        data = {"children": [block_data]}
        
        try:
            response = requests.patch(
                url, 
                headers=self.headers, 
                json=data, 
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Bloque agregado exitosamente a la página {page_id}")
                return {"success": True, "response": response.json()}
            else:
                logger.error(f"Error agregando bloque a {page_id}: {response.status_code}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Notion API: {str(e)}")
            return {"error": f"Error de conexión: {str(e)}"}
    
    def extract_text_from_blocks(self, blocks_data: Dict[str, Any]) -> str:
        """Extrae texto de los bloques de Notion (del código original)"""
        if "error" in blocks_data:
            return f"Error: {blocks_data['error']}"
        
        text_content = []
        for block in blocks_data.get('results', []):
            block_type = block.get('type', '')
            
            if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3']:
                rich_text = block.get(block_type, {}).get('rich_text', [])
                for text_obj in rich_text:
                    if text_obj.get('type') == 'text':
                        text_content.append(text_obj['text']['content'])
        
        return '\n'.join(text_content) if text_content else "No hay contenido de texto."
    
    def create_paragraph_block(self, content: str) -> Dict[str, Any]:
        """Crea un bloque de párrafo (del código original)"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content}
                    }
                ]
            }
        }
    
    def create_heading_block(self, content: str, level: int = 1) -> Dict[str, Any]:
        """Crea un bloque de encabezado"""
        heading_type = f"heading_{level}"
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content}
                    }
                ]
            }
        }
    
    def create_todo_block(self, content: str, checked: bool = False) -> Dict[str, Any]:
        """Crea un bloque de to-do (del código original)"""
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content}
                    }
                ],
                "checked": checked
            }
        }
    
    def analyze_page_structure(self, page_id: str) -> Dict[str, Any]:
        """Analiza la estructura de una página (del código original)"""
        blocks_data = self.get_blocks(page_id)
        
        if "error" in blocks_data:
            return {"error": blocks_data["error"]}
        
        structure = {
            "headings": 0,
            "paragraphs": 0,
            "lists": 0,
            "todos": 0,
            "total_blocks": len(blocks_data.get('results', []))
        }
        
        for block in blocks_data.get('results', []):
            block_type = block.get('type', '')
            
            if 'heading' in block_type:
                structure["headings"] += 1
            elif block_type == 'paragraph':
                structure["paragraphs"] += 1
            elif 'list' in block_type:
                structure["lists"] += 1
            elif block_type == 'to_do':
                structure["todos"] += 1
        
        return structure
    
    def is_configured(self) -> bool:
        """Verifica si la API está configurada correctamente"""
        return bool(Config.NOTION_TOKEN and len(Config.NOTION_TOKEN) > 10)
    
    def test_connection(self) -> Dict[str, Any]:
        """Prueba la conexión con la API de Notion"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Token de Notion no configurado"
            }
        
        # Intentar obtener información de la página por defecto
        if Config.DEFAULT_PAGE_ID:
            result = self.get_page(Config.DEFAULT_PAGE_ID)
            if "error" not in result:
                return {
                    "success": True,
                    "message": "Conexión exitosa con Notion API",
                    "page_title": result.get("properties", {}).get("title", {}).get("title", [{}])[0].get("plain_text", "Sin título")
                }
        
        return {
            "success": False,
            "error": "No se pudo conectar con la página especificada"
        }