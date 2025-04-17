# Testing Memotag API with Postman

This document provides instructions for testing the Memotag API endpoints using Postman.

## Setup

1. Download and install [Postman](https://www.postman.com/downloads/)
2. Import the Memotag collection from `docs/postman/memotag_collection.json` (if available)

## API Endpoints

### 1. Health Check

Verify if the API is running properly.

- **URL**: `{base_url}/api/health`
- **Method**: GET
- **Expected Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

### 2. Process Audio File

Upload and process an audio file for cognitive assessment.

- **URL**: `{base_url}/api/process-audio`
- **Method**: POST
- **Body**: Form-data
  - `file`: Audio file (wav, mp3, m4a) [Required]
  - `user_id`: User identifier (string) [Optional]
  - `assessment_type`: Assessment type (string) [Default: "cognitive"]
  - `save_to_db`: Whether to save to database (boolean) [Default: false]
- **Headers**:
  - Content-Type: multipart/form-data
- **Example Response**:
  ```json
  {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "test_user_123",
    "filename": "speech_sample.wav",
    "results": {
      "assessment_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
      "features": {
        "speech_rate_wpm": 156.3,
        "pause_count": 12,
        "hesitation_ratio": 0.089,
        "transcript_length": 224,
        "counting_sequence_length": 17,
        "word_finding_difficulty_count": 3
      },
      "cognitive_assessment": {
        "overall_score": 85,
        "fluency_score": 82,
        "memory_score": 87,
        "attention_score": 85,
        "risk_level": "low"
      }
    }
  }
  ```

### 3. Get Feature Importance

Retrieve the importance ranking of different speech features.

- **URL**: `{base_url}/api/features/importance`
- **Method**: GET
- **Expected Response**:
  ```json
  {
    "features": [
      {
        "Feature": "counting_sequence_length",
        "Importance": 1.0
      },
      {
        "Feature": "transcript_length",
        "Importance": 0.9607139179489091
      },
      ...
    ]
  }
  ```

## Testing Steps

### Testing the Audio Processing Endpoint

1. Open Postman and create a new request
2. Set the request type to POST
3. Enter the URL: `{base_url}/api/process-audio`
4. Go to the "Body" tab and select "form-data"
5. Add the following key-value pairs:
   - Key: `file`, Value: Select a test audio file (wav, mp3)
   - Key: `user_id`, Value: Enter test user ID (e.g., "test_user_001")
   - Key: `assessment_type`, Value: "cognitive"
   - Key: `save_to_db`, Value: Select "true" or "false"
6. Click "Send" to submit the request
7. Verify the response contains the expected fields

## Troubleshooting

If you encounter errors:

1. Check the API logs for detailed error messages
2. Verify the audio file format is supported
3. Ensure the file size does not exceed the maximum allowed size
4. Confirm that the server is running and accessible

## API Base URLs

- **Local Development**: http://localhost:8000
- **Production**: https://api.memotag-service.com
- **Staging**: https://staging-api.memotag-service.com
