import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

import requests
import time
import pandas as pd


def test_company_matcher():
    """Test the company matcher API"""
    logging.info("Starting tests...")
    base_url = "http://127.0.0.1:8080"

    try:
        # Test 1: Home page loads
        logging.info("\nTest 1: Testing home page load...")
        response = requests.get(base_url)
        if response.status_code != 200:
            raise Exception(f"Home page failed to load: {response.status_code}")
        if "Company Matcher" not in response.text:
            raise Exception("Home page title not found")
        logging.info("✓ Home page loads correctly")

        # Test 2: Valid company name
        logging.info("\nTest 2: Testing valid company name...")
        start = time.time()
        response = requests.post(base_url, data={"name": "Target Corporation"})
        end = time.time()
        logging.info(f"API Latency: {end - start:.4f} seconds")
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        if "Target" not in response.text:
            raise Exception("Company match not found")
        if "Ticker Match Score" not in response.text:
            raise Exception("Ticker match score not found")
        logging.info("✓ Valid company name test passed")

        # Test 3: Invalid input
        logging.info("\nTest 3: Testing invalid input...")
        response = requests.post(base_url, data={"name": "!@#$%^"})
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        if "Company Match Score" not in response.text:
            raise Exception("Score not found for invalid input")
        logging.info("✓ Invalid input test passed")

        logging.info("\nAll tests passed! ")

    except Exception as e:
        logging.error(f"\n❌ Test failed: {str(e)}")


if __name__ == "__main__":
    test_company_matcher()
