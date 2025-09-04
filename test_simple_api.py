#!/usr/bin/env python3
"""
Test script for simple MYUBER API
"""

import json
import urllib.request
import urllib.parse

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("=== Testing Simple MYUBER API ===")
    
    # Test 1: Root endpoint (GET)
    print("\n1. Testing root endpoint (GET)...")
    try:
        req = urllib.request.Request(f"{base_url}/")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Status: {response.status}")
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Health check (GET)
    print("\n2. Testing health check (GET)...")
    try:
        req = urllib.request.Request(f"{base_url}/health")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Status: {response.status}")
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Ping endpoint (POST) - Valid
    print("\n3. Testing ping endpoint (POST) - Valid...")
    try:
        data = {"data": "ping"}
        data_bytes = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            f"{base_url}/api/v1/ping",
            data=data_bytes,
            method="POST",
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Status: {response.status}")
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Ping endpoint (POST) - Invalid
    print("\n4. Testing ping endpoint (POST) - Invalid...")
    try:
        data = {"data": "invalid"}
        data_bytes = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            f"{base_url}/api/v1/ping",
            data=data_bytes,
            method="POST",
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Status: {response.status}")
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()


