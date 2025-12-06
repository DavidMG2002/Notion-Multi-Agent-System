"""
Funciones auxiliares para la aplicación
"""
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Any

def hash_user_id(user_id: str) -> str:
    """Genera hash del user_id para privacidad"""
    return hashlib.sha256(user_id.encode()).hexdigest()[:8]

def sanitize_text(text: str) -> str:
    """Sanitiza texto básico"""
    if not text:
        return ""
    
    # Remover caracteres peligrosos
    text = re.sub(r'[<>"\']', '', text)
    
    # Limitar longitud
    return text[:2000]

def format_timestamp(dt: datetime = None) -> str:
    """Formatea timestamp para logs"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def extract_keywords(text: str) -> List[str]:
    """Extrae palabras clave de un texto"""
    if not text:
        return []
    
    # Palabras comunes a ignorar
    stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las'}
    
    # Extraer palabras
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filtrar palabras cortas y stop words
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    
    return list(set(keywords))[:10]  # Máximo 10 keywords únicos

def validate_page_id(page_id: str) -> bool:
    """Valida formato de page_id de Notion"""
    if not page_id:
        return False
    
    # Formato típico: 32 caracteres hexadecimales
    pattern = r'^[a-f0-9]{32}$|^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}
    return bool(re.match(pattern, page_id.replace('-', '')))

def create_response_template(success: bool = True, data: Any = None, error: str = None) -> Dict[str, Any]:
    """Crea template estándar de respuesta"""
    response = {
        "success": success,
        "timestamp": format_timestamp()
    }
    
    if success and data is not None:
        response["data"] = data
    elif not success and error:
        response["error"] = error
    
    return response