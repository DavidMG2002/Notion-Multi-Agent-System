"""
Configuración de logging para la aplicación
"""
import logging
import sys
from app.config import Config

def setup_logging():
    """Configura el sistema de logging"""
    
    # Configuración básica
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log') if not Config.DEBUG else logging.NullHandler()
        ]
    )
    
    # Logger específico para seguridad
    security_logger = logging.getLogger('security')
    security_handler = logging.FileHandler('security.log')
    security_formatter = logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    )
    security_handler.setFormatter(security_formatter)
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    # Reducir logs de librerías externas
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)