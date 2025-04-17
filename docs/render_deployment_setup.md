# Render Deployment Configuration for CI/CD

This guide explains how to set up the required configuration for deploying your Memotag API to Render using GitHub Actions.

## Getting Your Render Service IDs

Each service in Render has a unique identifier. You need these IDs for your GitHub Actions workflow to deploy to the correct services.

1. **Log in to your Render account** at https://dashboard.render.com/

2. **Navigate to the service** you want to deploy to (e.g., your staging or production service)

3. **Check the URL in your browser address bar**. It should look something like:
   ```
   https://dashboard.render.com/web/srv-cjbcnq0rddl0l3q02mdg
   ```

4. **Extract the service ID** from the URL. In the example above, the service ID is:
   ```
   srv-cjbcnq0rddl0l3q02mdg
   ```

   > **Important**: For some Render services, you might need to use the service name instead of the service ID. If you see an "Unable to find the requested resource" error, try using the service name (e.g., `memotag-8lja` or `memotag-staging`) instead of the service ID.

## Getting Your Render API Key (REQUIRED)

The API key is **required** for CI/CD deployment. Without it, the deployment will fail with an error: "Input required and not supplied: api_key".

Follow these steps to generate and set up your Render API key:

1. **Go to your Render dashboard** at https://dashboard.render.com/

2. **Click on your account name** in the top-right corner

3. **Select "Account Settings"**

4. **Navigate to the "API Keys" section** in the left sidebar

5. **Generate a new API key** by clicking on the "Create API Key" button
   - Give it a name (e.g., "GitHub Actions")
   - Select the appropriate permissions (ensure it has deploy permissions)

6. **Copy the generated key immediately** (this is shown only once; if you lose it, you'll need to generate a new one)

7. **Add the API key to your GitHub repository secrets** as described below

## Setting Up GitHub Secrets

To securely use these values in your GitHub Actions workflow:

1. **Go to your GitHub repository** and navigate to its main page

2. **Click on "Settings"** (tab near the top of the page)

3. **Select "Secrets and variables" → "Actions"** from the left sidebar

4. **Click on "New repository secret"** button

5. **Add the following repository secrets** one by one:
   - Name: `RENDER_API_KEY`  
     Value: Your Render API key (copied in the previous section)
   
   - Name: `RENDER_STAGING_SERVICE_ID`  
     Value: Your staging service ID or name (e.g., `srv-cjbcnq0rddl0l3q02mdg` or `memotag-staging`)

   - Name: `RENDER_PRODUCTION_SERVICE_ID`  
     Value: Your production service ID or name (e.g., `srv-cjbcnuorddl0l3q02mgg` or `memotag-8lja`)

6. **Save each secret** by clicking the "Add secret" button

## Verifying Your API Key

To verify your Render API key is working correctly:

1. **Use curl to test the API** (make sure to replace YOUR_API_KEY with your actual key):
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.render.com/v1/services
   ```

2. **You should see a list of your services** in the response. This confirms your API key has the correct permissions.

3. **Check specific service access** (replace SERVICE_NAME with your service name):
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.render.com/v1/services/SERVICE_NAME
   ```
   
4. If you get a 404 error, try using the service ID format instead:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.render.com/v1/services/srv-xxxxxxxxxxxx
   ```

> **Note**: Since April 2025, Render has updated its API to better support both service names and service IDs. Make sure your API key has sufficient permissions for both deployments and service queries.

## Automatic Deployments

With these secrets set up, your GitHub Actions workflow will:

- Deploy to your staging environment when code is merged into the `develop` branch
- Deploy to your production environment when code is merged into the `main` branch

## Troubleshooting

### "Unable to find the requested resource" Error

If you encounter this error:

1. **Check if you're using the correct identifier** for your Render service:
   - Some Render API operations require the service name (e.g., `memotag-8lja`) instead of the service ID
   - Try updating your GitHub secret with the service name instead of the service ID

2. **Verify API key permissions**:
   - Ensure your API key has permission to access the specific service
   - If needed, generate a new API key with full permissions

3. **Confirm service existence**:
   - Double-check that the service exists in your Render account
   - Verify that you're looking at the correct team/account if you have access to multiple accounts

4. **Test the API manually**:
   You can test your API key and service ID with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.render.com/v1/services/YOUR_SERVICE_ID
   ```
   If this returns a 404 error, you're using an incorrect service ID or name.

### API Key Issues

If you encounter the error "Input required and not supplied: api_key":

1. **Check that you've added the RENDER_API_KEY secret** to your GitHub repository settings
2. **Verify that the secret name is exactly "RENDER_API_KEY"** (case-sensitive)
3. **Generate a new API key** on Render if necessary
4. **Update the GitHub secret** with the new API key

For other deployment issues:

1. **Check that your secrets are set correctly** in GitHub repository settings

2. **Verify the service IDs** match your Render services

3. **Ensure your API key has not expired** and has the necessary permissions

4. **Check your GitHub Actions logs** for detailed error messages

## Manual Deployment Alternative

If you're unable to set up CI/CD with GitHub Actions, you can deploy manually:

1. **Push your code changes** to your GitHub repository

2. **Log in to your Render dashboard**

3. **Navigate to your service**

4. **Click the "Manual Deploy" button** and select "Deploy latest commit"

This will trigger a new deployment of your application on Render.

## Current Configuration

The workflow has been configured with the following fallback values:

- **Staging**: `memotag-staging` (service name)
- **Production**: `memotag-8lja` (service name)

Update these values in the GitHub secrets or in the CI/CD workflow file if they don't match your actual service names.