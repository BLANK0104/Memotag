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

## API Base URLs

- **Local Development**: http://localhost:8000
- **Production**: https://api.memotag-service.com
- **Staging**: https://staging-api.memotag-service.com
- **Render Deployment**: https://memotag-8lja.onrender.com

## Deployment

### Render Deployment

1. Create a Render account at https://render.com if you don't have one

2. Create a new Web Service
   - Connect your GitHub repository
   - Select the branch you want to deploy
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `gunicorn src.api.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - Choose the appropriate instance type

3. Set Environment Variables
   - Add all required environment variables from your `.env` file

4. Deploy
   - Render will automatically deploy your application
   - For subsequent deployments, simply push to your selected branch

### Deploying with Docker to Render

1. Create a Render account at https://render.com if you don't have one

2. Create a new Web Service
   - Connect your GitHub repository
   - Select "Deploy from Dockerfile" option
   - Select the branch you want to deploy
   - Set environment variables as needed

3. Deploy
   - Render will automatically build and deploy your Docker container
   - For subsequent deployments, simply push to your selected branch

## Continuous Integration / Continuous Deployment

A GitHub Actions workflow is provided in `.github/workflows/ci-cd.yml` to:
1. Run tests on pull requests
2. Deploy to Render staging when merging to develop branch
3. Deploy to Render production when merging to main branch

## Monitoring

Once deployed, monitor the application using:
- Render Dashboard for logs and metrics
- Custom monitoring using the `/api/health` endpoint
- Set up Render health checks to ensure your application is responsive

## Testing Your Render Deployment

After deploying to Render, test your API:

1. **Test the Health Check Endpoint**:
   ```bash
   curl https://memotag-8lja.onrender.com/api/health
   ```

2. **Test the Process Audio Endpoint**:
   ```bash
   curl -X POST https://memotag-8lja.onrender.com/api/process-audio \
     -F "file=@/path/to/sample.wav" \
     -F "user_id=test_user_001" \
     -F "assessment_type=cognitive" \
     -F "save_to_db=false"
   ```

3. **Test Feature Importance Endpoint**:
   ```bash
   curl https://memotag-8lja.onrender.com/api/features/importance
   ```
