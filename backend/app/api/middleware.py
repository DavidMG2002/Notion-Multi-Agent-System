"""
Middleware de seguridad para la aplicación Flask
"""
import time
import logging
from flask import request, jsonify
from functools import wraps
from app.config import Config

logger = logging.getLogger(__name__)

def rate_limit_middleware():
    """Middleware básico de rate limiting"""
    # Por simplicidad, implementación básica
    # En producción usar redis o similar
    pass

def security_headers_middleware(response):
    """Añade headers de seguridad a las respuestas"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

def log_request_middleware():
    """Log de requests para monitoreo"""
    start_time = time.time()
    
    def after_request(response):
        duration = time.time() - start_time
        logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")
        return response
    
    return after_request

def validate_json_middleware():
    """Valida que el JSON sea válido en requests POST"""
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            request.get_json(force=True)
        except Exception:
            return jsonify({"error": "JSON inválido"}), 400
    return None