import sys
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import shutil
from pathlib import Path
import tempfile
import logging
from typing import Optional

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Import project modules
from src.tracking.longitudinal_tracker import LongitudinalTracker
from src.api.audio_processing import process_audio_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("memotag_api")

app = FastAPI(
    title="Memotag API",
    description="API for processing speech audio files to detect cognitive markers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Root endpoint to check API status"""
    return {"status": "online", "message": "Memotag API is running"}

@app.post("/api/process-audio")
async def process_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    assessment_type: str = Form("cognitive"),
    save_to_db: bool = Form(False)
):
    """
    Process an audio file and extract cognitive markers
    
    - **file**: Audio file (wav, mp3, m4a)
    - **user_id**: Optional user ID to associate with the assessment
    - **assessment_type**: Type of assessment (cognitive, memory, etc.)
    - **save_to_db**: Whether to save results to the database
    """
    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())
    temp_dir = Path(tempfile.gettempdir()) / "memotag" / request_id
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.wav', '.mp3', '.m4a']:
            raise HTTPException(status_code=400, detail="Audio file must be .wav, .mp3, or .m4a format")
            
        # Save uploaded file temporarily
        temp_audio_path = temp_dir / file.filename
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing file: {file.filename} (User ID: {user_id or 'anonymous'})")
        
        # Process the audio file
        results = process_audio_file(
            audio_file=temp_audio_path,
            user_id=user_id,
            assessment_type=assessment_type,
            save_to_db=save_to_db
        )
        
        # Clean up files in the background after response is sent
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        
        return JSONResponse(content={
            "request_id": request_id,
            "user_id": user_id or "anonymous",
            "filename": file.filename,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        # Clean up on error
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.get("/api/features/importance")
async def get_feature_importance():
    """Get the importance ranking of different speech features"""
    try:
        import pandas as pd
        feature_importance_path = Path(__file__).parents[2] / "reports" / "feature_importance.csv"
        
        if not feature_importance_path.exists():
            return JSONResponse(content={
                "error": "Feature importance data not found"
            }, status_code=404)
            
        df = pd.read_csv(feature_importance_path)
        features = df.to_dict(orient="records")
        
        return {"features": features}
        
    except Exception as e:
        logger.error(f"Error retrieving feature importance: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving feature data")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
