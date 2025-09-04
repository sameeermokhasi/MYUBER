#!/usr/bin/env python3
"""
Test script for MYUBER API
This script demonstrates how to use the ping endpoint
"""

import requests
import json

def test_ping_endpoint():
    """Test the ping endpoint"""
    base_url = "http://localhost:8000"
    
    print("=== Testing MYUBER API ===")
    
    # Test 1: Valid ping request
    print("\n1. Testing valid ping request...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/ping",
            json={"data": "ping"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Invalid ping request
    print("\n2. Testing invalid ping request...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/ping",
            json={"data": "invalid"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Health check
    print("\n3. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ping_endpoint()


