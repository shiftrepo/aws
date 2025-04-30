#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patent Report Generator Script
This script generates various patent analysis reports using SQLite data
"""

import os
import json
import sys
import datetime
from pathlib import Path

# Add the project root to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Importing patent analysis modules...")
from app.patent_system.patent_analyzer_inpit import PatentAnalyzerInpit
from app.patent_system.inpit_sqlite_connector import get_connector

def save_report_to_file(content, filename):
    """Save report content to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Report saved to {filename}")

def main():
    """Generate various patent analysis reports"""
    # Initialize the analyzer with the API URL
    api_url = os.environ.get("INPIT_API_URL", "http://localhost:5001")
    print(f"Connecting to Inpit SQLite API at {api_url}...")
    analyzer = PatentAnalyzerInpit(api_url)
    connector = get_connector(api_url)
    
    # Check database connection
    status = connector.get_api_status()
    print(f"Database status: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # Get basic patent statistics
    print("\nGenerating basic patent statistics...")
    stats_query = """
    SELECT 
        COUNT(*) as total_patents,
        COUNT(DISTINCT 出願人) as unique_applicants,
        COUNT(DISTINCT 国際特許分類) as unique_ipc,
        MIN(出願日) as earliest_date,
        MAX(出願日) as latest_date
    FROM inpit_data
    WHERE 出願日 IS NOT NULL
    """
    stats_result = connector.execute_sql_query(stats_query)
    print(f"Patent statistics: {json.dumps(stats_result, indent=2, ensure_ascii=False)}")
    
    # 1. Generate technology trends report
    print("\nGenerating technology trends report...")
    trends_result = analyzer.analyze_technology_trends(years=10, top_n=10)
    save_report_to_file(json.dumps(trends_result, indent=2, ensure_ascii=False), 'technology_trends.json')
    
    # 2. Generate applicant competition analysis
    print("\nGenerating applicant competition analysis...")
    competition_result = analyzer.analyze_applicant_competition(top_n=10)
    save_report_to_file(json.dumps(competition_result, indent=2, ensure_ascii=False), 'applicant_competition.json')
    
    # 3. Generate patent landscape report
    print("\nGenerating patent landscape report...")
    landscape_result = analyzer.analyze_patent_landscape(ipc_level=3)
    save_report_to_file(json.dumps(landscape_result, indent=2, ensure_ascii=False), 'patent_landscape.json')
    
    # 4. Generate comprehensive analysis report
    print("\nGenerating comprehensive analysis report...")
    today = datetime.datetime.now().strftime("%Y%m%d")
    report = analyzer.generate_analysis_report()
    save_report_to_file(report, f'patent_analysis_report_{today}.md')
    
    print("\nAll reports generated successfully!")
    print("\nGenerated files:")
    print("  - technology_trends.json")
    print("  - applicant_competition.json")
    print("  - patent_landscape.json")
    print(f"  - patent_analysis_report_{today}.md")

if __name__ == "__main__":
    main()
