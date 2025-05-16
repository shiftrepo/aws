# OpenAPI Specifications for AI_integrated_search_mcp

This directory contains OpenAPI 3.1.0 specifications for the AI_integrated_search_mcp services that can be used to integrate with Dify.

## Available Specifications

1. **Database API** (`database-api-spec.json`) - For executing SQL queries and accessing database schema
2. **Natural Language Query API** (`nl-query-api-spec.json`) - For processing natural language queries using AWS Bedrock
3. **Trend Analysis API** (`trend-analysis-api-spec.json`) - For patent trend analysis and report generation

## How to Use with Dify

### Database API Integration

1. In your Dify dashboard, go to "Model Provider" > "Tool Provider" > "Add Custom Tool Provider"
2. Enter a name (e.g., "SQLite Database API")
3. Upload or paste the contents of `database-api-spec.json`
4. Configure the authentication if needed (no authentication by default)
5. Save the provider

Example configuration:

```json
{
  "name": "SQLite Database API",
  "description": "API for interacting with SQLite databases containing patent data",
  "base_url": "http://localhost:5003",
  "auth": {
    "type": "none"
  },
  "tools": [
    {
      "name": "executeQuery",
      "description": "Execute an SQL query on the specified database"
    },
    {
      "name": "getSchema",
      "description": "Get the database schema for the specified database"
    },
    {
      "name": "getSampleQueries",
      "description": "Get sample SQL queries for the specified database"
    },
    {
      "name": "listDatabases",
      "description": "List all available databases"
    }
  ]
}
```

### Natural Language Query API Integration

1. In your Dify dashboard, go to "Model Provider" > "Tool Provider" > "Add Custom Tool Provider"
2. Enter a name (e.g., "NL Query API")
3. Upload or paste the contents of `nl-query-api-spec.json`
4. Configure the authentication if needed (no authentication by default)
5. Save the provider

Example configuration:

```json
{
  "name": "Natural Language Query API",
  "description": "API for processing natural language queries using AWS Bedrock models",
  "base_url": "http://localhost:5004",
  "auth": {
    "type": "none"
  },
  "tools": [
    {
      "name": "processNaturalLanguageQuery",
      "description": "Process a natural language query and convert it to SQL"
    }
  ]
}
```

### Trend Analysis API Integration

1. In your Dify dashboard, go to "Model Provider" > "Tool Provider" > "Add Custom Tool Provider"
2. Enter a name (e.g., "Patent Trend Analysis API")
3. Upload or paste the contents of `trend-analysis-api-spec.json`
4. Configure the authentication if needed (no authentication by default)
5. Save the provider

Example configuration:

```json
{
  "name": "Patent Trend Analysis API",
  "description": "API for analyzing patent classification trends by applicant and generating reports",
  "base_url": "http://localhost:5006",
  "auth": {
    "type": "none"
  },
  "tools": [
    {
      "name": "analyzePatentTrends",
      "description": "Analyze patent trends by classification and year for a specific applicant"
    },
    {
      "name": "generatePatentTrendsPDF",
      "description": "Generate a PDF report of patent trends by classification for a specific applicant"
    },
    {
      "name": "analyzeClassificationTrends",
      "description": "Analyze patent trends by applicant and year for a specific patent classification"
    },
    {
      "name": "generateClassificationTrendsPDF",
      "description": "Generate a PDF report of patent trends by applicant for a specific classification"
    }
  ]
}
```

## Using the APIs in Dify Applications

### Setting Up API Access in an Application

1. After adding the tool providers, create or edit a Dify application
2. Go to the "Tools" section
3. Enable the tool providers you've added
4. Save the changes

### Example Prompts for Using the APIs

#### Database API Example

```
Use the SQLite Database API to execute the following query on the bigquery database:
SELECT publication_number, title FROM publications WHERE title LIKE '%artificial intelligence%' LIMIT 10
```

#### Natural Language Query Example

```
Use the Natural Language Query API to ask this question on the bigquery database:
米国と日本の特許公開件数を比較して
```

#### Trend Analysis API Example

```
Use the Patent Trend Analysis API to analyze patent trends for テック株式会社 from 2015 to 2023
```

## Additional Notes

- Make sure all services are running (database-api on port 5003, nl-query-api on port 5004, trend-analysis on port 5006)
- Update the base URLs in the Dify configuration if your services are running on different hosts or ports
- These APIs can be used together in a Dify application to create powerful patent analysis capabilities
