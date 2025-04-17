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

## Getting Your Render API Key

To enable GitHub Actions to authenticate with Render, you need an API key:

1. **Go to your Render dashboard**

2. **Click on your account name** in the top-right corner

3. **Select "Account Settings"**

4. **Navigate to the "API Keys" section**

5. **Generate a new API key** by clicking on the "Create API Key" button

6. **Copy the generated key** (this is shown only once; if you lose it, you'll need to generate a new one)

## Setting Up GitHub Secrets

To securely use these values in your GitHub Actions workflow:

1. **Go to your GitHub repository**

2. **Click on "Settings"**

3. **Select "Secrets and variables" → "Actions"** from the sidebar

4. **Add the following repository secrets**:
   - `RENDER_API_KEY`: Your Render API key
   - `RENDER_STAGING_SERVICE_ID`: Your staging service ID
   - `RENDER_PRODUCTION_SERVICE_ID`: Your production service ID

## Automatic Deployments

With these secrets set up, your GitHub Actions workflow will:

- Deploy to your staging environment when code is merged into the `develop` branch
- Deploy to your production environment when code is merged into the `main` branch

## Troubleshooting

If you encounter deployment errors:

1. **Check that your secrets are set correctly** in GitHub repository settings

2. **Verify the service IDs** match your Render services

3. **Ensure your API key has not expired** and has the necessary permissions

4. **Check your GitHub Actions logs** for detailed error messages

## Fallback Service IDs

The workflow includes fallback service IDs in case the secrets are not configured. Replace these with your actual service IDs if you prefer not to use GitHub secrets:

```yaml
service_id: ${{ secrets.RENDER_STAGING_SERVICE_ID || 'srv-cjbcnq0rddl0l3q02mdg' }}
```

```yaml
service_id: ${{ secrets.RENDER_PRODUCTION_SERVICE_ID || 'srv-cjbcnuorddl0l3q02mgg' }}
```