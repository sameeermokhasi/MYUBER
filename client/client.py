import requests
import json
from typing import Dict, Any

class MYUBERClient:
    """Client for MYUBER API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "MYUBER-Client/1.0.0"
        })
    
    def ping(self, data: str = "ping") -> Dict[str, Any]:
        """
        Send ping request to the server
        
        Args:
            data: The data to send (default: "ping")
            
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/api/v1/ping"
        payload = {"data": data}
        
        try:
            # Intentional bug: incorrect URL construction
            # Should be: f"{self.base_url}/api/v1/ping"
            # But it's: f"{self.base_url}/api/v1/ping/" (extra slash)
            response = self.session.post(f"{self.base_url}/api/v1/ping/", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking health: {e}")
            return {"error": str(e)}

def main():
    """Main function to demonstrate client usage"""
    client = MYUBERClient()
    
    print("=== MYUBER Client Demo ===")
    
    # Health check
    print("\n1. Checking server health...")
    health = client.health_check()
    print(f"Health status: {health}")
    
    # Ping test
    print("\n2. Sending ping request...")
    ping_response = client.ping("ping")
    print(f"Ping response: {ping_response}")
    
    # Invalid ping test
    print("\n3. Sending invalid ping request...")
    invalid_response = client.ping("invalid")
    print(f"Invalid ping response: {invalid_response}")

if __name__ == "__main__":
    main()

