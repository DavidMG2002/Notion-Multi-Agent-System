"""
Script principal para ejecutar el sistema multi-agente
"""
from app import create_app
from app.config import Config

# Crear la aplicación Flask
app = create_app()

if __name__ == '__main__':
    # Validar configuración
    Config.validate_config()
    
    # Ejecutar la aplicación
    print("Iniciando Sistema Multi-Agente para Notion...")
    print(f"Servidor disponible en: http://{Config.HOST}:{Config.PORT}")
    
    app.run(
        debug=True,
        host= "0.0.0.0",
        port=8000
    )