# Notion-Multi-Agent-System
Sistema multiagente de notion con IA

# Sistema Multi-Agente con Notion

Sistema inteligente de gestión de contenido para Notion con agentes especializados, análisis con IA y interfaz web interactiva.

## Stack Tecnológico

**Backend:**
- Flask 3.0.0 (Python Web Framework)
- Google Gemini API (Análisis con IA)
- Notion API (Integración con Notion)
- ContentGuardrails (Sistema de seguridad)

**Frontend:**
- React 18+ (UI Framework)
- Tailwind CSS (Estilos)
- Axios (Cliente HTTP)

---

## Características

- 4 Agentes Especializados (Analizador, Creador, Gestor de Tareas, Arquitecto)
- Interfaz web moderna con React
- Análisis inteligente con Google Gemini
- Sistema de seguridad con moderación de contenido
- Integración directa con Notion API

---

## Requisitos Previos

- Python 3.8+
- Node.js 16+ y npm
- Cuenta de Notion con integración creada
- API Key de Google Gemini (opcional)

---

## Instalación Rápida

### Backend (Flask)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Frontend (React)

```bash
cd frontend
npm install
```

---

## Configuración

### Backend (.env en /backend)

```env
# Notion
NOTION_TOKEN=secret_tu_token_aqui
NOTION_PAGE_ID=tu_page_id_aqui

# Gemini (opcional)
GEMINI_API_KEY=tu_api_key_aqui

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Seguridad
MAX_REQUESTS_PER_HOUR=50
MAX_SUSPICIOUS_ATTEMPTS=3
```

### Obtener credenciales:

**Token de Notion:**
1. Ve a https://www.notion.so/my-integrations
2. Crea nueva integración
3. Copia el token
4. Conecta la integración a tu página (⋯ > Add connections)

**Page ID:**
Copia el ID de la URL de tu página:
```
https://notion.so/workspace/Page-Name-123abc456def
                                        ^^^^^^^^^^^
```

**Gemini API:**
1. Ve a https://makersuite.google.com/app/apikey
2. Crea API Key
3. Copia la clave

---

## Ejecución

### Iniciar Backend

```bash
cd backend
python -m flask --app app run --host 0.0.0.0 --port 8000 --debug
```

Backend corriendo en: http://localhost:8000

### Iniciar Frontend

```bash
cd frontend
npm start
```

Frontend corriendo en: http://localhost:3000

---

## Uso

### Interfaz Web (React)

1. Abre http://localhost:3000
2. Escribe tu solicitud en el input
3. Ejemplos:
   - "Analiza el contenido de mi página"
   - "Crea titulo: Mi Proyecto"
   - "Genera 5 tareas para mi proyecto"
   - "Organiza la estructura del documento"

### API REST

**Procesar solicitud:**
```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"request": "Analiza mi página"}'
```

**Estado del sistema:**
```bash
curl http://localhost:8000/api/status
```

**Health check:**
```bash
curl http://localhost:8000/api/health
```

---

## Agentes Especializados

### Analyzer Agent
Analiza contenido con Gemini. Palabras clave: "analiza", "resumen", "qué hay"

### Creator Agent
Crea títulos y contenido. Palabras clave: "crea", "agrega", "añade"

### Task Manager Agent
Genera listas de tareas. Palabras clave: "tarea", "todo", "hacer"

### Structure Architect
Organiza páginas. Palabras clave: "organiza", "estructura", "sección"

---

## Estructura del Proyecto

```
proyecto/
├── backend/
│   ├── app/
│   │   ├── agents/           # Agentes especializados
│   │   ├── core/             # Coordinador y servicios
│   │   ├── models/           # Modelos de datos
│   │   └── api/              # Endpoints REST
│   ├── .env                  # Configuración
│   └── requirements.txt      # Dependencias Python
│
└── frontend/
    ├── src/
    │   ├── components/       # Componentes React
    │   ├── services/         # API calls
    │   └── App.js           # Componente principal
    ├── public/
    └── package.json          # Dependencias Node
```

---

## Dependencias

### Backend (requirements.txt)
```
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0"
  }
}
```

---

## Solución de Problemas

### Error: "ImportError: circular import"
- Verificar que `coordinator.py` esté en `app/core/`
- En `routes.py` usar: `from app.core.coordinator import MultiAgentSystem`

### Error: "Token de Notion no configurado"
- Verificar que `.env` exista en `/backend`
- Reiniciar el servidor Flask

### Error: "Cannot connect to backend"
- Verificar que backend esté corriendo en puerto 8000
- Verificar CORS en Flask si el frontend está en otro puerto

### Puerto en uso
```bash
# Cambiar puerto en .env (backend)
PORT=8001

# O en package.json (frontend)
"start": "PORT=3001 react-scripts start"
```

---

## Sistema de Seguridad

- Moderación de contenido automática
- Rate limiting (50 req/hora por defecto)
- Detección de patrones peligrosos
- Bloqueo de usuarios tras intentos sospechosos

Logs en: `backend/logs/security.log`

---

## Desarrollo

**Agregar nuevo agente:**
1. Crear clase en `backend/app/agents/nuevo_agent.py`
2. Heredar de `BaseAgent`
3. Implementar método `process()`
4. Registrar en `coordinator.py`

**Tests:**
```bash
pip install pytest
pytest
```

---

## Licencia

MIT License

---

## Changelog

### v1.0.0
- Sistema multi-agente modular
- Interfaz React con Tailwind CSS
- Integración Notion + Gemini
- Sistema de seguridad completo
- API REST documentada