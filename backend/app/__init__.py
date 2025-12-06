from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configurar CORS para permitir requests desde el frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Registrar rutas
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app