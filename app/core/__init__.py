from typing import Dict, Any, Optional
import os

from .diarizer import Diarizer
from .lightweight_diarizer import LightweightDiarizer
from .whisper_diarizer import WhisperDiarizer

def create_diarizer(diarizer_type: str = "lightweight", config: Optional[Dict[str, Any]] = None) -> Diarizer:
    """
    Factory function to create a diarizer instance
    
    Args:
        diarizer_type: Type of diarizer to create ('lightweight' or 'whisper')
        config: Configuration for the diarizer
        
    Returns:
        A diarizer instance
    """
    config = config or {}
    
    # Get diarizer type from environment if not specified
    if os.environ.get("DIARIZER_TYPE"):
        diarizer_type = os.environ.get("DIARIZER_TYPE")
    
    if diarizer_type.lower() == "whisper":
        return WhisperDiarizer(config)
    else:
        return LightweightDiarizer(config)
