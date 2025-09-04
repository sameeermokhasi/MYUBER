#!/usr/bin/env python3
"""
Simple client for MYUBER project
Uses only built-in Python libraries to avoid dependency issues
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

class SimpleMYUBERClient:
    """Simple client for MYUBER API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        if data:
            data_bytes = json.dumps(data).encode('utf-8')
        else:
            data_bytes = None
        
        # Create request
        req = urllib.request.Request(
            url,
            data=data_bytes,
            method=method,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MYUBER-Simple-Client/1.0.0'
            }
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            try:
                return json.loads(error_data)
            except:
                return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}
    
    def ping(self, data: str = "ping") -> dict:
        """Send ping request"""
        return self.make_request("POST", "/api/v1/ping", {"data": data})
    
    def health_check(self) -> dict:
        """Check server health"""
        return self.make_request("GET", "/health")
    
    def get_root(self) -> dict:
        """Get root endpoint"""
        return self.make_request("GET", "/")

    def submit_ride_request(self, source_location: str, dest_location: str, user_id: str) -> dict:
        """Submit a ride request to the server"""
        payload = {
            "source_location": source_location,
            "dest_location": dest_location,
            "user_id": user_id
        }
        return self.make_request("POST", "/api/v1/ride_request", payload)

def main():
    """Main function to demonstrate client usage"""
    client = SimpleMYUBERClient()
    
    print("=== MYUBER Simple Client Demo ===")
    
    # Health check
    print("\n1. Checking server health...")
    health = client.health_check()
    print(f"Health status: {health}")
    
    # Root endpoint
    print("\n2. Getting root endpoint...")
    root = client.get_root()
    print(f"Root response: {root}")
    
    # Ping test
    print("\n3. Sending ping request...")
    ping_response = client.ping("ping")
    print(f"Ping response: {ping_response}")
    
    # Ride request demo
    print("\n4. Submitting ride request...")
    ride = client.submit_ride_request(
        source_location="12.9716,77.5946",
        dest_location="12.2958,76.6394",
        user_id="user_123"
    )
    print(f"Ride request response: {ride}")

if __name__ == "__main__":
    main()

