import os
import sys
import json
import zipfile
import io
import uvicorn
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import requests

# Add path for importing local modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import SQLite database modules
from app.patent_system.models_sqlite import ensure_db_exists, SessionLocal, get_db
from app.patent_system.db_sqlite import SQLiteDBManager
from sqlalchemy.orm import Session

app = FastAPI(title="Patent Analysis MCP Server", 
              description="MCP server for patent application trend analysis",
              version="1.0.0")

# Define request models for OpenAPI
class PatentAnalysisRequest(BaseModel):
    applicant_name: str
    db_type: Optional[str] = "sqlite"

class MCPToolRequest(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]

# Output directory for generated files
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure LLM service URL
LLM_SERVICE_URL = os.environ.get("LLM_SERVICE_URL", "http://patentdwh-mcp-enhanced:8080/api/v1/mcp")
DB_URL = os.environ.get("DB_URL", "http://patentdwh-db:5002/api/sql-query")

def sanitize_string_for_filename(input_string):
    """Convert Japanese characters to romaji for filenames"""
    return re.sub(r'[^\w\-_. ]', '', input_string)

def execute_sql_query(query, db_type="sqlite"):
    """Execute SQL query using the patent_sql_query tool via MCP API or direct DB access"""
    try:
        if db_type == "sqlite":
            # Use local SQLite connection
            with SQLiteDBManager() as db_manager:
                # This is a simplification - in a real implementation you'd 
                # interpret the SQL query and use the appropriate DB methods
                if "SELECT" in query.upper() and "COUNT" in query.upper() and "GROUP BY" in query.upper():
                    # Assume it's a classification count query
                    if "LIKE" in query.upper():
                        # Extract the applicant name from the query (simplified)
                        match = re.search(r"LIKE\s+['\"]%(.+?)%['\"]", query)
                        if match:
                            applicant_name = match.group(1)
                            # Get patents by applicant
                            patents = db_manager.get_patents_by_applicant(applicant_name)
                            # Process to get IPC classifications by year
                            result = process_patents_for_trends(patents)
                            return {
                                "success": True,
                                "columns": ["year", "ipc_class", "count"],
                                "data": result
                            }
                
                # Fallback to the API for other queries
                payload = {
                    "query": query,
                    "db_type": db_type
                }
                response = requests.post(DB_URL, json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"API error: {response.status_code} - {response.text}")
                    return None
        else:
            # Use the API for non-SQLite databases
            payload = {
                "query": query,
                "db_type": db_type
            }
            response = requests.post(DB_URL, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Exception executing query: {str(e)}")
        return None

def execute_nl_query(query, db_type="sqlite"):
    """Execute natural language query using LLM API"""
    try:
        payload = {
            "tool_name": "patent_nl_query",
            "tool_input": {
                "query": query,
                "db_type": db_type
            }
        }
        response = requests.post(LLM_SERVICE_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                return data
            else:
                print(f"Query error: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception executing query: {str(e)}")
        return None

def process_patents_for_trends(patents):
    """Process patent data to extract trends by year and IPC classification"""
    # Create a list to store results
    results = []
    
    # Process each patent
    for patent in patents:
        # Get the application year
        if patent.application_date:
            year = patent.application_date.strftime("%Y")
            
            # Process each IPC classification
            for ipc in patent.ipc_classifications:
                # Get the main class (first 3 or 4 characters)
                ipc_class = ipc.code[:3] if len(ipc.code) >= 3 else ipc.code
                
                # Add to results
                results.append({
                    "year": year,
                    "ipc_class": ipc_class,
                    "count": 1  # Each patent counts as 1
                })
    
    # Convert to DataFrame for aggregation
    if not results:
        return []
        
    df = pd.DataFrame(results)
    
    # Group by year and IPC class, counting occurrences
    grouped = df.groupby(['year', 'ipc_class']).size().reset_index(name='count')
    
    # Convert back to list of dictionaries
    return grouped.to_dict('records')

def get_patent_trends_by_applicant(applicant_name, db_type="sqlite"):
    """Get patent application trends by classification for a specific applicant from SQLite DB"""
    print(f"Analyzing patent trends for applicant: {applicant_name}")
    
    if db_type == "sqlite":
        # Use local SQLite connection
        with SQLiteDBManager() as db_manager:
            # Get patents by applicant
            patents = db_manager.get_patents_by_applicant(applicant_name)
            print(f"Found {len(patents)} patents for applicant {applicant_name}")
            
            # Process to get IPC classifications by year
            results = process_patents_for_trends(patents)
            
            # Convert to DataFrame
            if not results:
                print(f"No trend data found for applicant {applicant_name}")
                return pd.DataFrame()
                
            df = pd.DataFrame(results)
            
            return df
    else:
        # Use SQL query for other databases
        query = f"""
        SELECT 
            SUBSTR(p.application_date, 1, 4) AS year,
            SUBSTR(ipc.code, 1, 3) AS ipc_class,
            COUNT(*) AS count
        FROM patents p
        JOIN applicants a ON p.id = a.patent_id
        JOIN ipc_classifications ipc ON p.id = ipc.patent_id
        WHERE a.name LIKE '%{applicant_name}%'
        GROUP BY year, ipc_class
        ORDER BY year, count DESC
        """
        
        result = execute_sql_query(query, db_type)
        if result and "data" in result:
            df = pd.DataFrame(result["data"])
            print(f"Retrieved {len(df)} trend records via SQL")
            return df
        else:
            print("Failed to retrieve data via SQL")
            return pd.DataFrame()

def generate_trend_chart(df, applicant_name):
    """Generate a bar chart showing patent application trends over time by classification"""
    if df is None or df.empty:
        print("No data available to generate chart")
        return None
    
    # Get unique years and IPC classes
    years = sorted(df['year'].unique())
    ipc_classes = sorted(df['ipc_class'].unique())
    
    # Map IPC codes to English names
    ipc_mapping = {
        'A01': 'Agriculture',
        'A23': 'Foods',
        'A61': 'Medical/Health',
        'B01': 'Phys/Chem Processes',
        'B23': 'Machine Tools',
        'B29': 'Plastics',
        'B32': 'Layered Products',
        'B60': 'Vehicles',
        'B65': 'Conveying/Packaging',
        'C01': 'Inorganic Chemistry',
        'C02': 'Water Treatment',
        'C07': 'Organic Chemistry',
        'C08': 'Polymers',
        'C09': 'Dyes/Paints',
        'C12': 'Biochemistry',
        'C22': 'Metallurgy',
        'C23': 'Coatings',
        'D01': 'Textiles',
        'E04': 'Buildings',
        'F01': 'Machines/Engines',
        'F02': 'Combustion Engines',
        'F16': 'Engineering Elements',
        'F25': 'Refrigeration',
        'G01': 'Measuring/Testing',
        'G02': 'Optics',
        'G03': 'Photography',
        'G05': 'Controlling',
        'G06': 'Computing',
        'G06F': 'Electric Digital Data',
        'G06N': 'AI/Machine Learning',
        'G06Q': 'Business Methods',
        'G06T': 'Image Processing',
        'G09': 'Education/Display',
        'G10': 'Musical Instruments',
        'G11': 'Information Storage',
        'H01': 'Electric Elements',
        'H02': 'Electric Power',
        'H03': 'Electronic Circuitry',
        'H04': 'Electric Communication',
        'H04L': 'Digital Transmission',
        'H04N': 'Image Communication',
        'H05': 'Electric Techniques'
    }
    
    # Create a pivot table for plotting
    pivot_df = df.pivot_table(index='year', columns='ipc_class', values='count', fill_value=0)
    
    # Sort columns by total count to make the chart more readable
    column_sums = pivot_df.sum()
    sorted_columns = column_sums.sort_values(ascending=False).index
    pivot_df = pivot_df[sorted_columns]
    
    # Limit to top 10 classes for readability if there are too many
    if len(pivot_df.columns) > 10:
        top_columns = pivot_df.sum().sort_values(ascending=False).index[:10]
        pivot_df = pivot_df[top_columns]
        
    # Replace IPC codes with English names where possible
    renamed_columns = [ipc_mapping.get(col, col) for col in pivot_df.columns]
    pivot_df.columns = renamed_columns
    
    # Create the stacked bar chart
    plt.figure(figsize=(14, 8))
    ax = pivot_df.plot(kind='bar', stacked=True, figsize=(14, 8))
    
    # Set labels and title
    safe_applicant_name = re.sub(r'[^\x00-\x7F]', '', applicant_name)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Applications', fontsize=12)
    ax.set_title(f'Patent Applications by Classification: {safe_applicant_name}', fontsize=14)
    
    # Enhance legend
    plt.legend(title='IPC Classification', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    filename = os.path.join(OUTPUT_DIR, f"{sanitize_string_for_filename(applicant_name)}_classification_trend.png")
    plt.savefig(filename)
    print(f"Chart saved as {filename}")
    
    return filename

def analyze_trends_with_llm(df, applicant_name):
    """Use the LLM to analyze patent application trends"""
    if df is None or df.empty:
        return "データが見つかりませんでした。"
    
    # Create a summary dataframe for analysis
    yearly_totals = df.groupby('year')['count'].sum().reset_index()
    yearly_totals = yearly_totals.sort_values('year')
    
    class_totals = df.groupby('ipc_class')['count'].sum().reset_index()
    class_totals = class_totals.sort_values('count', ascending=False)
    
    # Create analysis prompt
    analysis_query = f"""
    以下は{applicant_name}の特許出願データです。このデータに基づいて、特許出願動向の分析を日本語で行ってください。
    時系列の傾向、主要な技術分野、特徴的な変化などに着目し、300〜500文字程度でまとめてください。
    
    【年別出願数】
    {yearly_totals.to_string(index=False)}
    
    【IPC分類別出願数】
    {class_totals.to_string(index=False)}
    
    【年度・分類別の詳細データ】
    {df.to_string(index=False)}
    """
    
    # Execute natural language query
    result = execute_nl_query(analysis_query)
    
    if result and "response" in result:
        return result["response"]
    else:
        # Fallback if NL query fails
        return f"{applicant_name}の特許出願動向の分析結果を取得できませんでした。SQLiteデータベースから直接データを確認してください。"

def generate_markdown_report(applicant_name, chart_filename, trend_analysis):
    """Generate a markdown report with the chart and analysis"""
    if chart_filename:
        chart_base_name = os.path.basename(chart_filename)
    else:
        chart_base_name = "chart_unavailable.png"
    
    report = f"""
# {applicant_name}の特許出願動向分析

## 特許分類別出願動向

![特許分類別出願動向]({chart_base_name})

## 動向分析

{trend_analysis}

"""
    # Save the report
    report_filename = os.path.join(OUTPUT_DIR, f"{sanitize_string_for_filename(applicant_name)}_patent_analysis.md")
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved as {report_filename}")
    return report_filename

@app.get("/")
async def root():
    return {"status": "ok", "message": "Patent Analysis MCP Server is running"}

@app.post("/api/v1/mcp")
async def mcp_endpoint(request: MCPToolRequest):
    """
    MCP compatible endpoint that handles tool requests
    """
    try:
        tool_name = request.tool_name
        tool_input = request.tool_input
        
        if tool_name == "analyze_patent_trends":
            applicant_name = tool_input.get("applicant_name")
            db_type = tool_input.get("db_type", "sqlite")
            
            if not applicant_name:
                return {"success": False, "error": "applicant_name is required"}
            
            result = await analyze_patent_data(applicant_name, db_type)
            return {"success": True, "response": result}
        else:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/analyze")
async def analyze_patents(request: PatentAnalysisRequest):
    """
    Analyze patent trends for an applicant and return JSON results
    """
    try:
        applicant_name = request.applicant_name
        db_type = request.db_type
        
        # Get patent trend data
        df = get_patent_trends_by_applicant(applicant_name, db_type)
        
        # Generate trend chart
        chart_filename = generate_trend_chart(df, applicant_name)
        chart_base_name = os.path.basename(chart_filename) if chart_filename else None
        
        # Analyze trends
        trend_analysis = analyze_trends_with_llm(df, applicant_name)
        
        # Generate markdown report
        report_filename = generate_markdown_report(applicant_name, chart_filename, trend_analysis)
        report_base_name = os.path.basename(report_filename)
        
        # Convert relative paths to absolute for response
        chart_path = chart_filename if chart_filename else None
        report_path = report_filename if report_filename else None
        
        response = {
            "applicant_name": applicant_name,
            "chart_filename": chart_base_name,
            "report_filename": report_base_name,
            "trend_analysis": trend_analysis
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing patent data: {str(e)}")

@app.get("/api/report/{applicant_name}")
async def get_report(applicant_name: str):
    """
    Get the markdown report for an applicant
    """
    try:
        # Create the report filename
        filename = sanitize_string_for_filename(applicant_name)
        report_path = os.path.join(OUTPUT_DIR, f"{filename}_patent_analysis.md")
        
        # If the report doesn't exist, generate it
        if not os.path.exists(report_path):
            df = get_patent_trends_by_applicant(applicant_name)
            chart_filename = generate_trend_chart(df, applicant_name)
            trend_analysis = analyze_trends_with_llm(df, applicant_name)
            report_path = generate_markdown_report(applicant_name, chart_filename, trend_analysis)
        
        # Read the report content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Return the markdown content directly
        return Response(content=content, media_type="text/markdown")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving report: {str(e)}")

@app.get("/api/report/{applicant_name}/zip")
async def get_report_zip(applicant_name: str):
    """
    Get the markdown report and associated images as a zip file
    """
    try:
        # Create the report filename
        filename = sanitize_string_for_filename(applicant_name)
        report_path = os.path.join(OUTPUT_DIR, f"{filename}_patent_analysis.md")
        chart_path = os.path.join(OUTPUT_DIR, f"{filename}_classification_trend.png")
        
        # If the report doesn't exist, generate it
        if not os.path.exists(report_path) or not os.path.exists(chart_path):
            df = get_patent_trends_by_applicant(applicant_name)
            chart_path = generate_trend_chart(df, applicant_name)
            trend_analysis = analyze_trends_with_llm(df, applicant_name)
            report_path = generate_markdown_report(applicant_name, chart_path, trend_analysis)
        
        # Create a zip file in memory
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            # Add the report markdown file
            zip_file.write(report_path, os.path.basename(report_path))
            
            # Add the chart image
            if os.path.exists(chart_path):
                zip_file.write(chart_path, os.path.basename(chart_path))
        
        # Reset the file pointer
        zip_io.seek(0)
        
        # Create a response with the zip file
        return StreamingResponse(
            zip_io, 
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}_patent_analysis.zip"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating zip archive: {str(e)}")

# For compatibility with dify's API expectations
@app.post("/api/tools/execute")
async def execute_patent_tool(request: dict):
    """
    Execute patent analysis tool and return results in Dify format
    """
    try:
        if "tool_name" not in request or "arguments" not in request:
            raise HTTPException(status_code=400, detail="Missing required fields: tool_name, arguments")
            
        tool_name = request.get("tool_name")
        arguments = request.get("arguments", {})
        
        if tool_name == "analyze_patent_trends":
            applicant_name = arguments.get("applicant_name")
            if not applicant_name:
                raise HTTPException(status_code=400, detail="Missing required argument: applicant_name")
                
            db_type = arguments.get("db_type", "sqlite")
            
            # Get patent trend data
            df = get_patent_trends_by_applicant(applicant_name, db_type)
            chart_filename = generate_trend_chart(df, applicant_name)
            trend_analysis = analyze_trends_with_llm(df, applicant_name)
            report_filename = generate_markdown_report(applicant_name, chart_filename, trend_analysis)
            
            # Create download URL for the zip file
            zip_url = f"/api/report/{applicant_name}/zip"
            
            return {
                "result": {
                    "applicant_name": applicant_name,
                    "trend_analysis": trend_analysis,
                    "report_url": zip_url,
                    "message": f"特許分析レポートが作成されました。ZIPファイルをダウンロードしてください。"
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")

async def analyze_patent_data(applicant_name, db_type="sqlite"):
    """Helper function to analyze patent data and return a summary"""
    df = get_patent_trends_by_applicant(applicant_name, db_type)
    
    # Generate trend chart
    chart_filename = generate_trend_chart(df, applicant_name)
    
    # Analyze trends
    trend_analysis = analyze_trends_with_llm(df, applicant_name)
    
    # Generate markdown report
    report_filename = generate_markdown_report(applicant_name, chart_filename, trend_analysis)
    
    # Get the base filename without path
    filename = sanitize_string_for_filename(applicant_name)
    
    # Create a nicer formatted response message with download link
    result = {
        "summary": trend_analysis,
        "report_file": f"{filename}_patent_analysis.md",
        "chart_file": f"{filename}_classification_trend.png",
        "download_url": f"/api/report/{applicant_name}/zip"
    }
    
    return result

# Initialize database at startup
@app.on_event("startup")
async def startup_event():
    """Initialize the database on server startup"""
    ensure_db_exists()

# OpenAPI specification with tool definitions for Dify
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    """Custom OpenAPI schema for Dify integration"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.openapi()
    
    # Add tool definitions for Dify
    openapi_schema["components"]["schemas"]["PatentAnalysisTool"] = {
        "type": "object",
        "properties": {
            "tool_name": {"type": "string", "enum": ["analyze_patent_trends"]},
            "arguments": {
                "type": "object",
                "properties": {
                    "applicant_name": {"type": "string", "description": "The name of the applicant to analyze"},
                    "db_type": {"type": "string", "description": "Database type to use", "default": "sqlite"}
                },
                "required": ["applicant_name"]
            }
        },
        "required": ["tool_name", "arguments"]
    }
    
    # Add specific path for Dify tool execution
    openapi_schema["paths"]["/api/tools/execute"] = {
        "post": {
            "operationId": "execute_patent_tool",
            "summary": "Execute patent analysis tool",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/PatentAnalysisTool"}
                    }
                },
                "required": True
            },
            "responses": {
                "200": {
                    "description": "Tool execution result",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "result": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("patent_analysis_mcp_server:app", host=host, port=port, reload=True)
