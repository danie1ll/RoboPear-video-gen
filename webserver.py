import http.server
import socketserver
import os

# Set the directory containing your static files
DIRECTORY = "./generatedWebsites"

# Change the working directory to the static files directory
os.chdir(DIRECTORY)

# Set the port for the server
PORT = 8000

# Create a handler for serving static files
handler = http.server.SimpleHTTPRequestHandler

# Create a socket server with the handler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at port {PORT}")
    print(f"Serving files from directory: {DIRECTORY}")
    
    # Start the server
    httpd.serve_forever()