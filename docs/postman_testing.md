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

### 4. Get User Assessment History

Retrieve assessment history for a specific user.

- **URL**: `{base_url}/api/user/history`
- **Method**: GET
- **Query Parameters**:
  - `user_id`: User identifier (string) [Required]
- **Example Response**:
  ```json
  {
    "user_id": "test_user_001",
    "assessments": [
      {
        "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2025-04-15T15:30:45",
        "assessment_type": "cognitive",
        "overall_score": 85,
        "risk_level": "low"
      },
      {
        "assessment_id": "662f9500-f39b-51e4-b826-557766550111",
        "timestamp": "2025-04-10T11:20:15",
        "assessment_type": "cognitive",
        "overall_score": 82,
        "risk_level": "low"
      }
    ]
  }
  ```

### 5. Get User Trends

Retrieve longitudinal trends for a specific user.

- **URL**: `{base_url}/api/user/trends`
- **Method**: GET
- **Query Parameters**:
  - `user_id`: User identifier (string) [Required]
- **Example Response**:
  ```json
  {
    "user_id": "test_user_001",
    "trends": {
      "speech_rate_wpm": [
        {"date": "2025-04-01", "value": 152.3},
        {"date": "2025-04-08", "value": 155.1},
        {"date": "2025-04-15", "value": 156.3}
      ],
      "hesitation_ratio": [
        {"date": "2025-04-01", "value": 0.092},
        {"date": "2025-04-08", "value": 0.090},
        {"date": "2025-04-15", "value": 0.089}
      ],
      "overall_score": [
        {"date": "2025-04-01", "value": 81},
        {"date": "2025-04-08", "value": 83},
        {"date": "2025-04-15", "value": 85}
      ]
    }
  }
  ```

### 6. Extract Raw Features

Extract raw features from audio without full cognitive assessment.

- **URL**: `{base_url}/api/extract/features`
- **Method**: POST
- **Body**: Form-data
  - `file`: Audio file (wav, mp3, m4a) [Required]
  - `feature_set`: Type of features to extract (string) [Default: "all"]
    - Options: "all", "acoustic", "linguistic", "cognitive"
- **Headers**:
  - Content-Type: multipart/form-data
- **Example Response**:
  ```json
  {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "speech_sample.wav",
    "feature_set": "all",
    "features": {
      "acoustic": {
        "speech_rate_wpm": 156.3,
        "pause_count": 12,
        "pause_duration_avg": 0.45,
        "pitch_mean": 185.23,
        "pitch_std": 25.67,
        "intensity_mean": 65.8,
        "voice_quality": 0.87
      },
      "linguistic": {
        "transcript_length": 224,
        "unique_words": 92,
        "lexical_diversity": 0.41,
        "hesitation_count": 5,
        "hesitation_ratio": 0.089
      },
      "cognitive": {
        "counting_sequence_length": 17,
        "counting_errors": 1,
        "animal_count": 12,
        "word_finding_difficulty_count": 3
      }
    }
  }
  ```

### 7. Analyze Cognitive Task

Analyze specific cognitive task performance.

- **URL**: `{base_url}/api/analyze/task`
- **Method**: POST
- **Body**: Form-data
  - `file`: Audio file (wav, mp3, m4a) [Required]
  - `task_type`: Type of cognitive task (string) [Default: "counting"]
    - Options: "counting", "animal_naming", "paragraph_recall", "word_list"
- **Headers**:
  - Content-Type: multipart/form-data
- **Example Response**:
  ```json
  {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "speech_sample.wav",
    "task_type": "counting",
    "results": {
      "transcript": "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17",
      "counting_sequence_length": 17,
      "counting_errors": 0,
      "counting_speed": 2.1,
      "performance_percentile": 92,
      "score": 95
    }
  }
  ```

### 8. Get Assessment Report

Get a detailed report for a specific assessment.

- **URL**: `{base_url}/api/report/{assessment_id}`
- **Method**: GET
- **Path Parameters**:
  - `assessment_id`: Assessment identifier (string) [Required]
- **Query Parameters**:
  - `format`: Report format (string) [Default: "json"]
    - Options: "json", "html", "pdf"
- **Example Response** (for JSON format):
  ```json
  {
    "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "test_user_123",
    "timestamp": "2025-04-15T15:30:45",
    "assessment_type": "cognitive",
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
    },
    "recommendations": [
      "Continue regular cognitive activities",
      "Practice verbal fluency exercises"
    ]
  }
  ```

### 9. Get Feature Distribution

Get statistical distribution for a specific feature.

- **URL**: `{base_url}/api/features/distribution`
- **Method**: GET
- **Query Parameters**:
  - `feature_name`: Name of the feature (string) [Required]
    - Examples: "speech_rate_wpm", "pause_count", "hesitation_ratio"
- **Example Response**:
  ```json
  {
    "feature": "speech_rate_wpm",
    "count": 250,
    "mean": 152.7,
    "median": 155.0,
    "std": 22.4,
    "min": 87.3,
    "max": 210.5,
    "percentiles": {
      "25": 135.8,
      "50": 155.0,
      "75": 168.3,
      "90": 183.6,
      "95": 190.2
    }
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

## Features Analyzed

The API analyzes the following speech features:

- **transcript_length**: Total number of words spoken
- **hesitation_count**: Number of hesitation markers (um, uh, etc.)
- **hesitation_ratio**: Ratio of hesitations to total words
- **pause_count**: Number of detected pauses
- **pause_rate**: Pauses per sentence
- **speech_rate_wpm**: Speaking rate in words per minute
- **counting_sequence_length**: Length of numeric sequences in speech
- **counting_errors**: Errors in counting sequences
- **animal_count**: Number of unique animals named
- **word_finding_difficulty_count**: Estimated instances of word-finding difficulties
- **pitch_mean**: Mean fundamental frequency
- **pitch_std**: Standard deviation of fundamental frequency
- **intensity_mean**: Mean speech intensity
- **voice_quality**: Measure of voice clarity and steadiness
- **lexical_diversity**: Ratio of unique words to total words

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
- **Render Deployment**: https://memotag-8lja.onrender.com

## Testing Your Render Deployment

Now that you've deployed the Memotag API on Render and confirmed it's running (by seeing the `{"message":"Speech Analyzer API is running"}` message), follow these steps to fully test the deployment:

1. **Test the Health Check Endpoint**:
   - Open Postman and create a new GET request
   - Enter the URL: `https://memotag-8lja.onrender.com/api/health`
   - Click "Send" and verify you receive a 200 response with `{"status":"healthy"}`

2. **Test the Audio Processing Endpoint**:
   - Create a new POST request
   - Enter the URL: `https://memotag-8lja.onrender.com/api/process-audio`
   - In the "Body" tab, select "form-data"
   - Add the key-value pairs as described in the Testing Steps section
   - Upload a test audio file and click "Send"
   - Verify you receive a successful response with assessment results

3. **Test Feature Importance Endpoint**:
   - Create a new GET request
   - Enter the URL: `https://memotag-8lja.onrender.com/api/features/importance`
   - Click "Send" and verify you receive the feature importance data

4. **Test User History Endpoint**:
   - Create a new GET request
   - Enter the URL: `https://memotag-8lja.onrender.com/api/user/history?user_id=test_user_001`
   - Click "Send" and verify you receive the user's assessment history

5. **Test Feature Extraction Endpoint**:
   - Create a new POST request
   - Enter the URL: `https://memotag-8lja.onrender.com/api/extract/features`
   - In the "Body" tab, select "form-data"
   - Add key-value pairs:
     - Key: `file`, Value: Select a test audio file
     - Key: `feature_set`, Value: "all" (or "acoustic", "linguistic", "cognitive")
   - Click "Send" and verify you receive the extracted features

If any tests fail, review the Troubleshooting section for common issues and solutions.

## Example Postman Collection

A Postman collection with all these endpoints pre-configured is available in the `docs/postman/memotag_collection.json` file. Import this collection into Postman for easier testing.

## Working with the API

### Setting Up a Testing Environment

1. Create an environment in Postman with variables:
   - `base_url`: Set to your preferred deployment URL (e.g., `http://localhost:8000` or `https://memotag-8lja.onrender.com`)
   - `test_user_id`: Set to a test user ID (e.g., `test_user_001`)
   - `assessment_id`: Leave empty initially, will be populated during testing

2. Use these environment variables in your requests for easier switching between environments.

### Workflow Testing

To test a complete workflow:

1. Process an audio file with `/api/process-audio`
2. Extract the `assessment_id` from the response and set it as the environment variable
3. Get the detailed report with `/api/report/{assessment_id}`
4. View the user's history with `/api/user/history?user_id={user_id}`
5. Check the user's trends with `/api/user/trends?user_id={user_id}`
