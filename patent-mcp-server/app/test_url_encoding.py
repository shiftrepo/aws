#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for validating URL encoding with Japanese applicant names in the Patent API
"""

import requests
import urllib.parse
import sys

def test_applicant_endpoint(applicant_name):
    """Test the /applicant/{applicant_name} endpoint with proper URL encoding"""
    base_url = "http://localhost:8000"
    
    # URL encode the applicant name
    encoded_name = urllib.parse.quote(applicant_name)
    
    # Original URL (will fail for non-ASCII characters)
    original_url = f"{base_url}/applicant/{applicant_name}"
    
    # Properly encoded URL
    encoded_url = f"{base_url}/applicant/{encoded_name}"
    
    print(f"Testing with applicant name: {applicant_name}")
    print(f"URL encoded as: {encoded_name}")
    
    # Test with unencoded URL (expected to fail for non-ASCII)
    print("\n1. Testing with unencoded URL (should fail for non-ASCII):")
    print(f"   URL: {original_url}")
    try:
        response = requests.get(original_url, timeout=5)
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.text[:100]}..." if len(response.text) > 100 else f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
    
    # Test with properly encoded URL (should work)
    print("\n2. Testing with properly encoded URL (should succeed):")
    print(f"   URL: {encoded_url}")
    try:
        response = requests.get(encoded_url, timeout=5)
        print(f"   Status code: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Success! The encoded URL works correctly.")
            print(f"   Response: {response.text[:100]}..." if len(response.text) > 100 else f"   Response: {response.text}")
        else:
            print("   ✗ Failed! The encoded URL returned an error.")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
    
    # Generate equivalent curl command
    print("\n3. Equivalent curl command (for manual testing):")
    print(f'   curl "{encoded_url}"')

def main():
    print("=" * 60)
    print("Patent API URL Encoding Test")
    print("=" * 60)
    
    # Default test applicant
    test_applicant = "テック株式会社"
    
    # Allow command-line argument to override
    if len(sys.argv) > 1:
        test_applicant = sys.argv[1]
    
    test_applicant_endpoint(test_applicant)
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
    
    print("\nSummary:")
    print("1. For non-ASCII characters (like Japanese), direct URL usage will fail")
    print("2. Properly encoded URLs should work correctly")
    print("3. Always encode non-ASCII characters in URLs using urllib.parse.quote() or equivalent")

if __name__ == "__main__":
    main()
