"""
Agente arquitecto de estructura - REFACTORIZADO
Toda la lógica de estructura movida desde el coordinador
"""
from typing import Dict, Any, List
import logging
from app.agents.base_agent import BaseAgent, AgentRole
from app.core.notion_client import NotionAPI
from app.config import Config

logger = logging.getLogger(__name__)

class StructureArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__("StructureArchitect", AgentRole.STRUCTURE_ARCHITECT)
        self.notion_api = NotionAPI()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceso principal de arquitectura de estructura"""
        page_id = input_data.get('page_id', Config.DEFAULT_PAGE_ID)
        structure_request = input_data.get('structure_request', '') or input_data.get('request', '')
        
        # Validar configuración
        if not Config.NOTION_TOKEN or not page_id:
            return {
                "agent": self.name,
                "error": "Configura NOTION_TOKEN y NOTION_PAGE_ID en .env",
                "implementation_status": "failed"
            }
        
        # Analizar contenido actual
        current_structure = self._analyze_current_structure(page_id)
        
        # Diseñar nueva estructura
        sections = self._design_structure(structure_request, current_structure)
        
        # Implementar estructura (lógica del coordinador original)
        sections_created = self._implement_structure(page_id, sections)
        
        return {
            "agent": self.name,
            "current_structure": current_structure,
            "new_structure": {"sections": sections},
            "sections_created": sections_created,
            "implementation_status": "completed" if sections_created > 0 else "failed"
        }
    
    def _analyze_current_structure(self, page_id: str) -> Dict[str, Any]:
        """Analiza la estructura actual de la página"""
        if Config.NOTION_TOKEN and page_id:
            return self.notion_api.analyze_page_structure(page_id)
        else:
            return {
                "headings": 0,
                "paragraphs": 0,
                "lists": 0,
                "todos": 0,
                "total_blocks": 0,
                "note": "Modo simulación"
            }
    
    def _design_structure(self, request: str, current: Dict[str, Any]) -> List[str]:
        """
        Diseña estructura basándose en la solicitud
        Lógica del coordinador original (líneas 267-290)
        """
        # Estructura por defecto
        default_sections = ["Introducción", "Desarrollo", "Conclusiones"]
        
        # Detectar si el usuario pide secciones específicas
        request_lower = request.lower()
        
        if 'proyecto' in request_lower or 'plan' in request_lower:
            return ["Objetivos", "Recursos", "Cronograma", "Entregables"]
        
        elif 'documento' in request_lower or 'informe' in request_lower:
            return ["Resumen Ejecutivo", "Introducción", "Desarrollo", "Conclusiones", "Referencias"]
        
        elif 'investigación' in request_lower or 'estudio' in request_lower:
            return ["Resumen", "Marco Teórico", "Metodología", "Resultados", "Discusión"]
        
        elif 'presentación' in request_lower:
            return ["Agenda", "Contexto", "Propuesta", "Beneficios", "Próximos Pasos"]
        
        # Si no hay match, usar estructura por defecto
        return default_sections
    
    def _implement_structure(self, page_id: str, sections: List[str]) -> int:
        """
        Implementa la estructura en Notion
        Lógica del coordinador original
        """
        sections_created = 0
        
        for section in sections:
            # Crear encabezado de sección
            heading = self.notion_api.create_heading_block(section, 2)
            result = self.notion_api.add_block(page_id, heading)
            
            if result.get("success"):
                sections_created += 1
                
                # Agregar un párrafo placeholder en cada sección
                placeholder = self.notion_api.create_paragraph_block(f"Contenido de {section.lower()}...")
                self.notion_api.add_block(page_id, placeholder)
        
        return sections_created
    
    def create_custom_structure(self, page_id: str, sections: List[str], 
                               with_placeholders: bool = True) -> Dict[str, Any]:
        """
        Método auxiliar para crear estructuras personalizadas
        """
        if not Config.NOTION_TOKEN or not page_id:
            return {
                "error": "Configuración inválida",
                "sections_created": 0
            }
        
        sections_created = 0
        
        for section in sections:
            heading = self.notion_api.create_heading_block(section, 2)
            result = self.notion_api.add_block(page_id, heading)
            
            if result.get("success"):
                sections_created += 1
                
                if with_placeholders:
                    placeholder = self.notion_api.create_paragraph_block(
                        f"Describe aquí el contenido de {section.lower()}..."
                    )
                    self.notion_api.add_block(page_id, placeholder)
        
        return {
            "success": sections_created > 0,
            "sections_created": sections_created,
            "total_sections": len(sections)
        }