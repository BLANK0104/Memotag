# Manual Render Deployment Guide

This guide provides steps for manually identifying your Render service details and deploying your application when CI/CD automation encounters errors.

## Finding Your Exact Render Service Name/ID

When encountering the "Unable to find the requested resource" error, you need to identify the exact service identifier that Render recognizes.

### Method 1: Using the Render Dashboard

1. **Log in to your Render account** at https://dashboard.render.com/
2. **Navigate to your service** (the one you're trying to deploy to)
3. **Copy the URL from your browser's address bar**. It will look like:
   ```
   https://dashboard.render.com/web/srv-abc123xyz
   ```
4. The service ID is the part after `/web/` (e.g., `srv-abc123xyz`)

### Method 2: Using the Render API (with your API key)

Use the following curl command to list all services your API key has access to:

```bash
curl -H "Authorization: Bearer rnd_hxUoFkuzJdJ5z7nFwoTAHtVbvjwK" https://api.render.com/v1/services
```

This will return a JSON response containing all your services with their IDs and names.

## Manual Deployment

Once you know your exact service identifier, you can manually trigger a deployment:

```bash
curl -X POST \
  -H "Authorization: Bearer rnd_hxUoFkuzJdJ5z7nFwoTAHtVbvjwK" \
  -H "Content-Type: application/json" \
  https://api.render.com/v1/services/YOUR_SERVICE_ID_OR_NAME/deploys
```

Replace `YOUR_SERVICE_ID_OR_NAME` with the service identifier from the methods above.

## Troubleshooting Common Deployment Issues

### "Unable to find the requested resource" Error

This typically means one of the following:

1. **Wrong service identifier**: The service name or ID you're using doesn't match what Render expects
2. **Permission issue**: Your API key doesn't have access to the specified service
3. **Service doesn't exist**: The service may have been deleted or renamed
4. **API format mismatch**: Some Render API operations expect the ID format (srv-xxx) while others accept the name

### Common Solutions:

1. **Try both formats**: If using the name (e.g., `memotag-8lja`) doesn't work, try the ID format (`srv-abc123`)
2. **Check which owner/team**: Your service might be under a different team or personal account than the API key
3. **Verify API key permissions**: Generate a new API key with full permissions if necessary
4. **Check service status**: Ensure your service exists and is active on Render

## GitHub Actions Workflow

The updated GitHub Actions workflow in your repository performs the following steps:

1. **Lists all services** your API key has access to
2. **Attempts to deploy** using your service name
3. **Tries an alternative format** if the first attempt fails
4. **Outputs detailed error information** to help identify the issue

To run this workflow, simply push commits to your main branch. The workflow logs will show all available services, helping you identify the correct service identifier to use.

## Important Notes

- **Keep your API key secure**: Don't share your API key publicly
- **Check GitHub Secrets**: Ensure your `RENDER_API_KEY` is correctly set in GitHub repository secrets
- **Service naming**: Render service identifiers are case-sensitive