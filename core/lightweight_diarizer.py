import os
import subprocess
import datetime
import wave
import contextlib
import numpy as np
import json
from typing import Dict, List, Any, Optional
from sklearn.cluster import AgglomerativeClustering
import librosa
from .diarizer import Diarizer

class LightweightDiarizer(Diarizer):
    """
    A lightweight implementation of audio diarization using librosa for audio processing
    and simple energy-based voice activity detection.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.config.setdefault("num_speakers", 2)  # Default to 2 speakers if not specified
        self.config.setdefault("min_segment_length", 1.0)  # Minimum segment length in seconds
        self.config.setdefault("energy_threshold", 0.1)  # Energy threshold for VAD
    
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
    
    def _extract_features(self, audio_path: str) -> np.ndarray:
        """Extract MFCC features from audio"""
        y, sr = librosa.load(audio_path, sr=16000)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        return mfccs.T  # Transpose to get (time, features)
    
    def _detect_voice_activity(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Simple energy-based voice activity detection"""
        # Calculate energy
        energy = librosa.feature.rms(y=y)[0]
        
        # Normalize energy
        energy = energy / np.max(energy)
        
        # Apply threshold
        is_speech = energy > self.config["energy_threshold"]
        
        # Convert to segments
        segments = []
        in_segment = False
        start_time = 0
        min_samples = int(self.config["min_segment_length"] * sr)
        
        for i, speech in enumerate(is_speech):
            frame_time = librosa.samples_to_time(i * 512, sr=sr)  # 512 is the default hop length
            
            if speech and not in_segment:
                # Start of a new segment
                in_segment = True
                start_time = frame_time
            elif not speech and in_segment:
                # End of a segment
                if (i * 512) - (start_time * sr) >= min_samples:
                    segments.append({
                        "start": start_time,
                        "end": frame_time,
                        "text": ""  # We'll fill this later with mock text
                    })
                in_segment = False
        
        # Handle last segment
        if in_segment:
            frame_time = librosa.samples_to_time(len(is_speech) * 512, sr=sr)
            if (len(is_speech) * 512) - (start_time * sr) >= min_samples:
                segments.append({
                    "start": start_time,
                    "end": frame_time,
                    "text": ""
                })
        
        return segments
    
    def _cluster_speakers(self, features: np.ndarray, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assign speakers to segments using clustering"""
        # Extract features for each segment
        segment_features = []
        for segment in segments:
            start_idx = int(segment["start"] * 16000 / 512)  # Convert time to feature index
            end_idx = int(segment["end"] * 16000 / 512)
            if start_idx < end_idx and start_idx < features.shape[0] and end_idx <= features.shape[0]:
                segment_feat = np.mean(features[start_idx:end_idx], axis=0)
                segment_features.append(segment_feat)
            else:
                # Handle edge case with invalid indices
                segment_features.append(np.zeros(features.shape[1]))
        
        if len(segment_features) == 0:
            return segments
            
        # Perform clustering
        clustering = AgglomerativeClustering(
            n_clusters=min(self.config["num_speakers"], len(segment_features))
        ).fit(np.array(segment_features))
        
        # Assign speaker labels
        for i, segment in enumerate(segments):
            if i < len(clustering.labels_):
                segment["speaker"] = f"SPEAKER {clustering.labels_[i] + 1}"
            else:
                segment["speaker"] = "UNKNOWN SPEAKER"
        
        return segments
    
    def _generate_mock_transcript(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate mock transcript text for segments"""
        mock_texts = [
            "This is placeholder text for the lightweight version.",
            "Switch to the full Whisper model for actual transcription.",
            "This segment would contain the actual transcribed speech.",
            "The lightweight version only focuses on speaker diarization.",
            "Enable the Whisper model for complete transcription."
        ]
        
        for i, segment in enumerate(segments):
            segment["text"] = mock_texts[i % len(mock_texts)]
        
        return segments
    
    def process_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """Process audio file and return diarized segments"""
        # Ensure WAV format
        wav_path = self._ensure_wav_format(audio_path)
        
        # Load audio
        y, sr = librosa.load(wav_path, sr=16000)
        
        # Detect voice activity
        segments = self._detect_voice_activity(y, sr)
        
        if not segments:
            return []
        
        # Extract features for speaker clustering
        features = self._extract_features(wav_path)
        
        # Cluster speakers
        segments = self._cluster_speakers(features, segments)
        
        # Generate mock transcript (in lightweight version)
        segments = self._generate_mock_transcript(segments)
        
        return segments
