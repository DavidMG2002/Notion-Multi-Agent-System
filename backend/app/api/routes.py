"""
Rutas de la API REST sistema multi-agente
"""
import logging
from flask import Blueprint, jsonify, request
from app.core.coordinator import MultiAgentSystem

# Crear blueprint para las rutas de la API
api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Instancia global del sistema multi-agente
multi_agent_system = MultiAgentSystem()

@api_bp.route('/')
def root():
    """Endpoint raíz"""
    return jsonify({
        "message": "Sistema Multi-Agente para Notion",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    })

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "multi-agent-notion-system",
        "version": "1.0.0"
    })

@api_bp.route('/api/process-request', methods=['POST'])
def process_request():
    """Procesa una solicitud usando el sistema multi-agente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibió data JSON"}), 400
        
        user_request = data.get("request", "")
        user_id = data.get("user_id", "anonymous")
        
        if not user_request.strip():
            return jsonify({"error": "La solicitud no puede estar vacía"}), 400
        
        logger.info(f"Nueva solicitud de usuario: {user_id}")
        
        result = multi_agent_system.process_request(user_request, user_id)
        
        if result.get('error'):
            status_code = 403 if 'no permitido' in str(result.get('error')) else 400
            return jsonify(result), status_code
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error procesando solicitud: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado"
        }), 500

@api_bp.route('/api/system-status')
def get_system_status():
    """Obtiene el estado actual del sistema"""
    try:
        status = multi_agent_system.get_system_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {str(e)}")
        return jsonify({
            "error": "Error obteniendo estado del sistema"
        }), 500

@api_bp.route('/api/agents')
def get_available_agents():
    """Lista todos los agentes disponibles y sus capacidades"""
    agents_info = {
        "analyzer": {
            "name": "ContentAnalyzer",
            "description": "Analiza contenido existente en Notion",
            "capabilities": ["análisis de texto", "extracción de insights", "recomendaciones"]
        },
        "creator": {
            "name": "ContentCreator", 
            "description": "Genera nuevo contenido",
            "capabilities": ["creación de párrafos", "listas", "encabezados"]
        },
        "task_manager": {
            "name": "TaskManager",
            "description": "Gestiona tareas y to-dos",
            "capabilities": ["organización de tareas", "priorización", "estimación de tiempo"]
        },
        "structure_architect": {
            "name": "StructureArchitect",
            "description": "Organiza la estructura del contenido",
            "capabilities": ["diseño de jerarquías", "organización", "navegación"]
        }
    }
    
    return jsonify({
        "agents_available": len(agents_info),
        "agents": agents_info
    })

@api_bp.route('/api/moderate-content', methods=['POST'])
def moderate_content():
    """Endpoint para moderar contenido directamente (para testing)"""
    try:
        data = request.get_json()
        content = data.get("content", "")
        user_id = data.get("user_id", "anonymous")
        
        result = multi_agent_system.guardrails.moderate_content(content, user_id)
        
        return jsonify({
            "is_safe": result.is_safe,
            "risk_level": result.risk_level.value,
            "reason": result.reason,
            "flagged_words_count": len(result.flagged_words),
            "flagged_patterns_count": len(result.flagged_patterns),
            "sanitized": bool(result.sanitized_content)
        })
        
    except Exception as e:
        logger.error(f"Error moderando contenido: {str(e)}")
        return jsonify({
            "error": "Error en la moderación de contenido"
        }), 500