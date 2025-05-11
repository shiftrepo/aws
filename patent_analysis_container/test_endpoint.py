import requests
import json
import os
import argparse

def test_endpoint(applicant_name="トヨタ", endpoint_type="tools"):
    """Test the patent analysis endpoint
    
    Args:
        applicant_name: Name of the applicant to analyze
        endpoint_type: Type of endpoint to test ('tools' or 'mcp')
    """
    if endpoint_type == "tools":
        url = "http://localhost:8000/api/tools/execute"
        payload = {
            "tool_name": "analyze_patent_trends",
            "arguments": {
                "applicant_name": applicant_name
            }
        }
    else:  # mcp endpoint
        url = "http://localhost:8000/api/v1/mcp"
        payload = {
            "tool_name": "analyze_patent_trends",
            "tool_input": {
                "applicant_name": applicant_name
            }
        }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing endpoint with applicant: {applicant_name}")
    print(f"Using URL: {url}")
    print(f"Sending payload: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Save response to file
            with open("endpoint_response.json", "w", encoding="utf-8") as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)
            print(f"Response saved to endpoint_response.json")
            
            # Also print to console
            print("Response content:")
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception: {str(e)}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the patent analysis endpoint')
    parser.add_argument('--applicant', '-a', type=str, default='トヨタ', 
                        help='Name of the applicant to analyze')
    parser.add_argument('--endpoint', '-e', type=str, default='tools', choices=['tools', 'mcp'],
                        help='Type of endpoint to test (tools or mcp)')
    
    args = parser.parse_args()
    test_endpoint(applicant_name=args.applicant, endpoint_type=args.endpoint)
