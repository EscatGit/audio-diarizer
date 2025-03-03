# Audio Diarizer - Backend

Servicio de backend para la diarización de archivos de audio (identificación de quién habla y cuándo), con una versión ligera para desarrollo y una versión completa basada en Whisper para producción.

## Características

- **Versión ligera**: Implementación basada en librosa y características básicas de audio para desarrollo y pruebas
- **Versión completa**: Implementación basada en Whisper de OpenAI y PyAnnote para transcripción y diarización de alta calidad
- **API REST**: Interfaz RESTful usando FastAPI con soporte CORS para aplicaciones cliente
- **Frontend Web**: Interfaz de usuario sencilla con HTML, CSS y JavaScript (opcional)
- **Dockerizado**: Fácil de implementar y escalar con Docker

## Requisitos

- Docker y Docker Compose
- Python 3.9+ (si se ejecuta sin Docker)
- FFmpeg (instalado automáticamente en Docker)
- GPU con al menos 8GB VRAM (para la versión completa con Whisper)

## Estructura del Proyecto

```
/audio-diarizer/
  /app
    /api           # API de FastAPI
    /core          # Lógica de diarización
    /static        # Archivos estáticos (CSS, JS)
    /templates     # Plantillas HTML
    main.py        # Punto de entrada de la aplicación
  Dockerfile       # Configuración de Docker para versión ligera
  Dockerfile.full  # Configuración de Docker para versión completa
  docker-compose.yml        # Configuración de Docker Compose para desarrollo
  docker-compose.server.yml # Configuración de Docker Compose para producción
  requirements.txt          # Dependencias para versión ligera
  requirements-full.txt     # Dependencias para versión completa
```

## Instalación y Uso

### Desarrollo Local con Docker (versión ligera)

1. Asegúrate de tener Docker y Docker Compose instalados
2. Clona el repositorio
3. Ejecuta el servidor:

```bash
docker-compose up -d
```

El servidor estará disponible en `http://localhost:8000`

### Despliegue en Producción (versión completa con Whisper)

Para desplegar la versión completa con Whisper:

1. Asegúrate de tener una máquina con GPU compatible con CUDA
2. Descomenta las secciones relevantes en `app/core/whisper_diarizer.py`:
   - Busca todas las secciones marcadas con `# Uncomment when enabling the full version`
   - Descomenta las importaciones al principio del archivo:
     ```python
     import torch
     import whisper
     from pyannote.audio import Audio
     from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
     from pyannote.core import Segment
     from sklearn.cluster import AgglomerativeClustering
     ```
   - Descomenta la inicialización del modelo en el método `__init__`:
     ```python
     # Load Whisper model
     self.model = whisper.load_model(self.config["model_size"])
     
     # Load speaker embedding model for diarization
     self.embedding_model = PretrainedSpeakerEmbedding(
         "speechbrain/spkrec-ecapa-voxceleb", 
         device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
     )
     self.audio = Audio()
     ```
   - Descomenta los métodos auxiliares: `_ensure_wav_format`, `_get_audio_duration`, `_segment_embedding`
   - Descomenta la implementación real del método `process_audio`

3. Utiliza el archivo `Dockerfile.full` y la configuración para producción:

```bash
docker-compose -f docker-compose.server.yml up -d
```

4. Verifica que el servidor esté utilizando correctamente la GPU:
```bash
docker logs audio-diarizer-server | grep -i cuda
```
Deberías ver mensajes indicando que CUDA está disponible y se está utilizando.

## API REST

La aplicación expone una API RESTful para interactuar con el servicio de diarización. Esta API es utilizada tanto por la interfaz web como por la aplicación de escritorio.

### Endpoints

#### 1. Subir archivo de audio

```
POST /api/upload
```

**Descripción**: Sube un archivo de audio para ser procesado por el sistema de diarización.

**Parámetros del formulario**:
- `file` (Requerido): Archivo de audio en formato MP3, WAV, OGG o FLAC
- `num_speakers` (Opcional): Número de hablantes esperados en la grabación (entero, por defecto 2)
- `diarizer_type` (Opcional): Tipo de diarización ('lightweight' o 'whisper', por defecto el valor configurado en el servidor)

**Ejemplo de solicitud con curl**:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/ruta/a/tu/audio.mp3" \
  -F "num_speakers=3" \
  -F "diarizer_type=lightweight"
```

**Respuesta exitosa** (200 OK):
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing"
}
```

#### 2. Verificar estado de procesamiento

```
GET /api/status/{job_id}
```

**Descripción**: Obtiene el estado actual de un trabajo de diarización.

**Parámetros de ruta**:
- `job_id` (Requerido): Identificador único del trabajo de diarización

**Ejemplo de solicitud**:
```bash
curl "http://localhost:8000/api/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Respuesta para trabajo completado** (200 OK):
```json
{
  "status": "completed",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "segments": [
    {
      "speaker": "SPEAKER_1",
      "start": 0.0,
      "end": 5.2,
      "text": "Este es un texto de ejemplo para el hablante 1"
    },
    {
      "speaker": "SPEAKER_2",
      "start": 6.1,
      "end": 10.5,
      "text": "Este es un texto de ejemplo para el hablante 2"
    }
  ],
  "timestamp": "2025-03-03T14:30:45.123456",
  "diarizer_type": "lightweight"
}
```

**Respuesta para trabajo en proceso** (200 OK):
```json
{
  "status": "processing",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Respuesta para trabajo con error** (200 OK):
```json
{
  "status": "error",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "error": "Descripción del error",
  "timestamp": "2025-03-03T14:30:45.123456"
}
```

#### 3. Descargar transcripción

```
GET /api/transcript/{job_id}
```

**Descripción**: Descarga la transcripción completa en formato de texto.

**Parámetros de ruta**:
- `job_id` (Requerido): Identificador único del trabajo de diarización

**Ejemplo de solicitud**:
```bash
curl "http://localhost:8000/api/transcript/a1b2c3d4-e5f6-7890-abcd-ef1234567890" -o transcript.txt
```

**Respuesta exitosa** (200 OK):
```
SPEAKER_1 [00:00:00]
Este es un texto de ejemplo para el hablante 1 

SPEAKER_2 [00:00:06]
Este es un texto de ejemplo para el hablante 2 
```

**Respuesta con error** (404 Not Found):
```json
{
  "detail": "Transcript not found"
}
```

#### 4. Obtener configuración del servidor

```
GET /api/config
```

**Descripción**: Obtiene la configuración actual del servicio de diarización.

**Ejemplo de solicitud**:
```bash
curl "http://localhost:8000/api/config"
```

**Respuesta** (200 OK):
```json
{
  "diarizer_type": "lightweight"
}
```

### Cambios en la API al migrar del modelo ligero al completo

La API en sí no cambia entre las versiones ligera y completa. Los mismos endpoints funcionan exactamente igual en ambas versiones, lo que facilita la migración entre ellas. Sin embargo, hay algunas diferencias en el comportamiento:

1. **Tiempo de procesamiento**: La versión completa con Whisper tarda significativamente más en procesar los archivos, especialmente para grabaciones largas.

2. **Calidad de los resultados**: La versión completa proporciona:
   - Transcripciones más precisas
   - Mejor identificación de los cambios de hablante
   - Mejor manejo de idiomas diferentes del español o inglés
   - Información más detallada en los segmentos

3. **Formato de respuesta**: Aunque el formato es el mismo, la versión completa puede incluir metadatos adicionales en los segmentos, como puntuaciones de confianza.

4. **Requisitos del servidor**: La versión completa requiere más recursos (especialmente GPU), lo que puede influir en el tiempo de respuesta de la API.

Para los clientes de la API (como la aplicación de escritorio), la migración es transparente y no requiere cambios en el código que consume la API.

## Despliegue en TensorDock

Para desplegar en una instancia de TensorDock:

1. Crea una instancia con GPU en TensorDock (recomendado: al menos 8GB VRAM)
2. Instala Docker y dependencias:

```bash
# Actualizar paquetes
sudo apt-get update

# Instalar dependencias
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar soporte NVIDIA para Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

3. Clona el repositorio y despliega:

```bash
git clone https://github.com/tu-usuario/audio-diarizer.git
cd audio-diarizer
docker-compose -f docker-compose.server.yml up -d
```

## Variables de Entorno

Puedes configurar el comportamiento del servicio mediante variables de entorno:

- `DIARIZER_TYPE`: Tipo de diarización ('lightweight' o 'whisper')
- `ALLOW_CORS`: Habilitar CORS para conexiones desde diferentes orígenes (true/false)
- `TEMPLATES_DIR`: Ruta al directorio de plantillas
- `STATIC_DIR`: Ruta al directorio de archivos estáticos
- `PORT`: Puerto en el que se ejecutará el servidor (por defecto 8000)
- `HOST`: Host en el que se ejecutará el servidor (por defecto 0.0.0.0)

## Arquitectura del Sistema

El sistema está diseñado con una arquitectura modular:

1. **API Layer**: Maneja las solicitudes HTTP, la validación y las respuestas
2. **Core Layer**: Contiene la lógica de negocio para la diarización de audio
3. **Interface Layer**: Proporciona una interfaz web básica (opcional)

La versión ligera utiliza técnicas básicas de procesamiento de audio para simular la diarización, mientras que la versión completa utiliza modelos avanzados de IA.

## Licencia

[MIT](LICENSE)

## Contacto y Contribuciones

Para contribuir al proyecto:
1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request
