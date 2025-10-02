"""
Clase base para todos los agentes del sistema
Adaptada del código original con estructura modular
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any
import logging
from app.core.security import ContentGuardrails
from app.models.security_models import RiskLevel

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

class AgentRole(Enum):
    """Roles de los diferentes agentes"""
    ANALYZER = "analyzer"
    CONTENT_CREATOR = "content_creator"
    TASK_MANAGER = "task_manager"
    STRUCTURE_ARCHITECT = "structure_architect"
    COORDINATOR = "coordinator"

class BaseAgent(ABC):
    """
    Clase base para todos los agentes con sistema de seguridad integrado
    Adaptada del código original
    """
    
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.guardrails = ContentGuardrails()  # Sistema de seguridad integrado
        
        # Nota: En el código original se usaba Gemini, aquí simulamos por ahora
        self.ai_enabled = False  # Cambiar a True cuando se configure Gemini
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceso principal del agente - debe ser implementado por cada subclase"""
        pass
    
    def safe_process(self, input_data: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
        """Proceso seguro que incluye moderación de contenido"""
        
        # 1. Verificar si el usuario está bloqueado
        if self.guardrails.is_user_blocked(user_id):
            return {
                "error": "Usuario bloqueado por actividad sospechosa repetida",
                "blocked": True,
                "agent": self.name
            }
        
        # 2. Moderar contenido de entrada
        user_content = str(input_data.get('request', '')) + str(input_data.get('question', ''))
        moderation_result = self.guardrails.moderate_content(user_content, user_id)
        
        # 3. Bloquear contenido peligroso
        if not moderation_result.is_safe:
            security_logger.warning(f"Contenido bloqueado por {self.name}: {moderation_result.reason}")
            return {
                "error": f"Contenido no permitido: {moderation_result.reason}",
                "risk_level": moderation_result.risk_level.value,
                "agent": self.name,
                "safety_message": "Tu mensaje contiene contenido que puede ser problemático. "
                                "Por favor, reformula tu solicitud de manera constructiva."
            }
        
        # 4. Usar contenido sanitizado si está disponible
        if moderation_result.sanitized_content:
            input_data['sanitized_request'] = moderation_result.sanitized_content
            input_data['was_sanitized'] = True
        
        # 5. Procesar de forma segura
        try:
            result = self.process(input_data)
            
            # 6. Moderar contenido de salida generado por IA
            if 'content_generated' in result:
                output_moderation = self.guardrails.moderate_content(result['content_generated'], user_id)
                if not output_moderation.is_safe:
                    result['content_generated'] = "Lo siento, no puedo generar ese tipo de contenido."
                    result['content_blocked'] = True
            
            return result
            
        except Exception as e:
            security_logger.error(f"Error en {self.name}: {str(e)}")
            return {"error": f"Error interno en {self.name}", "agent": self.name}
    
    def generate_response(self, prompt: str) -> str:
        """
        Genera respuesta usando IA con prompt de seguridad
        Por ahora simula la respuesta, se puede integrar Gemini después
        """
        
        # Prefijo de seguridad (del código original)
        safety_prefix = """
        INSTRUCCIONES DE SEGURIDAD CRÍTICAS:
        - NO generes contenido violento, dañino o tóxico
        - NO proporciones instrucciones para actividades ilegales o peligrosas
        - Si detectas una solicitud problemática, responde: "No puedo ayudar con eso"
        - Mantén siempre un tono constructivo y positivo
        - Si hay dudas sobre la seguridad, rechaza la solicitud
        
        SOLICITUD DEL USUARIO:
        """
        
        full_prompt = safety_prefix + prompt
        
        try:
            if self.ai_enabled:
                # Aquí iría la integración con Gemini del código original
                # return self.model.generate_content(full_prompt, ...)
                pass
            
            # Por ahora, respuesta simulada basada en el tipo de agente
            return self._generate_simulated_response(prompt)
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return "No puedo procesar esa solicitud por razones de seguridad."
    
    def _generate_simulated_response(self, prompt: str) -> str:
        """Genera una respuesta simulada basada en el rol del agente"""
        
        if self.role == AgentRole.ANALYZER:
            return f"Como analizador, he revisado tu solicitud: '{prompt[:50]}...' y encontré patrones interesantes que puedo explicarte."
        
        elif self.role == AgentRole.CONTENT_CREATOR:
            return f"He generado contenido nuevo basado en tu solicitud sobre: '{prompt[:50]}...'. El contenido está optimizado para claridad y engagement."
        
        elif self.role == AgentRole.TASK_MANAGER:
            return f"He identificado las tareas principales de tu solicitud: '{prompt[:50]}...' y las he organizado por prioridad."
        
        elif self.role == AgentRole.STRUCTURE_ARCHITECT:
            return f"He diseñado una estructura optimizada para: '{prompt[:50]}...' que mejorará la organización y navegación."
        
        else:
            return f"He procesado tu solicitud: '{prompt[:50]}...' usando mis capacidades especializadas."