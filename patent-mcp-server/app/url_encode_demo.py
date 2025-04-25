#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
URL Encoding Demo for Patent API

This script demonstrates how to properly URL encode non-ASCII characters
when making requests to the Patent API, especially for Japanese applicant names.
"""

import requests
import urllib.parse
import json
from typing import Dict, Any


def get_applicant_summary(base_url: str, applicant_name: str) -> Dict[str, Any]:
    """
    Get a summary for the specified applicant with proper URL encoding.
    
    Args:
        base_url (str): Base URL of the patent API (e.g., 'http://localhost:8000')
        applicant_name (str): Name of the applicant, can contain non-ASCII characters
        
    Returns:
        dict: JSON response from the API
    """
    # URL encode the applicant name
    encoded_name = urllib.parse.quote(applicant_name)
    
    # Construct the URL
    url = f"{base_url}/applicant/{encoded_name}"
    
    # Print debugging info
    print(f"Original applicant name: {applicant_name}")
    print(f"URL encoded name: {encoded_name}")
    print(f"Full request URL: {url}")
    
    # Make the request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return {"error": str(e)}


def curl_command_example(base_url: str, applicant_name: str) -> str:
    """
    Generate an equivalent curl command with proper URL encoding.
    
    Args:
        base_url (str): Base URL of the patent API
        applicant_name (str): Name of the applicant
        
    Returns:
        str: curl command that can be run from the command line
    """
    encoded_name = urllib.parse.quote(applicant_name)
    return f'curl "{base_url}/applicant/{encoded_name}"'


def main():
    """Main function to demonstrate URL encoding for the Patent API"""
    # Configuration
    BASE_URL = "http://localhost:8000"
    
    # Example Japanese applicant names
    applicants = [
        "テック株式会社",
        "日本特許株式会社",
        "東京電機株式会社",
        "ソフトウェア技術研究所"
    ]
    
    print("=" * 60)
    print("Patent API URL Encoding Demo")
    print("=" * 60)
    
    for applicant in applicants:
        print("\n" + "-" * 60)
        print(f"Testing with applicant: {applicant}")
        
        # Generate and print curl command
        curl_cmd = curl_command_example(BASE_URL, applicant)
        print("\nEquivalent curl command:")
        print(curl_cmd)
        
        # Make the actual request
        print("\nMaking API request...")
        result = get_applicant_summary(BASE_URL, applicant)
        
        # Print condensed result 
        print("\nAPI Response (condensed):")
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            # Just print some key information from the response
            if "applicant_name" in result:
                print(f"Applicant: {result['applicant_name']}")
            if "total_patents" in result:
                print(f"Total Patents: {result['total_patents']}")
            # Print first technical field if available
            if "technical_distribution" in result and result["technical_distribution"]:
                first_field = result["technical_distribution"][0]
                print(f"Top Technical Field: {first_field['field']} - {first_field['description']} ({first_field['percentage']})")
        
        print("-" * 60)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
