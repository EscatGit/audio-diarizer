import os
import json
from typing import Dict, List, Any

class LightweightDiarizer:
    """
    Implementación ligera del diarizador de audio.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el diarizador con la configuración dada.
        
        Args:
            config: Diccionario con la configuración.
        """
        self.num_speakers = config.get('num_speakers', 2)
        print(f"Inicializando LightweightDiarizer con {self.num_speakers} hablantes")
        
    def process_audio(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Procesa un archivo de audio y devuelve los segmentos.
        
        En esta implementación ligera, simplemente devolvemos datos de ejemplo.
        
        Args:
            file_path: Ruta al archivo de audio.
            
        Returns:
            Lista de segmentos de audio diarizados.
        """
        print(f"Procesando archivo: {file_path}")
        
        # Esta es una implementación simulada. En un caso real, utilizaríamos
        # una biblioteca de procesamiento de audio como PyAudio, librosa, o
        # herramientas específicas de diarización.
        
        segments = []
        # Simulamos 3 segmentos por hablante
        for speaker_id in range(1, self.num_speakers + 1):
            for i in range(3):
                start = (speaker_id - 1) * 30 + i * 10
                end = start + 8
                segments.append({
                    "speaker": f"SPEAKER_{speaker_id}",
                    "start": start,
                    "end": end,
                    "text": f"Este es un texto de ejemplo para el hablante {speaker_id}, segmento {i+1}"
                })
        
        return segments
    
    def save_transcript(self, segments: List[Dict[str, Any]], output_path: str):
        """
        Guarda los segmentos como un archivo de transcripción.
        
        Args:
            segments: Lista de segmentos diarizados.
            output_path: Ruta donde guardar la transcripción.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for segment in segments:
                start_time = self._format_time(segment['start'])
                end_time = self._format_time(segment['end'])
                f.write(f"[{start_time} --> {end_time}] {segment['speaker']}: {segment['text']}\n\n")
        
        print(f"Transcripción guardada en: {output_path}")
    
    def _format_time(self, seconds: float) -> str:
        """
        Formatea los segundos en formato HH:MM:SS.
        
        Args:
            seconds: Tiempo en segundos.
            
        Returns:
            Tiempo formateado como string HH:MM:SS.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"