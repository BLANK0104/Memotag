import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import tempfile
import json

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Import project modules
from src.tracking.longitudinal_tracker import LongitudinalTracker

logger = logging.getLogger("memotag_api.audio_processing")

def process_audio_file(
    audio_file: Union[str, Path],
    user_id: Optional[str] = None,
    assessment_type: str = "cognitive",
    save_to_db: bool = False
) -> Dict[str, Any]:
    """
    Process an audio file to extract cognitive markers
    
    Args:
        audio_file: Path to the audio file
        user_id: Optional user ID to associate with the assessment
        assessment_type: Type of assessment (cognitive, memory, etc.)
        save_to_db: Whether to save results to the database
        
    Returns:
        Dict containing extracted features and analysis results
    """
    audio_path = Path(audio_file)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    logger.info(f"Processing audio: {audio_path.name}")
    
    try:
        # Initialize tracker
        tracker = LongitudinalTracker()
        
        # Process audio file and extract features
        features = tracker.extract_speech_features(audio_path)
        
        # Perform cognitive assessment
        assessment_result = tracker.assess_cognitive_state(features)
        
        # Save to database if requested and user_id is provided
        assessment_id = None
        if save_to_db and user_id:
            assessment_id = tracker.save_assessment(
                user_id=user_id,
                features=features,
                assessment_type=assessment_type
            )
            logger.info(f"Assessment saved with ID: {assessment_id}")
        
        # Prepare response
        result = {
            "assessment_id": assessment_id,
            "features": {k: float(v) if isinstance(v, (int, float)) else v for k, v in features.items()},
            "cognitive_assessment": assessment_result,
        }
        
        # Add comparison to baseline if available
        if user_id:
            baseline = tracker.get_baseline(user_id)
            if baseline is not None and not baseline.empty:
                baseline_comparison = tracker.compare_to_baseline(features, baseline)
                result["baseline_comparison"] = baseline_comparison
        
        return result
        
    except Exception as e:
        logger.error(f"Error in audio processing: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to process audio: {str(e)}")
