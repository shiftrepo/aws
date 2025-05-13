# Patent Classification Trend Analysis Service

This service analyzes patent application trends by applicant name, providing classification-based analysis with visualizations and assessments. It accesses the local SQLite database through the database API service and provides an HTTP API for use with Dify MCP.

## Features

- Query patent application data by applicant name through SQLite database API
- Filter data by year range (optional)
- Generate classification-based trend analysis 
- Create bar chart visualization showing trends over time
- Provide written assessment of the applicant's patent activity patterns
- Convert Japanese text to English for better display in charts
- Generate PDF reports with visualizations and assessments

## API Endpoints

### GET /health
Health check endpoint to verify service is operational.

### POST /analyze
Main analysis endpoint that accepts:
```json
{
  "applicant_name": "Required: Name of applicant/company to analyze",
  "start_year": "Optional: Starting year for analysis period (e.g., 2010)",
  "end_year": "Optional: Ending year for analysis period (e.g., 2023)"
}
```

Returns:
```json
{
  "applicant_name": "Name provided in request",
  "yearly_classification_counts": {
    "YEAR": {
      "CLASS_CODE": count,
      "...": "..."
    },
    "...": "..."
  },
  "chart_image": "Base64-encoded PNG image of trend chart",
  "assessment": "Text assessment of patent trends"
}
```

### POST /analyze_pdf
PDF report generation endpoint that accepts the same parameters as /analyze:
```json
{
  "applicant_name": "Required: Name of applicant/company to analyze",
  "start_year": "Optional: Starting year for analysis period (e.g., 2010)",
  "end_year": "Optional: Ending year for analysis period (e.g., 2023)"
}
```

Returns a downloadable PDF file containing:
- Patent trend visualization chart
- Assessment of patent filing activities
- Information about dominant technology areas
- Technical diversification analysis

### GET /
Root endpoint with general API information.

## Configuration

### Environment Variables

- `DATABASE_API_URL`: URL for database service (default: http://sqlite-db:5000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Integration with Dify

This service can be integrated with Dify as an MCP server. The Dify configuration file is provided at `dify/trend_analysis_mcp_server.yml`.

To use in Dify:
1. Start the Trend Analysis service
2. Import the MCP server configuration in Dify
3. The tool `analyze_patent_trends` will be available for use in your Dify applications

## IPC Classification Codes

The analysis uses the first letter of IPC classification codes, which represent:

- A: Human Necessities
- B: Performing Operations; Transporting
- C: Chemistry; Metallurgy
- D: Textiles; Paper
- E: Fixed Constructions
- F: Mechanical Engineering; Lighting; Heating; Weapons; Blasting
- G: Physics
- H: Electricity

## Development

### Requirements

See `requirements.txt` for complete list of dependencies.

### HTTP Request Example

```bash
# Analyze patent trends for an applicant
curl -X POST http://localhost:5006/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "テック株式会社",
    "start_year": 2010,
    "end_year": 2023
  }'
```

### Running Locally

```bash
# Set environment variables
export DATABASE_API_URL=http://localhost:5003

# Run service
uvicorn app:app --host 0.0.0.0 --port 5000
```

### Rebuilding Container

Use the provided rebuild script:
```bash
./rebuild_trend_analysis.sh
