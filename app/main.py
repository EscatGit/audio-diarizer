from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# Cambiar importación relativa a absoluta
from app.api.routes import router as api_router

# Obtener rutas de directorios de variables de entorno o usar valores predeterminados
templates_dir = os.environ.get('TEMPLATES_DIR', 'app/templates')
static_dir = os.environ.get('STATIC_DIR', 'app/static')

# Imprimir información de depuración
print(f"🔍 Usando directorio de plantillas: {templates_dir}")
print(f"🔍 Usando directorio estático: {static_dir}")
print(f"🔍 Directorio actual: {os.getcwd()}")
print(f"🔍 Contenido del directorio de plantillas:")
try:
    if os.path.exists(templates_dir):
        print(f"   ✅ {templates_dir} existe")
        print(f"   Contenido: {os.listdir(templates_dir)}")
    else:
        print(f"   ❌ {templates_dir} no existe")
except Exception as e:
    print(f"   Error: {e}")

# Create FastAPI app
app = FastAPI(
    title="Audio Diarizer",
    description="API para diarización de audio",
    version="0.1.0"
)

# Configurar CORS para permitir solicitudes desde la aplicación Electron
# Verificar si CORS está habilitado desde variables de entorno
if os.environ.get('ALLOW_CORS', 'false').lower() in ('true', '1', 't'):
    print("✅ CORS habilitado para todos los orígenes")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permitir todos los orígenes
        allow_credentials=True,
        allow_methods=["*"],  # Permitir todos los métodos
        allow_headers=["*"],  # Permitir todos los encabezados
    )

# Asegurar que los directorios existan
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print("✅ Archivos estáticos montados correctamente")
except Exception as e:
    print(f"❌ Error al montar archivos estáticos: {e}")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página de inicio"""
    # Verificar si existe el template antes de intentar renderizarlo
    template_path = os.path.join(templates_dir, "index.html")
    if os.path.exists(template_path):
        print(f"✅ Usando template: {template_path}")
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        print(f"❌ No se encontró el template: {template_path}")
        # Template básico de respaldo
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Audio Diarizer</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #3498db; }
                .card { border: 1px solid #e1e5ea; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            </style>
        </head>
        <body>
            <h1>Audio Diarizer</h1>
            <div class="card">
                <p>El sistema está funcionando pero no se encontró la plantilla completa.</p>
                <p>Puedes subir archivos a través de la API: <code>/api/upload</code></p>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Verificación de estado"""
    return {
        "status": "healthy", 
        "version": app.version,
        "templates_dir": templates_dir,
        "templates_exists": os.path.exists(templates_dir),
        "index_exists": os.path.exists(os.path.join(templates_dir, "index.html")) if os.path.exists(templates_dir) else False,
        "cors_enabled": os.environ.get('ALLOW_CORS', 'false').lower() in ('true', '1', 't')
    }

if __name__ == "__main__":
    # Run the application when executed directly
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)