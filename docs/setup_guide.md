# Memotag API: Setup, Testing and Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.9 or higher
- Git
- Docker (optional, for containerized development)

### Initial Setup

1. Clone the repository and navigate to the project directory
```bash
git clone [your-repository-url]
cd Memotag
```

2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Windows
copy .env.example .env
# Linux/Mac
cp .env.example .env
```

5. Edit the `.env` file with your configuration settings

## Running Locally

### Running directly with Uvicorn

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Running with Docker

1. Build the Docker image
```bash
docker build -t memotag-api .
```

2. Run the container
```bash
docker run -p 8000:8000 -v $(pwd)/data:/app/data memotag-api
```

## Testing

### Running Automated Tests

Run all tests:
```bash
pytest
```

Run specific test files:
```bash
pytest tests/api/test_main.py
```

### Manual Testing with Postman

1. Start the API server locally
2. Import the Postman collection from `docs/postman/memotag_collection.json` (if available) or create new requests as described in `docs/postman_testing.md`
3. Send requests to `http://localhost:8000/api/...`

### Testing Audio Processing

1. Use the `/api/process-audio` endpoint
2. Upload a sample audio file (WAV, MP3, or M4A format)
3. Check the response for feature extraction results

Example curl request:
```bash
curl -X POST http://localhost:8000/api/process-audio \
  -F "file=@/path/to/sample.wav" \
  -F "user_id=test_user_001" \
  -F "assessment_type=cognitive" \
  -F "save_to_db=false"
```

## Deployment

### AWS Elastic Beanstalk Deployment

1. Install the AWS EB CLI
```bash
pip install awsebcli
```

2. Initialize EB application
```bash
eb init -p python-3.9 memotag-api
```

3. Create an environment and deploy
```bash
eb create memotag-api-env
```

4. For subsequent deployments
```bash
eb deploy
```

### Google Cloud Platform Deployment

1. Install the Google Cloud SDK

2. Initialize gcloud
```bash
gcloud init
```

3. Deploy to App Engine
```bash
gcloud app deploy deployment/gcp/app.yaml
```

### Deploying with Docker to any Cloud Platform

1. Build the Docker image
```bash
docker build -t memotag-api .
```

2. Tag the image for your container registry
```bash
# For AWS ECR
docker tag memotag-api:latest [aws-account-id].dkr.ecr.[region].amazonaws.com/memotag-api:latest

# For Google Container Registry
docker tag memotag-api:latest gcr.io/[project-id]/memotag-api:latest
```

3. Push the image
```bash
# For AWS ECR
docker push [aws-account-id].dkr.ecr.[region].amazonaws.com/memotag-api:latest

# For Google Container Registry
docker push gcr.io/[project-id]/memotag-api:latest
```

4. Deploy the container using your cloud platform's container service (AWS ECS, GKE, etc.)

## Continuous Integration / Continuous Deployment

A sample GitHub Actions workflow is provided in `.github/workflows/ci-cd.yml` to:
1. Run tests on pull requests
2. Deploy to staging when merging to develop branch
3. Deploy to production when merging to main branch

## Monitoring

Once deployed, monitor the application using:
- AWS CloudWatch (for AWS deployments)
- Google Cloud Monitoring (for GCP deployments)
- Custom monitoring using the `/api/health` endpoint
