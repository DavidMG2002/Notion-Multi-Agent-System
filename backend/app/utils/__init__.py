"""
Configuración de la aplicación Flask
"""
from flask import Flask
from flask_cors import CORS
import logging

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app, 
         origins=["http://localhost:3000", "http://127.0.0.1:3000"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Registrar blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app