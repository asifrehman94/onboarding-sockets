#!/usr/bin/env python3
"""
Simple HTTP server to serve client.html
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8001

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def serve_client():
    """Serve client.html on localhost:8001"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Serving client.html at http://localhost:{PORT}")
        print(f"📱 Open your browser and go to: http://localhost:{PORT}/client.html")
        print("🛑 Press Ctrl+C to stop the server")
        
        try:
            # Auto-open browser
            webbrowser.open(f'http://localhost:{PORT}/client.html')
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    serve_client()
