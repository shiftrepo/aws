#!/usr/bin/env python3

import requests
import json
import sys
import time

def test_jplatpat_import(base_url="http://localhost:5000"):
    """
    Test the J-PlatPat import functionality
    
    Args:
        base_url: Base URL of the patent-sqlite API service
    """
    print("Testing J-PlatPat import functionality...")
    
    # First, check server status
    try:
        status_url = f"{base_url}/status"
        status_response = requests.get(status_url)
        status_response.raise_for_status()
        status_data = status_response.json()
        
        print(f"Server status: {json.dumps(status_data, indent=2)}")
        print(f"Current patent count: {status_data.get('patent_count', 0)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {str(e)}")
        print("Make sure the patent-sqlite service is running")
        return False
    
    # Define search parameters for J-PlatPat import
    search_params = {
        "company": "トヨタ自動車",  # Toyota Motor Corporation
        "limit": 5  # Limit to 5 patents for testing
    }
    
    print(f"\nImporting patents from J-PlatPat for company: {search_params['company']}")
    
    try:
        import_url = f"{base_url}/import-jplatpat"
        import_response = requests.post(
            import_url, 
            json=search_params,
            headers={"Content-Type": "application/json"}
        )
        
        import_response.raise_for_status()
        import_data = import_response.json()
        
        print("J-PlatPat import successful!")
        print(f"Response message: {import_data.get('message', '')}")
        
        results = import_data.get("results", {})
        patents_found = results.get("patents_found", 0)
        patents_imported = results.get("patents_imported", 0)
        patents_updated = results.get("patents_updated", 0)
        
        print(f"Patents found: {patents_found}")
        print(f"Patents imported: {patents_imported}")
        print(f"Patents updated: {patents_updated}")
        
        # Display sample patents if available
        sample_patents = results.get("sample_patents", [])
        if sample_patents:
            print("\nSample imported patents:")
            for i, patent in enumerate(sample_patents, 1):
                print(f"Patent {i}:")
                print(f"  Title: {patent.get('title', 'N/A')}")
                print(f"  Applicant: {patent.get('applicant', 'N/A')}")
                print(f"  Publication Number: {patent.get('publication_number', 'N/A')}")
                print(f"  Filing Date: {patent.get('filing_date', 'N/A')}")
                print()
        
        # Check updated status
        time.sleep(1)  # Wait a moment for database to update
        status_response = requests.get(status_url)
        status_response.raise_for_status()
        status_data = status_response.json()
        
        print(f"Updated patent count: {status_data.get('patent_count', 0)}")
        
        # Try another search with different parameters
        keyword_search = {
            "keyword": "人工知能",  # "Artificial Intelligence" in Japanese
            "limit": 3
        }
        
        print(f"\nImporting patents from J-PlatPat with keyword (fuzzy search): {keyword_search['keyword']}")
        print("(注: キーワード検索は曖昧検索に対応しており、「人工知能システム」や「次世代人工知能」などの部分一致も検索できます)")
        
        import_response = requests.post(
            import_url, 
            json=keyword_search,
            headers={"Content-Type": "application/json"}
        )
        
        import_response.raise_for_status()
        import_data = import_response.json()
        
        print("J-PlatPat keyword import successful!")
        print(f"Response message: {import_data.get('message', '')}")
        
        results = import_data.get("results", {})
        patents_found = results.get("patents_found", 0)
        patents_imported = results.get("patents_imported", 0)
        patents_updated = results.get("patents_updated", 0)
        
        print(f"Patents found: {patents_found}")
        print(f"Patents imported: {patents_imported}")
        print(f"Patents updated: {patents_updated}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error during import: {str(e)}")
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
        
        return False


if __name__ == "__main__":
    # Get base URL from command line if provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"Using API base URL: {base_url}")
    success = test_jplatpat_import(base_url)
    
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")
        sys.exit(1)
