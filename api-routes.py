from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..core import create_diarizer

router = APIRouter()

# Create upload and results directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

@router.post("/upload")
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    num_speakers: int = Form(2),
    diarizer_type: str = Form("lightweight")
):
    """
    Upload an audio file for diarization
    """
    # Generate unique ID for this job
    job_id = str(uuid.uuid4())
    
    # Save the uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    file_path = f"uploads/{job_id}{file_extension}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Schedule processing in background
    background_tasks.add_task(
        process_audio, 
        file_path=file_path, 
        job_id=job_id,
        config={"num_speakers": num_speakers},
        diarizer_type=diarizer_type
    )
    
    return {"job_id": job_id, "status": "processing"}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """
    Get the status of a diarization job
    """
    result_path = f"results/{job_id}.json"
    
    if os.path.exists(result_path):
        with open(result_path, "r") as f:
            result = json.load(f)
        return result
    else:
        return {"status": "processing"}

@router.get("/transcript/{job_id}")
async def get_transcript(job_id: str):
    """
    Get the transcript file for a completed job
    """
    transcript_path = f"results/{job_id}.txt"
    
    if os.path.exists(transcript_path):
        return FileResponse(
            transcript_path,
            media_type="text/plain",
            filename=f"transcript_{job_id}.txt"
        )
    else:
        raise HTTPException(status_code=404, detail="Transcript not found")

@router.get("/config")
async def get_config():
    """
    Get the current diarizer configuration
    """
    diarizer_type = os.environ.get("DIARIZER_TYPE", "lightweight")
    return {"diarizer_type": diarizer_type}

def process_audio(file_path: str, job_id: str, config: Dict[str, Any], diarizer_type: str):
    """
    Process an audio file using the selected diarizer
    """
    try:
        # Create diarizer
        diarizer = create_diarizer(diarizer_type, config)
        
        # Process audio
        segments = diarizer.process_audio(file_path)
        
        # Save transcript
        transcript_path = f"results/{job_id}.txt"
        diarizer.save_transcript(segments, transcript_path)
        
        # Save results as JSON
        result = {
            "status": "completed",
            "job_id": job_id,
            "segments": segments,
            "timestamp": datetime.now().isoformat(),
            "diarizer_type": diarizer_type
        }
        
        with open(f"results/{job_id}.json", "w") as f:
            json.dump(result, f, default=str)
            
    except Exception as e:
        # Save error
        error_result = {
            "status": "error",
            "job_id": job_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(f"results/{job_id}.json", "w") as f:
            json.dump(error_result, f, default=str)
