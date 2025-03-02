# Audio Diarizer

Una aplicación para la diarización de archivos de audio (identificación de quién habla y cuándo), con una versión ligera para desarrollo y una versión completa basada en Whisper para producción.

## Características

- **Versión ligera**: Implementación basada en librosa y características básicas de audio para desarrollo y pruebas
- **Versión completa**: Implementación basada en Whisper de OpenAI y PyAnnote para transcripción y diarización de alta calidad
- **API**: Interfaz RESTful usando FastAPI
- **Frontend**: Interfaz de usuario sencilla con HTML, CSS y JavaScript
- **Dockerizado**: Fácil de implementar y escalar con Docker

## Requisitos

- Docker y Docker Compose
- Python 3.9+ (si se ejecuta sin Docker)
- FFmpeg (instalado automáticamente en Docker)

## Estructura del Proyecto

```
/audio-diarizer
  /app
    /api           # API de FastAPI
    /core          # Lógica de diarización
    /static        # Archivos estáticos (CSS, JS)
    /templates     # Plantillas HTML
    main.py        # Punto de entrada de la aplicación
  Dockerfile       # Configuración de Docker
  docker-compose.yml  # Configuración de Docker Compose
  requirements.txt    # Dependencias para versión ligera
  requirements-full.txt  # Dependencias para versión completa
```

## Instalación y Uso

### Usando Docker (recomendado)

1. Clona el repositorio:

```bash
git clone https://github.com/tuusuario/audio-diarizer.git
cd audio-diarizer
```

2. Inicia la aplicación con Docker Compose:

```bash
docker-compose up -d
```

La aplicación estará disponible en http://localhost:8000

### Cambiar a la versión completa con Whisper

1. Edita el archivo `docker-compose.yml` y descomenta la línea:

```yaml
# - DIARIZER_TYPE=whisper
```

2. Reconstruye la imagen con las dependencias completas:

```bash
docker-compose down
docker build -f Dockerfile.full -t audio-diarizer-full .
docker-compose up -d
```

### Instalación manual (desarrollo)

1. Clona el repositorio:

```bash
git clone https://github.com/tuusuario/audio-diarizer.git
cd audio-diarizer
```

2. Crea un entorno virtual e instala las dependencias:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```bash
uvicorn app.main:app --reload
```

## API REST

La aplicación expone los siguientes endpoints:

- `POST /api/upload` - Sube un archivo de audio para procesamiento
- `GET /api/status/{job_id}` - Obtiene el estado de un trabajo de diarización
- `GET /api/transcript/{job_id}` - Descarga la transcripción completa
- `GET /api/config` - Obtiene la configuración actual de la aplicación

## Personalización

### Número de hablantes

Puedes especificar el número de hablantes esperados al subir el archivo mediante el parámetro `num_speakers` (por defecto es 2).

### Tipo de diarizador

Puedes cambiar entre la versión ligera y la versión completa mediante la variable de entorno `DIARIZER_TYPE`:

- `lightweight` - Usa la implementación ligera (por defecto)
- `whisper` - Usa la implementación completa basada en Whisper

## Licencia

[MIT](LICENSE)
