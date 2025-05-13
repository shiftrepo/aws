#!/usr/bin/env python3
import requests
import json
import sys

def query_database(classification_code="G", start_year=2010, end_year=2023):
    """Send a direct query to the database API for classification analysis"""
    
    # Build the SQL query
    query = f"""
    SELECT 
        substr(filing_date, 1, 4) as year,
        assignee_original as applicant_name,
        COUNT(*) as application_count
    FROM 
        publications
    WHERE 
        substr(ipc_code, 1, 1) = '{classification_code}'
        AND substr(filing_date, 1, 4) >= '{start_year}'
        AND substr(filing_date, 1, 4) <= '{end_year}'
    GROUP BY 
        substr(filing_date, 1, 4), 
        assignee_original
    ORDER BY 
        substr(filing_date, 1, 4), 
        COUNT(*) DESC
    """
    
    # Send query to database API
    try:
        db_url = "http://localhost:5003"
        response = requests.post(
            f"{db_url}/execute/bigquery",
            json={"query": query}
        )
        
        # Save raw response to file
        with open('db_query_response.json', 'w') as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)
        
        print(f"Saved raw database response to db_query_response.json")
        
        return response.json()
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    # Run the query and get results
    result = query_database()
    
    # Save top 5 applicants per year to a summary file
    if result and 'rows' in result:
        yearly_data = {}
        
        # Group by year
        for row in result['rows']:
            year = str(row.get('year', 'Unknown'))
            applicant = row.get('applicant_name', 'Unknown')
            count = row.get('application_count', 0)
            
            if year not in yearly_data:
                yearly_data[year] = []
                
            yearly_data[year].append({
                'applicant': applicant,
                'count': count
            })
        
        # Create summary with top 5 per year
        summary = {}
        for year, applicants in yearly_data.items():
            # Sort by count descending
            sorted_applicants = sorted(applicants, key=lambda x: x['count'], reverse=True)
            # Get top 5
            top5 = sorted_applicants[:5]
            summary[year] = top5
        
        # Save summary to file
        with open('classification_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        print(f"Saved summary to classification_summary.json")
