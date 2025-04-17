import sys
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uuid
import shutil
from pathlib import Path
import tempfile
import logging
from typing import Optional, List
import json

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Import project modules
from src.tracking.longitudinal_tracker import LongitudinalTracker
from src.api.audio_processing import process_audio_file
from src.data_processing.acoustic_analyzer import AcousticAnalyzer
from src.data_processing.feature_extractor import FeatureExtractor
from src.reports.report_generator import ReportGenerator
from src.models.unsupervised_analyzer import UnsupervisedAnalyzer

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

# Initialize components
tracker = LongitudinalTracker()
acoustic_analyzer = AcousticAnalyzer()
feature_extractor = FeatureExtractor()
report_generator = ReportGenerator()
unsupervised_analyzer = UnsupervisedAnalyzer()

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

@app.get("/api/user/history")
async def get_user_history(user_id: str):
    """
    Get assessment history for a specific user
    
    - **user_id**: User identifier
    """
    try:
        history = tracker.get_user_history(user_id)
        if not history:
            return JSONResponse(content={"message": f"No assessment history found for user {user_id}"}, status_code=404)
        
        return {"user_id": user_id, "assessments": history}
    except Exception as e:
        logger.error(f"Error retrieving user history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user history: {str(e)}")

@app.get("/api/user/trends")
async def get_user_trends(user_id: str):
    """
    Get longitudinal trends for a specific user
    
    - **user_id**: User identifier
    """
    try:
        trends = tracker.get_trend_data(user_id)
        if not trends:
            return JSONResponse(content={"message": f"No trend data found for user {user_id}"}, status_code=404)
        
        return {"user_id": user_id, "trends": trends}
    except Exception as e:
        logger.error(f"Error retrieving user trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user trends: {str(e)}")

@app.post("/api/extract/features")
async def extract_raw_features(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    feature_set: str = Form("all")
):
    """
    Extract raw features from audio without cognitive assessment
    
    - **file**: Audio file (wav, mp3, m4a)
    - **feature_set**: Type of features to extract (all, acoustic, linguistic, cognitive)
    """
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
        
        # Extract features based on feature_set parameter
        if feature_set == "acoustic":
            features = acoustic_analyzer.extract_acoustic_features(temp_audio_path)
        elif feature_set == "linguistic":
            features = feature_extractor.extract_linguistic_features(temp_audio_path)
        elif feature_set == "cognitive":
            features = feature_extractor.extract_cognitive_features(temp_audio_path)
        else:  # "all"
            features = feature_extractor.extract_all_features(temp_audio_path)
        
        # Clean up files in the background after response is sent
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        
        return JSONResponse(content={
            "request_id": request_id,
            "filename": file.filename,
            "feature_set": feature_set,
            "features": features
        })
        
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}", exc_info=True)
        # Clean up on error
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error extracting features: {str(e)}")

@app.post("/api/analyze/task")
async def analyze_cognitive_task(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    task_type: str = Form("counting"),
):
    """
    Analyze specific cognitive task performance
    
    - **file**: Audio file (wav, mp3, m4a)
    - **task_type**: Type of cognitive task (counting, animal_naming, paragraph_recall, word_list)
    """
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
            
        # Process specific cognitive task
        task_results = feature_extractor.analyze_specific_task(temp_audio_path, task_type)
        
        # Clean up files in the background after response is sent
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        
        return JSONResponse(content={
            "request_id": request_id,
            "filename": file.filename,
            "task_type": task_type,
            "results": task_results
        })
        
    except Exception as e:
        logger.error(f"Error analyzing cognitive task: {str(e)}", exc_info=True)
        # Clean up on error
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing cognitive task: {str(e)}")

@app.get("/api/report/{assessment_id}")
async def get_assessment_report(assessment_id: str, format: str = "json"):
    """
    Get a detailed report for a specific assessment
    
    - **assessment_id**: Assessment identifier
    - **format**: Report format (json, html, pdf)
    """
    try:
        if format == "html":
            report_path = report_generator.generate_html_report(assessment_id)
            if not report_path or not os.path.exists(report_path):
                raise HTTPException(status_code=404, detail=f"Report not found for assessment {assessment_id}")
                
            return FileResponse(report_path, media_type="text/html")
        elif format == "pdf":
            report_path = report_generator.generate_pdf_report(assessment_id)
            if not report_path or not os.path.exists(report_path):
                raise HTTPException(status_code=404, detail=f"Report not found for assessment {assessment_id}")
                
            return FileResponse(report_path, media_type="application/pdf")
        else:  # json
            report_data = report_generator.generate_json_report(assessment_id)
            if not report_data:
                raise HTTPException(status_code=404, detail=f"Report not found for assessment {assessment_id}")
                
            return JSONResponse(content=report_data)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/api/features/distribution")
async def get_feature_distribution(feature_name: str = Query(..., description="Name of the feature to get distribution for")):
    """
    Get statistical distribution for a specific feature
    
    - **feature_name**: Name of the feature (e.g., speech_rate_wpm, pause_count)
    """
    try:
        import pandas as pd
        import numpy as np
        
        # Load feature data
        features_path = Path(__file__).parents[2] / "data" / "processed" / "extracted_features.csv"
        
        if not features_path.exists():
            return JSONResponse(content={
                "error": "Feature data not found"
            }, status_code=404)
            
        df = pd.read_csv(features_path)
        
        if feature_name not in df.columns:
            return JSONResponse(content={
                "error": f"Feature {feature_name} not found"
            }, status_code=404)
            
        # Calculate distribution statistics
        feature_data = df[feature_name].dropna()
        distribution = {
            "feature": feature_name,
            "count": len(feature_data),
            "mean": float(feature_data.mean()),
            "median": float(feature_data.median()),
            "std": float(feature_data.std()),
            "min": float(feature_data.min()),
            "max": float(feature_data.max()),
            "percentiles": {
                "25": float(feature_data.quantile(0.25)),
                "50": float(feature_data.quantile(0.50)),
                "75": float(feature_data.quantile(0.75)),
                "90": float(feature_data.quantile(0.90)),
                "95": float(feature_data.quantile(0.95))
            }
        }
        
        return distribution
        
    except Exception as e:
        logger.error(f"Error retrieving feature distribution: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving feature distribution")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
