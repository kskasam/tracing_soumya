#!/usr/bin/env python3
"""
Run the interactive tracing tool as a local web server.

Usage:
    python3 tools/run_trace_tool.py
    
Then open your browser to:
    http://localhost:8000/tools/interactive_trace_tool.html
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

PORT = 8000

def find_free_port(start_port=8000, max_attempts=10):
    """Find a free port starting from start_port."""
    import socket
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Handle requests for Telugu letter files
        if self.path.startswith('/lib/assets/phontics_assets_points/telugu_phontics/'):
            file_path = self.path[1:]  # Remove leading /
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
        
        if self.path.startswith('/lib/src/phontics_constants/telugu_shape_paths.dart'):
            file_path = self.path[1:]
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
        
        # Default behavior for other files
        super().do_GET()

def main():
    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # Find a free port
    actual_port = find_free_port(PORT)
    if actual_port is None:
        print("Error: Could not find a free port. Please close other servers.")
        sys.exit(1)
    
    Handler = CustomHTTPRequestHandler
    
    with socketserver.TCPServer(("", actual_port), Handler) as httpd:
        url = f"http://localhost:{actual_port}/tools/telugu_stroke_editor.html"
        url_old = f"http://localhost:{actual_port}/tools/interactive_trace_tool.html"
        print("="*80)
        print("Telugu Stroke Editor Tools")
        print("="*80)
        print("\nTwo tools available:")
        if actual_port != PORT:
            print(f"\n⚠️  Port {PORT} was in use. Using port {actual_port} instead.")
        print(f"\nServer starting on port {actual_port}...")
        print(f"\n1. NEW IMPROVED TOOL (Recommended):")
        print(f"   {url}")
        print(f"\n2. Original Tool:")
        print(f"   {url_old}")
        print("\nPress Ctrl+C to stop the server")
        print("="*80)
        
        # Try to open browser automatically
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")

if __name__ == '__main__':
    main()

