"""
Sistema Multi-Agente REFACTORIZADO
Coordinador limpio - Solo orquestación, sin lógica de negocio
"""
import hashlib
import logging
from datetime import datetime
from typing import Dict, List
from app.core.security import ContentGuardrails
from app.config import Config

# Importar agentes especializados
from app.agents.analyzer_agent import ContentAnalyzerAgent
from app.agents.creator_agent import ContentCreatorAgent
from app.agents.task_manager_agent import TaskManagerAgent
from app.agents.structure_agent import StructureArchitectAgent

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

class MultiAgentSystem:
    """
    Sistema coordinador multi-agente REFACTORIZADO
    Solo orquestación - Toda la lógica movida a los agentes especializados
    """
    
    def __init__(self):
        self.guardrails = ContentGuardrails()
        self.session_history = []
        self.rate_limiter = {}
        
        # Registro de agentes disponibles (solo para referencia)
        self.available_agents = {
            "analyzer": "ContentAnalyzerAgent",
            "creator": "ContentCreatorAgent",
            "task_manager": "TaskManagerAgent",
            "structure_architect": "StructureArchitectAgent"
        }
    
    def process_request(self, user_request: str, user_id: str = "anonymous") -> Dict:
        """Procesa una solicitud del usuario con todas las verificaciones de seguridad"""
        
        logger.info(f"Verificando seguridad para: {user_request[:50]}...")
        
        # 1. Rate limiting básico
        if not self._check_rate_limit(user_id):
            return {
                "error": "Demasiadas solicitudes. Espera un momento antes de continuar.",
                "rate_limited": True
            }
        
        # 2. Verificar si el usuario está bloqueado
        if self.guardrails.is_user_blocked(user_id):
            return {
                "error": "Usuario bloqueado por actividad sospechosa repetida",
                "blocked": True
            }
        
        # 3. Moderación inicial de la solicitud
        moderation_result = self.guardrails.moderate_content(user_request, user_id)
        
        # 4. Preparar datos de entrada seguros
        safe_request = moderation_result.sanitized_content or user_request
        
        logger.info("Procesando con sistema multi-agente...")
        
        # 5. Determinar qué agentes usar
        required_agents = self._determine_required_agents(safe_request)
        
        # 6. Procesar con agentes (DELEGACIÓN COMPLETA)
        try:
            response = self._process_agents(safe_request, required_agents, user_id)
            
            # 7. Guardar en historial
            self.session_history.append({
                'request_hash': hashlib.sha256(user_request.encode()).hexdigest()[:8],
                'safe': moderation_result.is_safe,
                'risk_level': moderation_result.risk_level.value,
                'timestamp': datetime.now().isoformat(),
                'agents_used': required_agents
            })
            
            # 8. Añadir información de seguridad a la respuesta
            return {
                "coordinator_response": response,
                "agents_used": required_agents,
                "security_info": {
                    "content_checked": True,
                    "risk_level": moderation_result.risk_level.value,
                    "was_sanitized": bool(moderation_result.sanitized_content)
                },
                "safety_checked": True
            }
            
        except Exception as e:
            security_logger.error(f"Error del sistema: {str(e)}")
            return {
                "error": "Error interno del sistema. El incidente ha sido registrado.",
                "system_error": True
            }
    
    def _determine_required_agents(self, request: str) -> List[str]:
        """Determina qué agentes necesitamos basado en la solicitud"""
        request_lower = request.lower()
        agents_needed = []
        
        if any(word in request_lower for word in ['analiza', 'qué hay', 'resumen', 'contenido', 'ver', 'muestra']):
            agents_needed.append('analyzer')
        
        if any(word in request_lower for word in ['crea', 'agrega', 'escribe', 'genera', 'añade', 'nuevo']):
            agents_needed.append('creator')
        
        if any(word in request_lower for word in ['tarea', 'todo', 'hacer', 'pendiente', 'lista']):
            agents_needed.append('task_manager')
        
        if any(word in request_lower for word in ['organiza', 'estructura', 'sección', 'título', 'reorganiza']):
            agents_needed.append('structure_architect')
        
        # Si no es claro, usar analizador por defecto
        if not agents_needed:
            agents_needed.append('analyzer')
        
        return agents_needed
    
    def _process_agents(self, request: str, agents: List[str], user_id: str) -> str:
        """
        Procesa los agentes - REFACTORIZADO
        Solo orquestación, sin lógica de negocio
        """
        responses = []
        page_id = Config.DEFAULT_PAGE_ID
        
        for agent_name in agents:
            try:
                # Instanciar el agente correspondiente
                agent = self._get_agent_instance(agent_name)
                
                # Preparar datos de entrada
                input_data = {
                    'page_id': page_id,
                    'request': request,
                    'question': request,
                    'topic': request,
                    'task_request': request,
                    'structure_request': request
                }
                
                # Llamar al agente con seguridad integrada
                result = agent.safe_process(input_data, user_id)
                
                # Formatear respuesta
                formatted_response = self._format_agent_response(agent_name, result)
                responses.append(formatted_response)
                
            except Exception as e:
                logger.error(f"Error procesando agente {agent_name}: {str(e)}")
                responses.append(f"{agent_name.title()}: Error al procesar - {str(e)[:100]}")
        
        return "\n\n".join(responses)
    
    def _get_agent_instance(self, agent_name: str):
        """Instancia el agente correspondiente"""
        if agent_name == 'analyzer':
            return ContentAnalyzerAgent()
        elif agent_name == 'creator':
            return ContentCreatorAgent()
        elif agent_name == 'task_manager':
            return TaskManagerAgent()
        elif agent_name == 'structure_architect':
            return StructureArchitectAgent()
        else:
            raise ValueError(f"Agente desconocido: {agent_name}")
    
    def _format_agent_response(self, agent_name: str, result: Dict) -> str:
        """Formatea la respuesta del agente para el usuario"""
        
        # Manejar errores
        if 'error' in result:
            return f"{agent_name.replace('_', ' ').title()}: {result['error']}"
        
        # Formatear según el tipo de agente
        if agent_name == 'analyzer':
            analysis = result.get('analysis', 'Sin análisis')
            recommendations = result.get('recommendations', [])
            recs_text = "\nRecomendaciones:\n- " + "\n- ".join(recommendations) if recommendations else ""
            return f"Análisis:\n{analysis}{recs_text}"
        
        elif agent_name == 'creator':
            content = result.get('content_generated', '')
            notion_result = result.get('notion_result', {})
            message = notion_result.get('message', f"Contenido creado: {content}")
            return f"Creador: {message}"
        
        elif agent_name == 'task_manager':
            tasks_count = result.get('tasks_created', 0)
            return f"Gestor de Tareas: {tasks_count} tareas creadas en Notion"
        
        elif agent_name == 'structure_architect':
            sections_count = result.get('sections_created', 0)
            status = result.get('implementation_status', 'unknown')
            return f"Arquitecto: Estructura creada con {sections_count} secciones ({status})"
        
        return f"{agent_name.title()}: Procesado exitosamente"
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Verifica el rate limiting básico"""
        current_time = datetime.now()
        
        if user_id not in self.rate_limiter:
            self.rate_limiter[user_id] = []
        
        # Limpiar requests antiguos (más de 1 hora)
        self.rate_limiter[user_id] = [
            req_time for req_time in self.rate_limiter[user_id]
            if (current_time - req_time).seconds < 3600
        ]
        
        # Verificar límite
        if len(self.rate_limiter[user_id]) >= Config.MAX_REQUESTS_PER_HOUR:
            return False
        
        # Agregar request actual
        self.rate_limiter[user_id].append(current_time)
        return True
    
    def get_system_status(self) -> Dict:
        """Obtiene el estado del sistema"""
        return {
            "agents_available": list(self.available_agents.keys()),
            "total_requests": len(self.session_history),
            "last_request": self.session_history[-1] if self.session_history else None,
            "safety_stats": self.guardrails.get_safety_stats(),
            "rate_limiter_stats": {
                "active_users": len(self.rate_limiter),
                "total_hourly_requests": sum(len(reqs) for reqs in self.rate_limiter.values())
            }
        }