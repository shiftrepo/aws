from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from fpdf import FPDF
import tempfile
import os
import io
from datetime import datetime
import os
import tempfile
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import pandas as pd
import json
import sqlite3
import re
from typing import List, Dict, Optional, Any
import logging
import base64
from io import BytesIO
import seaborn as sns
from japanesetoeng import japanese_to_english
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup FastAPI app
app = FastAPI(
    title="Patent Classification Trend Analysis API",
    description="API for analyzing patent classification trends by applicant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Japanese to English conversion module
class JapaneseToEnglish:
    @staticmethod
    def convert(text):
        """Convert Japanese text to English using romaji"""
        # This is a simple implementation - in a real system, 
        # you'd use a proper translation library
        mapping = {
            '株式会社': 'Corporation',
            'テクノロジー': 'Technology',
            'サイエンス': 'Science',
            'エレクトロニクス': 'Electronics',
            'システム': 'Systems',
            'デバイス': 'Devices',
            '研究所': 'Laboratory',
            'グループ': 'Group',
            '製作所': 'Works',
            '電機': 'Electric',
            '電子': 'Electronics',
            '開発': 'Development',
            '特許': 'Patent',
            '出願': 'Application',
            '分析': 'Analysis',
            '技術': 'Technical',
            '年': 'Year',
            '件数': 'Count',
            '合計': 'Total',
            '分類': 'Classification'
        }
        
        for ja, en in mapping.items():
            text = text.replace(ja, en)
        
        # Convert remaining Japanese characters to romaji
        return re.sub(r'[^\x00-\x7F]+', 'X', text)

japanese_to_english = JapaneseToEnglish()

# Models for applicant-based endpoints
class PatentTrendRequest(BaseModel):
    applicant_name: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None

class PatentTrendResponse(BaseModel):
    applicant_name: str
    yearly_classification_counts: Dict[str, Dict[str, int]]
    chart_image: str
    assessment: str

# Models for classification-based endpoints
class ClassificationTrendRequest(BaseModel):
    classification_code: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None

class ClassificationTrendResponse(BaseModel):
    classification_code: str
    yearly_applicant_counts: Dict[str, Dict[str, int]]
    chart_image: str
    assessment: str

# Database connection setup
def get_db_connection():
    """Connect to the database API"""
    try:
        # Get database URL from environment or use default
        db_api_url = os.environ.get("DATABASE_API_URL", "http://sqlite-db:5000")
        logger.info(f"Using database API at {db_api_url}")
        return db_api_url
    except Exception as e:
        logger.error(f"Failed to set up database connection: {e}")
        raise Exception(f"Database connection setup failed: {e}")

# Helper functions for analysis
def analyze_patent_trends(applicant_name: str, start_year: Optional[int] = None, end_year: Optional[int] = None):
    """Query SQLite database for patent application data by classification and year"""
    db_url = get_db_connection()
    
    # Build the SQL query with parameters for the database API
    where_clauses = ["assignee_original LIKE '%' || ? || '%'"]
    params = [applicant_name]
    
    if start_year:
        where_clauses.append("substr(filing_date, 1, 4) >= ?")
        params.append(str(start_year))
    
    if end_year:
        where_clauses.append("substr(filing_date, 1, 4) <= ?")
        params.append(str(end_year))
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
        SELECT 
            substr(filing_date, 1, 4) as year,
            substr(ipc_code, 1, 1) as class_code,
            COUNT(*) as application_count
        FROM 
            publications
        WHERE 
            {where_clause}
        GROUP BY 
            substr(filing_date, 1, 4), 
            substr(ipc_code, 1, 1)
        ORDER BY 
            substr(filing_date, 1, 4), 
            substr(ipc_code, 1, 1)
    """
    
    try:
        # For the database API, we need to replace the placeholders (?) with actual values
        # since the API doesn't support parameterized queries directly
        query_with_params = query
        
        # Replace placeholders with literal values
        actual_query = f"""
        SELECT 
            substr(filing_date, 1, 4) as year,
            substr(ipc_code, 1, 1) as class_code,
            COUNT(*) as application_count
        FROM 
            publications
        WHERE 
            assignee_original LIKE '%{applicant_name}%'
        """
        
        # Add year filters if provided
        if start_year:
            actual_query += f" AND substr(filing_date, 1, 4) >= '{start_year}'"
        
        if end_year:
            actual_query += f" AND substr(filing_date, 1, 4) <= '{end_year}'"
            
        actual_query += """
        GROUP BY 
            substr(filing_date, 1, 4), 
            substr(ipc_code, 1, 1)
        ORDER BY 
            substr(filing_date, 1, 4), 
            substr(ipc_code, 1, 1)
        """
        
        logger.info(f"Sending query to database API: {actual_query}")
        
        # Send query to database API
        response = requests.post(
            f"{db_url}/execute/bigquery",
            json={"query": actual_query}
        )
        
        if response.status_code != 200:
            raise Exception(f"Database API returned error: {response.status_code}, {response.text}")
        
        result = response.json()
        
        # Process results into the desired format
        yearly_classification_counts = {}
        
        # Extract rows from API response
        for row in result.get("rows", []):
            year = str(row.get("year"))
            class_code = row.get("class_code") if row.get("class_code") else "Unclassified"
            application_count = row.get("application_count", 0)
            
            if year not in yearly_classification_counts:
                yearly_classification_counts[year] = {}
            
            if class_code in yearly_classification_counts[year]:
                yearly_classification_counts[year][class_code] += application_count
            else:
                yearly_classification_counts[year][class_code] = application_count
        
        return yearly_classification_counts
    
    except Exception as e:
        logger.error(f"Error querying database: {e}")
        raise Exception(f"Error retrieving patent trend data: {e}")

def analyze_classification_trends(classification_code: str, start_year: Optional[int] = None, end_year: Optional[int] = None):
    """Query SQLite database for patent application data by applicant and year for a specific classification"""
    db_url = get_db_connection()
    
    # Build the SQL query
    where_clauses = [f"substr(ipc_code, 1, 1) = '{classification_code}'"]
    
    if start_year:
        where_clauses.append(f"substr(filing_date, 1, 4) >= '{start_year}'")
    
    if end_year:
        where_clauses.append(f"substr(filing_date, 1, 4) <= '{end_year}'")
    
    where_clause = " AND ".join(where_clauses)
    
    # Query to get top applicants per year for the specified classification
    actual_query = f"""
    SELECT 
        substr(filing_date, 1, 4) as year,
        assignee_original as applicant_name,
        COUNT(*) as application_count
    FROM 
        publications
    WHERE 
        {where_clause}
    GROUP BY 
        substr(filing_date, 1, 4), 
        assignee_original
    ORDER BY 
        substr(filing_date, 1, 4), 
        COUNT(*) DESC
    """
    
    try:
        logger.info(f"Sending classification query to database API: {actual_query}")
        
        # Send query to database API
        response = requests.post(
            f"{db_url}/execute/bigquery",
            json={"query": actual_query}
        )
        
        if response.status_code != 200:
            raise Exception(f"Database API returned error: {response.status_code}, {response.text}")
        
        result = response.json()
        
        # Process results into the desired format
        yearly_applicant_counts = {}
        
        # Extract rows from API response and group by year
        for row in result.get("rows", []):
            year = str(row.get("year"))
            applicant = row.get("applicant_name", "Unknown")
            application_count = row.get("application_count", 0)
            
            if year not in yearly_applicant_counts:
                yearly_applicant_counts[year] = {}
            
            # Only keep top 5 applicants per year to prevent cluttering the chart
            if len(yearly_applicant_counts[year]) < 5:
                yearly_applicant_counts[year][applicant] = application_count
        
        return yearly_applicant_counts
    
    except Exception as e:
        logger.error(f"Error querying classification data: {e}")
        raise Exception(f"Error retrieving classification trend data: {e}")

def generate_trend_chart(applicant_name: str, yearly_classification_counts: Dict[str, Dict[str, int]]):
    """Generate a bar chart visualization of the patent classification trends"""
    plt.figure(figsize=(12, 8))
    
    # Convert the nested dict into a pandas DataFrame for easier plotting
    data = []
    for year, class_counts in yearly_classification_counts.items():
        for class_name, count in class_counts.items():
            data.append({"Year": year, "Class": class_name, "Count": count})
    
    df = pd.DataFrame(data)
    
    # Check if we have data to plot
    if df.empty:
        plt.text(0.5, 0.5, "No data available for the specified criteria", 
                 horizontalalignment='center', verticalalignment='center')
    else:
        # Set seaborn style
        sns.set(style="whitegrid")
        
        # Convert applicant name for the title
        safe_applicant = japanese_to_english.convert(applicant_name)
        
        # Create pivot table for plotting
        pivot_df = df.pivot_table(
            index="Year", 
            columns="Class", 
            values="Count",
            aggfunc="sum",
            fill_value=0
        )
        
        # Plot stacked bar chart
        ax = pivot_df.plot(kind="bar", stacked=True, figsize=(12, 8), cmap="tab10")
        
        # Customize the plot
        plt.title(f"Patent Classifications by Year for {safe_applicant}", fontsize=16)
        plt.xlabel("Year", fontsize=14)
        plt.ylabel("Number of Patent Applications", fontsize=14)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add annotations for total counts on top of each bar
        for i, year in enumerate(pivot_df.index):
            total = pivot_df.loc[year].sum()
            ax.text(i, total + 5, f'Total: {int(total)}', ha='center', fontweight='bold')
        
        # Add legend with a title
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, title="IPC Classes", title_fontsize=12, 
                 bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
    
    # Save to bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    
    # Convert to base64 for embedding in JSON
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

def generate_classification_chart(classification_code: str, yearly_applicant_counts: Dict[str, Dict[str, int]]):
    """Generate a bar chart visualization of the top applicants by year for a classification"""
    plt.figure(figsize=(14, 9))
    
    # Convert the nested dict into a pandas DataFrame for easier plotting
    data = []
    for year, applicant_counts in yearly_applicant_counts.items():
        for applicant, count in applicant_counts.items():
            applicant_safe = japanese_to_english.convert(applicant)
            # Truncate long applicant names
            if len(applicant_safe) > 20:
                applicant_safe = applicant_safe[:18] + "..."
            data.append({"Year": year, "Applicant": applicant_safe, "Count": count})
    
    df = pd.DataFrame(data)
    
    # Check if we have data to plot
    if df.empty:
        plt.text(0.5, 0.5, "No data available for the specified criteria", 
                 horizontalalignment='center', verticalalignment='center')
    else:
        # Set seaborn style
        sns.set(style="whitegrid")
        
        # Get class description
        class_description = get_ipc_class_description(classification_code)
        
        # Create pivot table for plotting
        pivot_df = df.pivot_table(
            index="Year", 
            columns="Applicant", 
            values="Count",
            aggfunc="sum",
            fill_value=0
        )
        
        # Plot stacked bar chart
        ax = pivot_df.plot(kind="bar", stacked=True, figsize=(14, 9), cmap="tab20")
        
        # Customize the plot
        plt.title(f"Top Applicants by Year for IPC Class {classification_code} ({class_description})", fontsize=16)
        plt.xlabel("Year", fontsize=14)
        plt.ylabel("Number of Patent Applications", fontsize=14)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add annotations for total counts on top of each bar
        for i, year in enumerate(pivot_df.index):
            total = pivot_df.loc[year].sum()
            ax.text(i, total + 5, f'Total: {int(total)}', ha='center', fontweight='bold')
        
        # Add legend with a title
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, title="Top Applicants", title_fontsize=12, 
                 bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
    
    # Save to bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    
    # Convert to base64 for embedding in JSON
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

def generate_assessment(applicant_name: str, yearly_classification_counts: Dict[str, Dict[str, int]]):
    """Generate an assessment based on the patent trend data"""
    try:
        # Convert data structure to DataFrame for analysis
        data = []
        for year, class_counts in yearly_classification_counts.items():
            for class_name, count in class_counts.items():
                data.append({"Year": int(year), "Class": class_name, "Count": count})
        
        df = pd.DataFrame(data)
        
        if df.empty:
            return f"No patent application data found for {applicant_name}."
        
        # Calculate total patents by year
        yearly_totals = df.groupby("Year")["Count"].sum()
        
        # Find trend direction (increasing, decreasing, stable)
        if len(yearly_totals) >= 2:
            years = sorted(yearly_totals.index)
            first_year = years[0]
            last_year = years[-1]
            
            first_count = yearly_totals[first_year]
            last_count = yearly_totals[last_year]
            
            percent_change = ((last_count - first_count) / first_count * 100) if first_count > 0 else 0
            
            if percent_change > 20:
                trend_direction = "significantly increasing"
            elif percent_change > 5:
                trend_direction = "increasing"
            elif percent_change < -20:
                trend_direction = "significantly decreasing"
            elif percent_change < -5:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "unknown (insufficient data)"
        
        # Calculate dominant technology areas
        class_totals = df.groupby("Class")["Count"].sum().sort_values(ascending=False)
        dominant_classes = class_totals.head(3)
        
        # Generate assessment text
        safe_applicant = japanese_to_english.convert(applicant_name)
        
        assessment = f"Assessment for {safe_applicant}:\n\n"
        
        # Overall trend
        assessment += f"1. Overall Patent Activity: The patent application trend is {trend_direction} "
        assessment += f"from {first_year} to {last_year}.\n\n"
        
        # Dominant technology areas
        assessment += "2. Dominant Technology Areas:\n"
        for i, (class_name, count) in enumerate(dominant_classes.items(), 1):
            percentage = (count / class_totals.sum()) * 100
            class_description = get_ipc_class_description(class_name)
            assessment += f"   - {class_name} ({class_description}): {count} applications ({percentage:.1f}%)\n"
        
        # Year with highest activity
        if len(yearly_totals) > 0:
            max_year = yearly_totals.idxmax()
            max_count = yearly_totals[max_year]
            assessment += f"\n3. Peak Activity: The highest number of patent applications ({max_count}) was in {max_year}.\n"
        
        # Technology diversification
        unique_classes_by_year = df.groupby("Year")["Class"].nunique()
        if len(unique_classes_by_year) >= 2:
            first_year_diversity = unique_classes_by_year.get(first_year, 0)
            last_year_diversity = unique_classes_by_year.get(last_year, 0)
            
            if last_year_diversity > first_year_diversity:
                diversity_trend = "increased"
            elif last_year_diversity < first_year_diversity:
                diversity_trend = "decreased"
            else:
                diversity_trend = "remained stable"
                
            assessment += f"\n4. Technology Diversification: The number of technology areas has {diversity_trend} "
            assessment += f"from {first_year_diversity} in {first_year} to {last_year_diversity} in {last_year}.\n"
        
        return assessment
        
    except Exception as e:
        logger.error(f"Error generating assessment: {e}")
        return f"Unable to generate assessment due to an error: {str(e)}"

def generate_classification_assessment(classification_code: str, yearly_applicant_counts: Dict[str, Dict[str, int]]):
    """Generate an assessment for a classification trend analysis"""
    try:
        # Flatten the nested dict into a DataFrame
        data = []
        for year, applicant_counts in yearly_applicant_counts.items():
            for applicant, count in applicant_counts.items():
                data.append({"Year": int(year), "Applicant": applicant, "Count": count})
        
        df = pd.DataFrame(data)
        
        if df.empty:
            return f"No patent application data found for classification code {classification_code}."
        
        # Get classification description
        class_description = get_ipc_class_description(classification_code)
        
        # Calculate total patents by year
        yearly_totals = df.groupby("Year")["Count"].sum()
        
        # Find trend direction
        if len(yearly_totals) >= 2:
            years = sorted(yearly_totals.index)
            first_year = years[0]
            last_year = years[-1]
            
            first_count = yearly_totals[first_year]
            last_count = yearly_totals[last_year]
            
            percent_change = ((last_count - first_count) / first_count * 100) if first_count > 0 else 0
            
            if percent_change > 20:
                trend_direction = "significantly increasing"
            elif percent_change > 5:
                trend_direction = "increasing"
            elif percent_change < -20:
                trend_direction = "significantly decreasing"
            elif percent_change < -5:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "unknown (insufficient data)"
            first_year = years[0] if len(yearly_totals) > 0 else "N/A"
            last_year = years[-1] if len(yearly_totals) > 0 else "N/A"
        
        # Calculate dominant applicants overall
        applicant_totals = df.groupby("Applicant")["Count"].sum().sort_values(ascending=False)
        dominant_applicants = applicant_totals.head(5)
        
        # Build the assessment
        assessment = f"Assessment for IPC Class {classification_code} ({class_description}):\n\n"
        
        # Overall trend
        assessment += f"1. Overall Trend: Patent applications in this classification are {trend_direction} "
        assessment += f"from {first_year} to {last_year}.\n\n"
        
        # Top applicants
        assessment += "2. Top Applicants in this Classification:\n"
        for i, (applicant, count) in enumerate(dominant_applicants.items(), 1):
            percentage = (count / applicant_totals.sum()) * 100
            safe_applicant = japanese_to_english.convert(applicant)
            assessment += f"   - {safe_applicant}: {count} applications ({percentage:.1f}%)\n"
        
        # Year with highest activity
        if len(yearly_totals) > 0:
            max_year = yearly_totals.idxmax()
            max_count = yearly_totals[max_year]
            assessment += f"\n3. Peak Activity: The highest number of patent applications ({max_count}) was in {max_year}.\n"
        
        # Applicant diversification
        unique_applicants_by_year = df.groupby("Year")["Applicant"].nunique()
        if len(unique_applicants_by_year) >= 2:
            first_year_diversity = unique_applicants_by_year.get(first_year, 0)
            last_year_diversity = unique_applicants_by_year.get(last_year, 0)
            
            if last_year_diversity > first_year_diversity:
                diversity_trend = "increased"
            elif last_year_diversity < first_year_diversity:
                diversity_trend = "decreased"
            else:
                diversity_trend = "remained stable"
                
            assessment += f"\n4. Applicant Diversification: The number of active applicants has {diversity_trend} "
            assessment += f"from {first_year_diversity} in {first_year} to {last_year_diversity} in {last_year}.\n"
        
        return assessment
        
    except Exception as e:
        logger.error(f"Error generating classification assessment: {e}")
        return f"Unable to generate assessment due to an error: {str(e)}"

def get_ipc_class_description(class_code):
    """Get description for IPC class code"""
    ipc_descriptions = {
        'A': 'Human Necessities',
        'B': 'Performing Operations; Transporting',
        'C': 'Chemistry; Metallurgy',
        'D': 'Textiles; Paper',
        'E': 'Fixed Constructions',
        'F': 'Mechanical Engineering; Lighting; Heating; Weapons; Blasting',
        'G': 'Physics',
        'H': 'Electricity',
        'Unclassified': 'Unclassified'
    }
    return ipc_descriptions.get(class_code, 'Unknown')

# Root endpoint for basic API info
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Patent Classification Trend Analysis API",
        "version": "1.0.0",
        "endpoints": [
            "/health", 
            "/analyze", 
            "/analyze_pdf",
            "/analyze_classification",
            "/analyze_classification_pdf"
        ]
    }

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Basic check - in a real app, you might want to verify DB connection, etc.
        return {"status": "healthy", "message": "Trend analysis service is operational"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def create_pdf_report(title: str, assessment: str, chart_image_base64: str) -> bytes:
    """Create a PDF report with assessment and chart"""
    # Initialize PDF object
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    pdf.cell(0, 10, title, 0, 1, 'C')
    
    # Date
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'R')
    
    # Assessment
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Assessment:', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    # Split assessment into lines and add to PDF
    for line in assessment.split('\n'):
        pdf.multi_cell(0, 6, line)
    
    # Add some space
    pdf.ln(10)
    
    # Add chart
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Patent Trend Visualization:', 0, 1)
    
    # Decode base64 image
    img_data = base64.b64decode(chart_image_base64)
    
    # Create temp image file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_file.write(img_data)
        temp_file_path = temp_file.name
    
    # Add image to PDF
    try:
        pdf.image(temp_file_path, x=10, y=None, w=180)
    except Exception as e:
        logger.error(f"Failed to add image to PDF: {e}")
    
    # Clean up temp file
    try:
        os.unlink(temp_file_path)
    except Exception as e:
        logger.warning(f"Could not delete temp file {temp_file_path}: {e}")
    
    # Add footer
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'Patent trend analysis powered by AI Integrated Search MCP', 0, 0, 'C')
    
    # Get PDF as bytes
    return pdf.output(dest='S').encode('latin-1')

# Applicant-based endpoints
@app.post("/analyze", response_model=PatentTrendResponse)
async def analyze(request: PatentTrendRequest):
    """Analyze patent trends by classification and year for a given applicant"""
    try:
        logger.info(f"Analyzing trends for applicant: {request.applicant_name}")
        
        # Get data from database API (SQLite)
        yearly_classification_counts = analyze_patent_trends(
            request.applicant_name,
            request.start_year,
            request.end_year
        )
        
        # Generate chart
        chart_image = generate_trend_chart(request.applicant_name, yearly_classification_counts)
        
        # Generate assessment
        assessment = generate_assessment(request.applicant_name, yearly_classification_counts)
        
        # Prepare response
        response = PatentTrendResponse(
            applicant_name=request.applicant_name,
            yearly_classification_counts=yearly_classification_counts,
            chart_image=chart_image,
            assessment=assessment
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_pdf")
async def analyze_pdf(request: PatentTrendRequest):
    """Analyze patent trends and return a PDF report"""
    try:
        logger.info(f"Analyzing trends for PDF report: {request.applicant_name}")
        
        # Get data from database API
        yearly_classification_counts = analyze_patent_trends(
            request.applicant_name,
            request.start_year,
            request.end_year
        )
        
        # Generate chart
        chart_image = generate_trend_chart(request.applicant_name, yearly_classification_counts)
        
        # Generate assessment
        assessment = generate_assessment(request.applicant_name, yearly_classification_counts)
        
        # Create PDF title
        safe_applicant = japanese_to_english.convert(request.applicant_name)
        title = f'Patent Analysis Report: {safe_applicant}'
        
        # Create PDF report
        pdf_bytes = create_pdf_report(
            title,
            assessment,
            chart_image
        )
        
        # Create safe filename
        safe_name = safe_applicant.replace(' ', '_')
        filename = f"{safe_name}_patent_analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error processing PDF request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Classification-based endpoints
@app.post("/analyze_classification", response_model=ClassificationTrendResponse)
async def analyze_classification(request: ClassificationTrendRequest):
    """Analyze patent trends by applicant and year for a given classification code"""
    try:
        logger.info(f"Analyzing trends for classification: {request.classification_code}")
        
        # Get data from database API
        yearly_applicant_counts = analyze_classification_trends(
            request.classification_code,
            request.start_year,
            request.end_year
        )
        
        # Generate chart
        chart_image = generate_classification_chart(request.classification_code, yearly_applicant_counts)
        
        # Generate assessment
        assessment = generate_classification_assessment(request.classification_code, yearly_applicant_counts)
        
        # Prepare response
        response = ClassificationTrendResponse(
            classification_code=request.classification_code,
            yearly_applicant_counts=yearly_applicant_counts,
            chart_image=chart_image,
            assessment=assessment
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing classification request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_classification_pdf")
async def analyze_classification_pdf(request: ClassificationTrendRequest):
    """Analyze classification trends and return a PDF report"""
    try:
        logger.info(f"Analyzing trends for PDF report, classification: {request.classification_code}")
        
        # Get data from database API
        yearly_applicant_counts = analyze_classification_trends(
            request.classification_code,
            request.start_year,
            request.end_year
        )
        
        # Generate chart
        chart_image = generate_classification_chart(request.classification_code, yearly_applicant_counts)
        
        # Generate assessment
        assessment = generate_classification_assessment(request.classification_code, yearly_applicant_counts)
        
        # Get class description for the title
        class_description = get_ipc_class_description(request.classification_code)
        title = f'Patent Analysis Report: Class {request.classification_code} ({class_description})'
        
        # Create PDF report
        pdf_bytes = create_pdf_report(
            title,
            assessment,
            chart_image
        )
        
        # Create safe filename
        filename = f"Class_{request.classification_code}_analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error processing classification PDF request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
