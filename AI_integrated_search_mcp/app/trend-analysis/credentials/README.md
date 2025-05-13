# Google BigQuery Credentials

## Important: Adding Service Account Credentials

To use the Trend Analysis service with BigQuery, you need to add your Google Cloud Platform service account credentials here.

1. Create a service account in Google Cloud Platform with access to BigQuery
2. Download the JSON key file for this service account
3. Rename the file to `google-service-account.json` and place it in this directory

The file structure should be:
```
AI_integrated_search_mcp/app/trend-analysis/credentials/google-service-account.json
```

## Environment Configuration

The service reads the path to this file from the environment variable `GOOGLE_APPLICATION_CREDENTIALS`. 
This variable is already configured in the `.env` file and passed to the container through Docker/Podman Compose.

## Note on Security

- Never commit actual credentials to version control
- Make sure the file has appropriate permissions (readable only by the service)
- Consider using a secret management solution for production environments
