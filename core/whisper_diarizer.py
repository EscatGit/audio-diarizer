"""
This module is intentionally left commented out in the lightweight version.
Uncomment and install the required dependencies for the full Whisper-based diarizer.
"""

import os
import subprocess
import datetime
import wave
import contextlib
import numpy as np
from typing import Dict, List, Any, Optional
from .diarizer import Diarizer

"""
# Uncomment these imports when enabling the full version
import torch
import whisper
from pyannote.audio import Audio
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.core import Segment
from sklearn.cluster import AgglomerativeClustering
"""

class WhisperDiarizer(Diarizer):
    """
    Full implementation of audio diarization using Whisper for transcription
    and PyAnnote for speaker diarization.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.config.setdefault("num_speakers", 2)
        self.config.setdefault("language", "any")
        self.config.setdefault("model_size", "base")  # ['tiny', 'base', 'small', 'medium', 'large']
        
        """
        # Uncomment when enabling the full version
        # Load Whisper model
        self.model = whisper.load_model(self.config["model_size"])
        
        # Load speaker embedding model for diarization
        self.embedding_model = PretrainedSpeakerEmbedding(
            "speechbrain/spkrec-ecapa-voxceleb", 
            device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.audio = Audio()
        """
    
    def _ensure_wav_format(self, audio_path: str) -> str:
        """Convert audio to WAV format if it's not already"""
        if audio_path.lower().endswith('.wav'):
            # Check if it's a valid WAV file
            try:
                with wave.open(audio_path, 'r') as f:
                    return audio_path
            except wave.Error:
                pass  # Not a valid WAV file, convert it
        
        # Convert to WAV
        output_path = os.path.splitext(audio_path)[0] + '_converted.wav'
        subprocess.call(['ffmpeg', '-i', audio_path, '-ar', '16000', '-ac', '1', 
                         '-c:a', 'pcm_s16le', output_path, '-y'])
        return output_path
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of an audio file"""
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        return duration
    
    def _segment_embedding(self, segment: Dict[str, Any], audio_path: str, duration: float):
        """
        Extract speaker embedding for a segment.
        This is commented out by default since it requires PyAnnote.
        """
        """
        # Uncomment when enabling the full version
        try:
            start, end = segment["start"], min(duration, segment["end"])
            clip = Segment(start, end)
            waveform, sample_rate = self.audio.crop(audio_path, clip)

            if not isinstance(waveform, torch.Tensor):
                waveform = torch.tensor(waveform)

            if waveform.ndim == 1:  # Convert 1D tensor to 3D
                waveform = waveform.unsqueeze(0).unsqueeze(0)
            elif waveform.ndim == 2:  # Convert [channels, samples] to [1, channels, samples]
                waveform = waveform.unsqueeze(0)

            if waveform.shape[1] > 1:
                waveform = waveform.mean(dim=1, keepdim=True)

            waveform = waveform.to(torch.float32)

            assert waveform.shape[1] == 1, "Waveform must be mono (1 channel)"

            return self.embedding_model(waveform)
        except Exception as e:
            print(f"Error processing segment {segment['start']} - {segment['end']}: {e}")
            return np.zeros(192)  # Return a dummy embedding
        """
        # Placeholder for lightweight version
        return np.zeros(192)
    
    def process_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Process audio file and return diarized segments.
        In lightweight version, this returns a message.
        """
        return [
            {
                "start": 0,
                "end": 1,
                "text": "This is the WhisperDiarizer stub. To enable the full functionality, uncomment the code in whisper_diarizer.py and install the required dependencies.",
                "speaker": "SYSTEM"
            }
        ]
        
        """
        # Uncomment when enabling the full version
        # Ensure WAV format
        wav_path = self._ensure_wav_format(audio_path)
        
        # Get audio duration
        duration = self._get_audio_duration(wav_path)
        
        # Transcribe with Whisper
        language = None if self.config["language"] == "any" else self.config["language"]
        result = self.model.transcribe(wav_path, language=language)
        segments = result.get("segments", [])
        
        if not segments:
            return []
        
        # Compute embeddings for each segment
        embeddings = np.zeros((len(segments), 192))
        for i, segment in enumerate(segments):
            embeddings[i] = self._segment_embedding(segment, wav_path, duration)
        
        # Handle NaN values
        embeddings = np.nan_to_num(embeddings)
        
        # Perform speaker clustering
        clustering = AgglomerativeClustering(
            n_clusters=self.config["num_speakers"]
        ).fit(embeddings)
        
        # Assign speaker labels
        for i, segment in enumerate(segments):
            segment["speaker"] = f"SPEAKER {clustering.labels_[i] + 1}"
        
        return segments
        """
