#!/usr/bin/env python3
"""
Run the Centerline Generator HTML tool.
This starts a local HTTP server to serve the centerline editor.
"""

import http.server
import socketserver
import webbrowser
import os
import socket
from pathlib import Path

DEFAULT_PORT = 8002

def find_free_port(start_port):
    """Find an available port starting from start_port."""
    port = start_port
    while port < start_port + 100:  # Try up to 100 ports
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError("Could not find an available port")

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        workspace = Path(__file__).parent.parent.parent
        super().__init__(*args, directory=str(workspace), **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow loading JSON files
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Override to show requests in console
        print(f"📥 {args[0]}")

def main():
    # Get the workspace directory (flutter_tracing folder)
    workspace = Path(__file__).parent.parent.parent
    os.chdir(workspace)
    
    # Verify the HTML file exists
    html_file = workspace / 'tools' / 'center_line_generator' / 'centerline_editor.html'
    if not html_file.exists():
        print(f"❌ Error: HTML file not found at {html_file}")
        return 1
    
    print(f"✅ Found HTML file at: {html_file}")
    print(f"📁 Serving from: {workspace}\n")
    
    # Find an available port
    port = find_free_port(DEFAULT_PORT)
    if port != DEFAULT_PORT:
        print(f"⚠️  Port {DEFAULT_PORT} is in use, using port {port} instead")
    
    try:
        with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
            url = f"http://localhost:{port}/tools/center_line_generator/centerline_editor.html"
            print(f"🚀 Starting Centerline Generator...")
            print(f"📝 Open your browser to: {url}")
            print(f"🛑 Press Ctrl+C to stop the server\n")
            
            # Try to open browser automatically
            try:
                webbrowser.open(url)
            except:
                pass
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n\n👋 Server stopped. Goodbye!")
    except OSError as e:
        print(f"❌ Error starting server: {e}")
        print(f"💡 Try killing any process using port {port} with: lsof -ti:{port} | xargs kill")
        return 1
    
    return 0

if __name__ == '__main__':
    main()

