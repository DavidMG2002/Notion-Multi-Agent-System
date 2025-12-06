"""
Agente creador de contenido - REFACTORIZADO
Toda la lógica de creación movida desde el coordinador
"""
from typing import Dict, Any, Tuple
import logging
from app.agents.base_agent import BaseAgent, AgentRole
from app.core.notion_client import NotionAPI
from app.config import Config

logger = logging.getLogger(__name__)

class ContentCreatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("ContentCreator", AgentRole.CONTENT_CREATOR)
        self.notion_api = NotionAPI()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceso principal de creación de contenido"""
        page_id = input_data.get('page_id', Config.DEFAULT_PAGE_ID)
        request = input_data.get('topic', '') or input_data.get('request', '')
        
        # Validar configuración
        if not Config.NOTION_TOKEN or not page_id:
            return {
                "agent": self.name,
                "error": "Configura NOTION_TOKEN y NOTION_PAGE_ID en .env",
                "content_generated": None
            }
        
        # Extraer título limpio (lógica del coordinador original)
        title = self._extract_clean_title(request)
        
        # Crear SOLO el encabezado en Notion
        heading = self.notion_api.create_heading_block(title, 2)
        result = self.notion_api.add_block(page_id, heading)
        
        if result.get("success"):
            return {
                "agent": self.name,
                "content_generated": title,
                "content_type": "heading",
                "notion_result": {
                    "success": True,
                    "message": f"Título '{title}' agregado exitosamente"
                }
            }
        else:
            return {
                "agent": self.name,
                "error": f"Error al crear contenido: {result.get('error')}",
                "content_generated": None
            }
    
    def _extract_clean_title(self, request: str) -> str:
        """
        Extrae el título limpio de la solicitud
        Lógica del coordinador original (líneas 182-205)
        """
        title = request
        
        # Detectar formato "agrega titulo: X" y extraer solo X
        if ':' in request:
            # Tomar solo lo que está después de ":"
            title = request.split(':', 1)[1].strip()
        
        # Quitar palabras de comando si no hay ":"
        elif any(word in request.lower() for word in ['agrega', 'crea', 'genera', 'añade']):
            words_to_remove = ['agrega', 'crea', 'genera', 'añade', 'titulo', 'título', 'un', 'una']
            title_words = request.split()
            title = ' '.join([w for w in title_words if w.lower() not in words_to_remove])
        
        # Capitalizar primera letra si está todo en minúsculas
        if title and title[0].islower():
            title = title[0].upper() + title[1:]
        
        return title if title else request[:50]
    
    def _parse_and_create(self, request: str) -> Tuple[str, str]:
        """
        Extrae el tipo de contenido y el contenido de la solicitud
        (Método alternativo para soporte de múltiples tipos)
        """
        request_lower = request.lower()
        
        # Detectar tipo de contenido
        if 'titulo:' in request_lower or 'título:' in request_lower:
            content = request.split(':', 1)[1].strip()
            return ('heading', content)
        
        elif 'parrafo:' in request_lower or 'párrafo:' in request_lower:
            content = request.split(':', 1)[1].strip()
            return ('paragraph', content)
        
        elif 'tarea:' in request_lower:
            content = request.split(':', 1)[1].strip()
            return ('todo', content)
        
        # Por defecto, crear título
        else:
            return ('heading', self._extract_clean_title(request))
    
    def create_custom_content(self, page_id: str, content_type: str, content: str) -> Dict[str, Any]:
        """
        Método auxiliar para crear diferentes tipos de contenido
        """
        if content_type == 'heading':
            block = self.notion_api.create_heading_block(content, 2)
        elif content_type == 'paragraph':
            block = self.notion_api.create_paragraph_block(content)
        elif content_type == 'todo':
            block = self.notion_api.create_todo_block(content)
        else:
            block = self.notion_api.create_paragraph_block(content)
        
        result = self.notion_api.add_block(page_id, block)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Contenido '{content_type}' agregado: {content[:30]}..."
            }
        else:
            return {"error": result.get("error", "Error desconocido")}