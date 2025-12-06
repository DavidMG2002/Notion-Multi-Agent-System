"""
Agente gestor de tareas - REFACTORIZADO
Toda la lógica de tareas movida desde el coordinador
"""
from typing import Dict, Any, List
import logging
import re
import requests
from app.agents.base_agent import BaseAgent, AgentRole
from app.core.notion_client import NotionAPI
from app.config import Config

logger = logging.getLogger(__name__)

class TaskManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__("TaskManager", AgentRole.TASK_MANAGER)
        self.notion_api = NotionAPI()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceso principal de gestión de tareas"""
        page_id = input_data.get('page_id', Config.DEFAULT_PAGE_ID)
        task_request = input_data.get('task_request', '') or input_data.get('request', '')
        
        # Validar configuración
        if not Config.NOTION_TOKEN or not page_id:
            return {
                "agent": self.name,
                "error": "Configura NOTION_TOKEN y NOTION_PAGE_ID en .env",
                "tasks_created": 0
            }
        
        # Extraer o generar tareas (lógica del coordinador original)
        tasks_to_create = self._extract_or_generate_tasks(task_request, page_id)
        
        # Crear encabezado de tareas
        header = self.notion_api.create_heading_block("📋 Tareas", 2)
        self.notion_api.add_block(page_id, header)
        
        # Crear tareas en Notion
        tasks_created = 0
        for task in tasks_to_create:
            # Limpiar la tarea de caracteres especiales de markdown
            clean_task = task.replace('**', '').replace('*', '').replace('-', '').strip()
            
            if clean_task:  # Solo crear si hay contenido
                todo_block = self.notion_api.create_todo_block(clean_task)
                result = self.notion_api.add_block(page_id, todo_block)
                if result.get("success"):
                    tasks_created += 1
        
        return {
            "agent": self.name,
            "tasks_created": tasks_created,
            "tasks": tasks_to_create,
            "productivity_tips": self._get_productivity_tips()
        }
    
    def _extract_or_generate_tasks(self, request: str, page_id: str) -> List[str]:
        """
        Extrae o genera tareas usando Gemini
        Lógica del coordinador original (líneas 207-265)
        """
        tasks_to_create = []
        
        # Detectar si el usuario especifica tareas concretas
        if ':' in request and any(word in request.lower() for word in ['tarea', 'tareas', 'todo', 'hacer']):
            # Formato: "crea 3 tareas: tarea1, tarea2, tarea3"
            parts = request.split(':', 1)
            tasks_text = parts[1].strip()
            
            # Separar por comas o saltos de línea
            if ',' in tasks_text:
                tasks_to_create = [t.strip() for t in tasks_text.split(',') if t.strip()]
            elif '\n' in tasks_text:
                tasks_to_create = [t.strip() for t in tasks_text.split('\n') if t.strip()]
            else:
                tasks_to_create = [tasks_text]
        
        # Detectar número específico de tareas
        num_match = re.search(r'(\d+)\s*tarea', request.lower())
        desired_count = int(num_match.group(1)) if num_match else None
        
        # Si no hay tareas específicas, usar Gemini para generarlas
        if not tasks_to_create and Config.GEMINI_API_KEY:
            tasks_to_create = self._generate_tasks_with_gemini(request, page_id, desired_count)
        
        # Si aún no hay tareas, usar predeterminadas
        if not tasks_to_create:
            tasks_to_create = [
                f"Revisar: {request[:40]}",
                "Organizar la información relacionada",
                "Dar seguimiento y actualizar progreso"
            ]
        
        # Limitar al número deseado si se especificó
        if desired_count:
            tasks_to_create = tasks_to_create[:desired_count]
        
        return tasks_to_create
    
    def _generate_tasks_with_gemini(self, request: str, page_id: str, desired_count: int = None) -> List[str]:
        """Genera tareas usando Gemini basándose en el contexto"""
        try:
            # Obtener contexto de la página
            blocks = self.notion_api.get_blocks(page_id)
            content = ""
            if "error" not in blocks:
                content = self.notion_api.extract_text_from_blocks(blocks)[:800]
            
            count_instruction = f"Genera exactamente {desired_count} tareas" if desired_count else "Genera 3-5 tareas"
            
            prompt = f"""Basándote en esta solicitud: "{request}"
Y este contexto de la página:
{content if content else "Sin contexto disponible"}

{count_instruction} específicas y accionables.
Cada tarea debe ser:
- Clara y concisa (máximo 60 caracteres)
- Realista y alcanzable
- Sin numeración ni viñetas

Responde SOLO con las tareas, una por línea."""
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={Config.GEMINI_API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 300
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    tasks = [t.strip() for t in text.split('\n') if t.strip() and len(t.strip()) > 5]
                    return tasks if tasks else []
        
        except Exception as e:
            logger.error(f"Error generando tareas con Gemini: {str(e)}")
        
        return []
    
    def _prioritize_tasks(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """Prioriza tareas automáticamente"""
        prioritized = []
        for i, task in enumerate(tasks):
            priority = "Alta" if i < 2 else "Media" if i < 4 else "Baja"
            prioritized.append({
                "task": task,
                "priority": priority,
                "estimated_time": self._estimate_time(task)
            })
        return prioritized
    
    def _estimate_time(self, task: str) -> str:
        """Estima el tiempo de una tarea basado en heurísticas"""
        if len(task) > 50 or "investigar" in task.lower():
            return "2-3 horas"
        elif "llamar" in task.lower() or "email" in task.lower():
            return "15-30 min"
        else:
            return "30-60 min"
    
    def _get_productivity_tips(self) -> List[str]:
        """Retorna tips de productividad"""
        return [
            "Comienza con las tareas de alta prioridad",
            "Usa la técnica Pomodoro para mantener el foco",
            "Revisa tu progreso cada día"
        ]