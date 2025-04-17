# Manual Render Deployment Guide

This guide provides steps for manually identifying your Render service details and deploying your application when CI/CD automation encounters errors.

## Finding Your Exact Render Service Name/ID

The deployment errors indicate that neither "memotag-8lja" nor "srv-memotag-8lja" are recognized as valid service identifiers by the Render API. You need to identify the exact service identifier that Render recognizes.

### Method 1: Using the Render Dashboard (Most Reliable)

1. **Log in to your Render account** at https://dashboard.render.com/
2. **Navigate to your service** (the one with URL https://memotag-8lja.onrender.com)
3. **Look at the URL in your browser's address bar**. It will look something like:
   ```
   https://dashboard.render.com/web/srv-abc123xyz
   ```
4. The service ID is the part after `/web/` (e.g., `srv-abc123xyz`)
5. **Copy this exact ID** for use in deployment commands

### Method 2: List All Your Services Using the Render API

Use the following curl command to list all services your API key has access to:

```bash
curl -H "Authorization: Bearer rnd_hxUoFkuzJdJ5z7nFwoTAHtVbvjwK" https://api.render.com/v1/services
```

This will return a JSON response containing all your services with their IDs and names. Look for the service with name that matches your deployment or with URL "memotag-8lja.onrender.com".

## Manual Deployment

Once you know your exact service identifier, you can manually trigger a deployment:

```bash
curl -X POST \
  -H "Authorization: Bearer rnd_hxUoFkuzJdJ5z7nFwoTAHtVbvjwK" \
  -H "Content-Type: application/json" \
  https://api.render.com/v1/services/YOUR_EXACT_SERVICE_ID/deploys
```

Replace `YOUR_EXACT_SERVICE_ID` with the service identifier from the methods above (likely something like `srv-abc123xyz`, not "memotag-8lja").

## Common Reasons for "Not Found" Errors

Based on your deployment errors, here are the most likely causes:

1. **Incorrect Service Identifier Format**: 
   - The service name "memotag-8lja" is likely the subdomain of your deployed site but not the actual service identifier
   - The actual service ID should be in the format `srv-xxxxxxxxx`

2. **Service in Different Team/Account**: 
   - Your API key might be from a different Render account or team than where the service is created
   - Check that you're logged into the correct account that owns the service

3. **Service Name vs. Service ID Confusion**: 
   - Render has both internal service IDs (`srv-xxxxx`) and service names (which may be different from the URL subdomain)
   - You need to use the internal service ID for API operations

## Updating Your CI/CD Workflow

Once you have identified the correct service ID, update your GitHub workflow file:

1. Open `.github/workflows/ci-cd.yml`
2. Replace both instances of `memotag-8lja` with your correct service ID
3. Commit and push the changes

## Important Commands for Troubleshooting

### Get Your Service IDs

```bash
curl -H "Authorization: Bearer rnd_hxUoFkuzJdJ5z7nFwoTAHtVbvjwK" https://api.render.com/v1/services | grep -o '"id":"[^"]*"'
```

### Get Your Service Names

```bash
curl -H "Authorization: Bearer rnd_hxUoFkuzJdJ5z7nFwoTAHtVbvjwK" https://api.render.com/v1/services | grep -o '"name":"[^"]*"'
```

### Check Specific Service

```bash
curl -H "Authorization: Bearer rnd_hxUoFkuzJdJ5z7nFwoTAHtVbvjwK" https://api.render.com/v1/services/YOUR_EXACT_SERVICE_ID
```