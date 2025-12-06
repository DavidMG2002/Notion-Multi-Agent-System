"""
Agente analizador de contenido - REFACTORIZADO
Toda la lógica de análisis movida desde el coordinador
"""
from typing import Dict, Any, List
import logging
import requests
from app.agents.base_agent import BaseAgent, AgentRole
from app.core.notion_client import NotionAPI
from app.config import Config

logger = logging.getLogger(__name__)

class ContentAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("ContentAnalyzer", AgentRole.ANALYZER)
        self.notion_api = NotionAPI()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceso principal de análisis con Gemini"""
        page_id = input_data.get('page_id', Config.DEFAULT_PAGE_ID)
        question = input_data.get('question', '')
        
        # Validar configuración
        if not Config.NOTION_TOKEN or not page_id:
            return {
                "agent": self.name,
                "error": "Configura NOTION_TOKEN y NOTION_PAGE_ID en .env",
                "analysis": None
            }
        
        # Obtener contenido de Notion
        blocks = self.notion_api.get_blocks(page_id)
        
        if "error" in blocks:
            return {
                "agent": self.name,
                "error": f"Error obteniendo bloques: {blocks.get('error')}",
                "analysis": None
            }
        
        content = self.notion_api.extract_text_from_blocks(blocks)
        results = blocks.get('results', [])
        
        # Validar que hay contenido
        if not content or len(content.strip()) < 10:
            return {
                "agent": self.name,
                "analysis": f"La página tiene {len(results)} bloques pero parece estar vacía.",
                "blocks_count": len(results),
                "recommendations": ["Agrega contenido a la página para poder analizarlo"]
            }
        
        # Análisis con Gemini o básico
        if Config.GEMINI_API_KEY:
            analysis = self._analyze_with_gemini(content, question, len(results))
        else:
            analysis = f"Análisis básico: {len(results)} bloques encontrados. Configura GEMINI_API_KEY para análisis detallado."
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(content, len(results))
        
        return {
            "agent": self.name,
            "analysis": analysis,
            "blocks_count": len(results),
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "recommendations": recommendations
        }
    
    def _analyze_with_gemini(self, content: str, question: str, blocks_count: int) -> str:
        """Análisis usando Gemini (lógica del coordinador original)"""
        try:
            prompt = f"""Analiza este contenido de Notion y proporciona:
1. Resumen breve del contenido
2. 2-3 sugerencias concretas de mejora
3. Responde a esta pregunta si aplica: {question}

Contenido ({blocks_count} bloques):
{content[:1500]}

Sé conciso y directo."""
            
            # API REST de Gemini
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={Config.GEMINI_API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    return text
                else:
                    return f"Análisis: {blocks_count} bloques encontrados pero sin respuesta de IA."
            else:
                error_msg = response.json().get('error', {}).get('message', 'Error desconocido')
                logger.error(f"Error de Gemini API: {error_msg}")
                return f"Error de API: {error_msg[:100]}"
        
        except Exception as e:
            logger.error(f"Error con Gemini: {str(e)}")
            return f"Error al usar IA: {str(e)[:100]}"
    
    def _generate_recommendations(self, content: str, blocks_count: int) -> List[str]:
        """Genera recomendaciones automáticas basadas en el contenido"""
        recommendations = []
        
        # Contenido muy breve
        if len(content) < 100:
            recommendations.append("El contenido es muy breve, considera expandirlo")
        
        # Detectar tareas pendientes
        if "TODO" in content.upper() or "TASK" in content.upper() or "pendiente" in content.lower():
            recommendations.append("Detecté tareas, el TaskManager puede organizarlas mejor")
        
        # Pocos bloques
        if blocks_count < 5:
            recommendations.append("La página tiene pocos bloques, considera agregar más estructura")
        
        # Sin títulos
        if not any(word in content.lower() for word in ['#', 'título', 'sección']):
            recommendations.append("Agrega títulos o encabezados para mejorar la estructura")
        
        # Contenido muy largo sin estructura
        if len(content) > 1000 and blocks_count < 10:
            recommendations.append("El contenido es extenso, considera dividirlo en secciones")
        
        # Si no hay recomendaciones, dar una genérica
        if not recommendations:
            recommendations.append("El contenido está bien estructurado. Continúa así.")
        
        return recommendations