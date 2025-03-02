from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import os
import datetime

class Diarizer(ABC):
    """
    Base abstract class for audio diarization implementations.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
    @abstractmethod
    def process_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Process an audio file and return diarized segments
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of segment dictionaries with:
                - start: start time in seconds
                - end: end time in seconds
                - text: transcribed text
                - speaker: speaker identifier
        """
        pass
    
    def format_time(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS format"""
        return str(datetime.timedelta(seconds=round(seconds)))
    
    def save_transcript(self, segments: List[Dict[str, Any]], output_path: str) -> str:
        """
        Save the diarized transcript to a file
        
        Args:
            segments: List of diarized segments
            output_path: Path to save the transcript
            
        Returns:
            The path to the saved transcript
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments):
                if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
                    f.write(f"\n{segment['speaker']} [{self.format_time(segment['start'])}]\n")
                f.write(segment["text"].strip() + " ")
        
        return output_path
