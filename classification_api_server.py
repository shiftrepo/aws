#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
import requests
import json

# Setup FastAPI app
app = FastAPI(
    title="Classification Analysis API",
    description="API for patent classification trend analysis",
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

class ClassificationTrendRequest(BaseModel):
    classification_code: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None

class ClassificationTrendResponse(BaseModel):
    classification_code: str
    yearly_applicant_counts: Dict[str, Dict[str, int]]
    assessment: str

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

def query_database(classification_code, start_year=None, end_year=None):
    """Query the database API for patent classification data"""
    # Build the SQL query
    where_clauses = [f"substr(ipc_code, 1, 1) = '{classification_code}'"]
    
    if start_year:
        where_clauses.append(f"substr(filing_date, 1, 4) >= '{start_year}'")
    
    if end_year:
        where_clauses.append(f"substr(filing_date, 1, 4) <= '{end_year}'")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
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
        # Send query to database API
        db_url = "http://localhost:5003"
        response = requests.post(
            f"{db_url}/execute/bigquery",
            json={"query": query}
        )
        
        if response.status_code != 200:
            raise Exception(f"Database API error: {response.status_code}, {response.text}")
        
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
            
            # Only keep top 5 applicants per year to prevent cluttering
            if len(yearly_applicant_counts[year]) < 5:
                yearly_applicant_counts[year][applicant] = application_count
        
        return yearly_applicant_counts
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying classification data: {e}")

def analyze_classification_data(classification_code, yearly_applicant_counts):
    """Generate assessment for classification trend data"""
    class_description = get_ipc_class_description(classification_code)
    
    try:
        # Convert to a structure for analysis
        data = []
        for year, applicants in yearly_applicant_counts.items():
            year_total = sum(applicants.values())
            for applicant, count in applicants.items():
                data.append({
                    "year": int(year), 
                    "applicant": applicant, 
                    "count": count,
                    "year_total": year_total
                })
        
        # Calculate total patents by year
        yearly_totals = {}
        for item in data:
            year = item["year"]
            if year not in yearly_totals:
                yearly_totals[year] = 0
            yearly_totals[year] += item["count"]
        
        # Calculate growth trend
        if len(yearly_totals) >= 2:
            years = sorted(yearly_totals.keys())
            first_year = years[0]
            last_year = years[-1]
            
            first_count = yearly_totals[first_year]
            last_count = yearly_totals[last_year]
            
            if first_count > 0:
                percent_change = ((last_count - first_count) / first_count * 100)
                
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
                trend_direction = "undetermined (initial count was zero)"
        else:
            trend_direction = "unknown (insufficient data)"
            first_year = "unknown"
            last_year = "unknown"
            percent_change = 0
            
        # Find dominant applicants
        applicant_totals = {}
        for item in data:
            applicant = item["applicant"]
            count = item["count"]
            
            if applicant not in applicant_totals:
                applicant_totals[applicant] = 0
            
            applicant_totals[applicant] += count
            
        # Sort applicants by total count
        sorted_applicants = sorted(applicant_totals.items(), key=lambda x: x[1], reverse=True)
        top_applicants = sorted_applicants[:5]
        
        # Build assessment text
        assessment = f"Assessment for IPC Class {classification_code} ({class_description}):\n\n"
        
        # Overall trend
        if len(yearly_totals) >= 2:
            assessment += f"1. Overall Trend: Patent applications in Class {classification_code} are {trend_direction} "
            assessment += f"from {first_year} ({yearly_totals[first_year]} applications) to {last_year} ({yearly_totals[last_year]} applications)"
            assessment += f", which represents a {abs(percent_change):.1f}% {'increase' if percent_change > 0 else 'decrease'}.\n\n"
        else:
            assessment += f"1. Overall Trend: Insufficient data to determine trend for Class {classification_code}.\n\n"
            
        # Top applicants
        assessment += "2. Top Applicants in this Classification:\n"
        for i, (applicant, count) in enumerate(top_applicants, 1):
            percentage = (count / sum(applicant_totals.values())) * 100
            assessment += f"   - {applicant}: {count} applications ({percentage:.1f}%)\n"
            
        # Year with highest activity
        if yearly_totals:
            max_year = max(yearly_totals.items(), key=lambda x: x[1])[0]
            max_count = yearly_totals[max_year]
            assessment += f"\n3. Peak Activity: The highest number of patent applications ({max_count}) was in {max_year}.\n"
            
        # Market competition assessment
        if len(applicant_totals) > 1:
            top_applicant_count = top_applicants[0][1]
            total_count = sum(applicant_totals.values())
            top_applicant_share = (top_applicant_count / total_count) * 100
            
            if top_applicant_share > 50:
                competition = "dominated by a single applicant"
            elif top_applicant_share > 30:
                competition = "led by one major applicant with significant competition"
            else:
                competition = "highly competitive with multiple active applicants"
                
            assessment += f"\n4. Market Dynamics: The {classification_code} classification field is {competition}.\n"
            
        # Yearly activity trend
        if len(yearly_totals) > 2:
            recent_years = sorted(yearly_totals.keys())[-3:]
            recent_trend = []
            
            for i in range(len(recent_years)-1):
                curr_year = recent_years[i]
                next_year = recent_years[i+1]
                
                if yearly_totals[next_year] > yearly_totals[curr_year]:
                    recent_trend.append("up")
                elif yearly_totals[next_year] < yearly_totals[curr_year]:
                    recent_trend.append("down")
                else:
                    recent_trend.append("stable")
            
            if all(direction == "up" for direction in recent_trend):
                recent_trend_desc = "consistently increasing"
            elif all(direction == "down" for direction in recent_trend):
                recent_trend_desc = "consistently decreasing"
            else:
                recent_trend_desc = "fluctuating"
                
            assessment += f"\n5. Recent Activity: Patent applications in the most recent years show a {recent_trend_desc} trend.\n"
            
        return assessment
            
    except Exception as e:
        return f"Error generating assessment: {e}"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Classification analysis API is operational"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Classification Analysis API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/analyze_classification"
        ]
    }

@app.post("/analyze_classification", response_model=ClassificationTrendResponse)
async def analyze_classification(request: ClassificationTrendRequest):
    """
    Analyze patent trends by applicant and year for a given classification code
    
    - **classification_code**: IPC classification code (e.g. 'G' for Physics)
    - **start_year**: Optional starting year for the analysis
    - **end_year**: Optional ending year for the analysis
    """
    try:
        # Query database for classification data
        yearly_applicant_counts = query_database(
            request.classification_code,
            request.start_year,
            request.end_year
        )
        
        # Generate assessment
        assessment = analyze_classification_data(
            request.classification_code, 
            yearly_applicant_counts
        )
        
        # Return response
        return ClassificationTrendResponse(
            classification_code=request.classification_code,
            yearly_applicant_counts=yearly_applicant_counts,
            assessment=assessment
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the API server on port 5006
    uvicorn.run(app, host="0.0.0.0", port=5006)
