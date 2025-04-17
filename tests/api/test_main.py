import sys
import os
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "online"

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_feature_importance():
    response = client.get("/api/features/importance")
    assert response.status_code == 200
    assert "features" in response.json()
    # Further tests depending on your feature importance file structure

@pytest.mark.skip(reason="Requires actual audio file and mocked LongitudinalTracker")
def test_process_audio():
    # Mock setup would go here in a real test
    
    test_file = Path(__file__).parent.parent / "resources" / "test_audio.wav"
    
    if not test_file.exists():
        pytest.skip("Test audio file not available")
    
    with open(test_file, "rb") as f:
        response = client.post(
            "/api/process-audio",
            files={"file": ("test_audio.wav", f, "audio/wav")},
            data={
                "user_id": "test_user",
                "assessment_type": "cognitive",
                "save_to_db": "false"
            }
        )
    
    assert response.status_code == 200
    assert "results" in response.json()
    # Additional assertions based on expected response structure
