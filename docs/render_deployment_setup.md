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
     Value: Your staging service ID

   - Name: `RENDER_PRODUCTION_SERVICE_ID`  
     Value: Your production service ID

6. **Save each secret** by clicking the "Add secret" button

## Automatic Deployments

With these secrets set up, your GitHub Actions workflow will:

- Deploy to your staging environment when code is merged into the `develop` branch
- Deploy to your production environment when code is merged into the `main` branch

## Troubleshooting

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

## Fallback Service IDs

The workflow includes fallback service IDs in case the secrets are not configured. Replace these with your actual service IDs if you prefer not to use GitHub secrets:

```yaml
service_id: ${{ secrets.RENDER_STAGING_SERVICE_ID || 'srv-cjbcnq0rddl0l3q02mdg' }}
```

```yaml
service_id: ${{ secrets.RENDER_PRODUCTION_SERVICE_ID || 'srv-cjbcnuorddl0l3q02mgg' }}
```

However, there is **no fallback for the API key** as it must be kept secure and cannot be stored in the workflow file.