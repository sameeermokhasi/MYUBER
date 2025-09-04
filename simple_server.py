#!/usr/bin/env python3
"""
Simple HTTP server for MYUBER project
Uses only built-in Python libraries to avoid dependency issues
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class MYUBERHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "message": "Welcome to MYUBER API",
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "MYUBER API"
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {"error": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/v1/ping':
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse JSON data
                data = json.loads(post_data.decode('utf-8'))
                
                # Check if data contains "ping"
                if data.get('data') == 'ping':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        "message": "pong",
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    response = {
                        "error": "Invalid data. Expected 'ping'"
                    }
                    self.wfile.write(json.dumps(response).encode())
                    
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {"error": "Invalid JSON"}
                self.wfile.write(json.dumps(response).encode())
                
        elif parsed_path.path == '/api/v1/ride_request':
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse JSON data
                data = json.loads(post_data.decode('utf-8'))

                source_location = data.get('source_location')
                dest_location = data.get('dest_location')
                user_id = data.get('user_id')

                # Basic validation
                missing_fields = [
                    field for field, value in [
                        ('source_location', source_location),
                        ('dest_location', dest_location),
                        ('user_id', user_id)
                    ] if not value
                ]
                if missing_fields:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        "error": "Missing required fields",
                        "missing": missing_fields
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return

                # Here we'd store to Postgres. For now, print and acknowledge.
                print("We will store this data in Postgres now:")
                print(json.dumps({
                    'source_location': source_location,
                    'dest_location': dest_location,
                    'user_id': user_id,
                    'received_at': datetime.now().isoformat()
                }, indent=2))

                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                response = {
                    "message": "ride_request accepted",
                    "status": "queued",
                    "data": {
                        "source_location": source_location,
                        "dest_location": dest_location,
                        "user_id": user_id
                    },
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Invalid JSON"}
                self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {"error": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    """Start the server"""
    PORT = 8000
    HOST = "0.0.0.0"
    
    with socketserver.TCPServer((HOST, PORT), MYUBERHandler) as httpd:
        print(f"MYUBER Server starting on   http://{HOST}:{PORT}")
        print("Available endpoints:")
        print("  GET  /                    - Welcome message")
        print("  GET  /health              - Health check")
        print("  POST /api/v1/ping         - Ping endpoint (send JSON: {\"data\": \"ping\"})")
        print("  POST /api/v1/ride_request - Submit ride request (JSON: {source_location, dest_location, user_id})")
        print("\nPress Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    main()


