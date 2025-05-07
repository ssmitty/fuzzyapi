
import requests


import pandas as pd

def test_company_matcher():
    """Test the company matcher API"""
    print("Starting tests...")
    base_url = "http://127.0.0.1:8080"
    
    try:
        # Test 1: Home page loads
        print("\nTest 1: Testing home page load...")
        response = requests.get(base_url)
        if response.status_code != 200:
            raise Exception(f"Home page failed to load: {response.status_code}")
        if "Company Matcher" not in response.text:
            raise Exception("Home page title not found")
        print("✓ Home page loads correctly")
        
        # Test 2: Valid company name
        print("\nTest 2: Testing valid company name...")
        response = requests.post(base_url, data={"name": "Target Corporation"})
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        if "Target" not in response.text:
            raise Exception("Company match not found")
        if "Ticker Match Score" not in response.text:
            raise Exception("Ticker match score not found")
        print("✓ Valid company name test passed")
        
        # Test 3: Invalid input
        print("\nTest 3: Testing invalid input...")
        response = requests.post(base_url, data={"name": "!@#$%^"})
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        if "Company Match Score" not in response.text:
            raise Exception("Score not found for invalid input")
        print("✓ Invalid input test passed")
        
        print("\nAll tests passed! ")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Test failed: Could not connect to the server. Make sure it's running on port 8080.")

if __name__ == "__main__":
    test_company_matcher() 