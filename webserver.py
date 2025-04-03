from microdot import Microdot, Response, Request
import time, socket
import wifi
import os, json
import gc
import asyncio
import hashlib
from oled.oledfuncs import oledprint, oledclear

Request.max_content_length = 200 * 1024  # 200KB
# Set a very conservative chunk size for file operations
CHUNK_SIZE = 1 * 1024  # 1KB
# Set the maximum body length for requests to be slightly less than the chunk size, above will be streamed in chunks
Request.max_body_length = CHUNK_SIZE - 1  

async def setup(autoconnect=False):
    if autoconnect:
        print("Attempting to autoconnect to WiFi...")
        oledprint("Attempting to autoconnect to WiFi...")
        await asyncio.sleep(0)  # Allow other tasks to run
        wifi.connect_to_network()
        await asyncio.sleep(1)
    else:
        print("Skipping autoconnect, assuming WiFi is already connected.")
    #check 3 times if the wifi is connected
    for _ in range(3):
        if wifi.wlan_isconnected():
            print("WiFi is connected")
            break
        else:
            print("WiFi is not connected, retrying...")
            await asyncio.sleep(1)
    else:
        print("WiFi is not connected after 3 attempts, shutting down...")
        return False
    
    app = Microdot()
    
    # Force garbage collection before starting server
    print("Freeing memory before starting server...")
    gc.collect()
    free_mem = gc.mem_free() if hasattr(gc, 'mem_free') else "unknown"
    print(f"Free memory: {free_mem}")

    @app.before_request
    async def startTimeMem(request):
        request.g.start_time = time.ticks_ms()
        gc.collect()  # Force garbage collection before request
        request.g.free_mem = gc.mem_free()

    @app.after_request
    async def EndTimeMem(request, response):
        duration = time.ticks_diff(time.ticks_ms(), request.g.start_time)
        memUsed = request.g.free_mem - gc.mem_free()
        gc.collect()  # Force garbage collection after request
        print(f"Request duration: {duration} ms, Memory used: {memUsed} bytes")

    @app.get('/shutdown')
    async def shutdown(request):
        request.app.shutdown()
        print("Shutting down server...")
        return Response("Shutdown initiated.", status_code=200)

    @app.get('/ping')
    async def ping(request):
        return Response("pong", status_code=200, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        })

    # Generate ETag for a file using size and content samples
    def generate_etag(file_path):
        try:
            # Get file size
            stats = os.stat(file_path)
            file_size = stats[6]  # Size is at index 6 in os.stat result
            
            if file_size <= 0:
                return f"sz-{file_size}"
                
            with open(file_path, 'rb') as f:
                # Sample from two positions in the file, but not start/end
                # to reduce predictability and improve uniqueness
                sample_size = min(64, file_size // 4)  # Use up to 64 bytes for sample
                
                # First sample: ~1/3 into the file
                pos1 = max(1, file_size // 3)
                f.seek(pos1)
                sample1 = f.read(sample_size)
                
                # Second sample: ~2/3 into the file
                pos2 = max(pos1 + sample_size, (file_size * 2) // 3)
                f.seek(pos2)
                sample2 = f.read(sample_size)
                
                # Create a simple hash of the samples and file size
                # Using hashlib but with MicroPython-compatible approach
                hasher = hashlib.md5()
                hasher.update(str(file_size).encode())
                hasher.update(sample1)
                hasher.update(sample2)
                
                # Get digest as bytes and convert first 8 bytes to hex
                digest_bytes = hasher.digest()
                etag = ''.join('{:02x}'.format(b) for b in digest_bytes[:4])
                return f'"{etag}"'  # Etags should be quoted
                
        except Exception as e:
            print(f"Error generating ETag: {e}")
            gc.collect()
            # Return None on error rather than a timestamp-based fallback
            return None

    # Build standardized response headers
    def build_response_headers(content_type, etag=None, additional_headers=None):
        """
        Create a dictionary of headers for HTTP responses.
        
        Args:
            content_type (str): MIME type for the Content-Type header
            etag (str, optional): ETag value for caching
            additional_headers (dict, optional): Additional headers to include
            
        Returns:
            dict: Complete set of headers
        """
        # Start with basic headers
        headers = {
            'Content-Type': content_type,
            'Cache-Control': 'no-cache'  # Force revalidation via ETag
        }
        
        # Add ETag only if it's a valid string (not None)
        if etag is not None:
            headers['ETag'] = etag
            
        # Add any additional headers
        if additional_headers:
            headers.update(additional_headers)
            
        return headers

    # More memory efficient reading function - reads line by line instead of whole file
    async def read_html(filename):
        try:
            print(f"Reading file: {filename}")
            content = []
            with open(filename, 'r') as file:
                for line in file:
                    content.append(line)
                    # Force garbage collection periodically
                    if len(content) % 50 == 0:
                        gc.collect()
            return ''.join(content)
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            gc.collect()  # Force GC on error
            return f"Error: {str(e)}"
    
    # Define read_in_chunks function once to avoid duplication
    # Simplified generator loop
    def read_in_chunks(file_path):
        async def generate():
            f = None
            try:
                f = open(file_path, 'rb')
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    # Ensure chunk is bytes (already handled by 'rb' mode, but safe check)
                    if not isinstance(chunk, bytes):
                        chunk = bytes(chunk) # Should not happen with 'rb'
                    yield chunk
            except Exception as e:
                print(f"Error reading file in chunks: {e}")
                gc.collect() # Collect garbage on error
                yield b''
            finally:
                if f:
                    try:
                        f.close()
                    except Exception as close_e:
                        print(f"Error closing file {file_path}: {close_e}")
                gc.collect() # Collect garbage after finishing or error

        return generate()

    @app.route('/', methods=['GET'])
    async def index(request):
        try:
            print("Serving index.html...")
            html_content = await read_html('webpage/index.html')
            # Add a data attribute to the body tag to indicate the page is served from ESP32
            html_content = html_content.replace('<body>', '<body data-esp-mode="true">')
            
            # # Force garbage collection before sending response
            # gc.collect()
            # free_mem = gc.mem_free() if hasattr(gc, 'mem_free') else "unknown"
            # print(f"Free memory before sending index.html: {free_mem}")
            
            return Response(html_content, headers={'Content-Type': 'text/html'})
        except Exception as e:
            print(f"Error serving index.html: {e}")
            gc.collect()
            return f"Error: {str(e)}"
    
    
    @app.route('/list-command', methods=['GET'])
    async def list_command(request):
        dirs = ['thumbnails', 'bins']
        files = [[], []]
        try:
            files[0] = [f for f in os.listdir(dirs[0]) if f.endswith('.png')]
            files[1] = [f for f in os.listdir(dirs[1]) if f.endswith('.bin')]

            return Response(json.dumps({"thumbnails": files[0], "bins": files[1]}),
                            headers={'Content-Type': 'application/json',
                                     'Cache-Control': 'no-cache'})
        
        except Exception as e:
            print(f"Error listing files: {e}")
            gc.collect()
            return Response(json.dumps({"error": str(e)}), status_code=500, 
                           headers={'Content-Type': 'application/json'})
        

    
    
    # Add endpoint to list images in the thumbnails directory
    @app.route('/list-images', methods=['GET'])
    async def list_images(request):
        try:
            # Get all png files in the thumbnails directory (assume it exists)
            images = [f for f in os.listdir('thumbnails') if f.endswith('.png')]
            # gc.collect()  # Force garbage collection
            return Response(json.dumps(images), headers={'Content-Type': 'application/json'})
        except Exception as e:
            print(f"Error listing images: {e}")
            gc.collect()
            return Response(json.dumps({"error": str(e)}), status_code=500, 
                           headers={'Content-Type': 'application/json'})
    
    # Add endpoint to serve images from the thumbnails directory
    @app.route('/thumbnails/<filename>', methods=['GET'])
    async def serve_image(request, filename):
        try:
            # Security check - make sure the filename doesn't contain path traversal
            if '..' in filename or '/' in filename:
                return Response("Invalid filename", status_code=400)
                
            file_path = f'thumbnails/{filename}'
            
            # Generate ETag for the image
            etag = generate_etag(file_path)
            
            # Only perform ETag comparison if we successfully generated an ETag
            if etag is not None:
                # Check If-None-Match header
                if_none_match = request.headers.get('If-None-Match')
                if if_none_match and if_none_match == etag:
                    return Response('', status_code=304, headers={'ETag': etag})
            
            # Build response headers - only include ETag if it was generated successfully
            headers = build_response_headers('image/png', etag)
            
            # Use the generator function directly
            return Response(body=read_in_chunks(file_path), headers=headers)
        except Exception as e:
            print(f"Error serving image {filename}: {e}")
            gc.collect()
            return Response("Error serving image", status_code=500)
    
    # Add a new route for serving static files
    @app.route('/webpage/<path:path>', methods=['GET'])
    async def static_files(request, path):
        try:
            print(f"Serving static file: {path}")
            # Determine content type based on file extension
            content_type = 'text/plain'
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif path.endswith('.png'):
                content_type = 'image/png'
            elif path.endswith('.ico'):
                content_type = 'image/x-icon'
                
            # Open the file but don't read it all at once
            file_path = f'webpage/{path}'
            
            # Generate ETag for the file
            etag = generate_etag(file_path)
            
            # Only perform ETag comparison if we successfully generated an ETag
            if etag is not None:
                # Check If-None-Match header
                if_none_match = request.headers.get('If-None-Match')
                if if_none_match and if_none_match == etag:
                    # Client already has the current version
                    return Response('', status_code=304, headers={'ETag': etag})
            
            # # Log memory before serving file
            # free_mem = gc.mem_free() if hasattr(gc, 'mem_free') else "unknown"
            # print(f"Free memory before serving {path}: {free_mem}")
            
            # Build response headers - only include ETag if it was generated successfully
            headers = build_response_headers(content_type, etag)
            
            # Use the generator function directly
            return Response(body=read_in_chunks(file_path), headers=headers)
        except Exception as e:
            print(f"Error serving static file {path}: {e}")
            gc.collect()
            return Response("File not found", status_code=404)

    # Add a streaming upload endpoint for large files
    @app.route('/upload-stream', methods=['POST'])
    async def upload_stream(request):
        try:
            # Get the filename and folder from query parameters
            filename = request.args.get('filename')
            folder = request.args.get('folder')
            
            # Check if filename or folder is missing
            if not filename:
                return Response(json.dumps({"error": "Missing filename parameter"}), 
                              status_code=400, headers={'Content-Type': 'application/json'})
            
            if not folder:
                return Response(json.dumps({"error": "Missing folder parameter"}), 
                              status_code=400, headers={'Content-Type': 'application/json'})
            
            # Validate that folder is either 'thumbnails' or 'bins'
            if folder not in ['thumbnails', 'bins']:
                return Response(json.dumps({"error": "Folder must be either 'thumbnails' or 'bins'"}), 
                              status_code=400, headers={'Content-Type': 'application/json'})
            
            # Ensure the target directory exists
            try:
                if not folder in os.listdir():
                    os.mkdir(folder)
            except:
                pass
            
            file_path = f'{folder}/{filename}'
            print(f"Streaming upload to: {file_path}")
            
            # Get content length or default to 0
            size = int(request.headers.get('Content-Length', 0))
            print(f"Content-Length: {size} bytes")
            bytes_written = 0

            # Open the file for writing
            with open(file_path, 'wb') as f:
                # Debug the available attributes and methods on the request object
                #print(f"Request attributes: {dir(request)}")
                
                # Process with request.stream only
                if hasattr(request, 'stream'):
                    # print("Using request.stream")
                    # print(f"Request stream attributes: {dir(request.stream)}")
                    
                    try:
                        # Process the stream with proper async/await
                        chunknum = 0
                        while True:
                            # Await the read operation to get the chunk
                            chunk = await request.stream.read(CHUNK_SIZE)
                            
                            if not chunk:
                                break
                                
                            # Write the chunk to the file
                            f.write(chunk)
                            bytes_written += len(chunk)
                                
                            # Check if we've reached the end of content
                            if size > 0 and bytes_written >= size:
                                break
                            
                            chunknum += 1
                            # Force garbage collection periodically
                            if chunknum % 2 == 0:
                                gc.collect()
                            

                            # Progress report
                            print(f"Wrote {bytes_written}/{size} bytes so far")
                            
                    except Exception as stream_error:
                        print(f"Error reading from stream: {stream_error}")
                        raise
                else:
                    print("Request does not have a stream attribute")
            
            print(f"Successfully wrote {bytes_written}/{size} bytes to {file_path}")
            return Response(json.dumps({
                "status": "success",
                "path": file_path,
                "size": bytes_written
            }), headers={'Content-Type': 'application/json'})
        
        except Exception as e:
            print(f"Error in streaming upload: {e}")
            # Try removing the file if it was partially written
            try:
                if folder == 'bins' or folder == 'thumbnails':
                    os.remove(file_path)
                    print(f"Removed partial file: {file_path}")
            except Exception as remove_error:
                print(f"Error removing partial file at {file_path}: {remove_error}")
            gc.collect()
            return Response(json.dumps({"error": str(e)}), 
                          status_code=500, headers={'Content-Type': 'application/json'})

    # Add endpoint to list binary files in the bins directory
    @app.route('/list-binaries', methods=['GET'])
    async def list_binaries(request):
        try:
            # Check if bins directory exists, create if needed
            if 'bins' not in os.listdir():
                os.mkdir('bins')
                
            # Get all bin files in the bins directory
            binaries = [f for f in os.listdir('bins') if f.endswith('.bin')]
            # gc.collect()  # Force garbage collection
            return Response(json.dumps(binaries), headers={'Content-Type': 'application/json'})
        except Exception as e:
            print(f"Error listing binaries: {e}")
            gc.collect()
            return Response(json.dumps({"error": str(e)}), status_code=500, 
                           headers={'Content-Type': 'application/json'})
    
    # Add endpoint for deleting a file from bins or thumbnails
    @app.route('/delete-file', methods=['DELETE'])
    async def delete_file(request):
        try:
            # Get folder and filename from query parameters
            folder = request.args.get('folder')
            filename = request.args.get('filename')
            
            # Check if params are provided
            if not folder or not filename:
                return Response(json.dumps({"error": "Missing folder or filename parameter"}), 
                              status_code=400, headers={'Content-Type': 'application/json'})
            
            # Validate folder is either bins or thumbnails
            if folder not in ['bins', 'thumbnails']:
                return Response(json.dumps({"error": "Folder must be either 'bins' or 'thumbnails'"}), 
                              status_code=400, headers={'Content-Type': 'application/json'})
            
            # Security check - prevent path traversal
            if '..' in filename or '/' in filename:
                return Response(json.dumps({"error": "Invalid filename"}), 
                              status_code=400, headers={'Content-Type': 'application/json'})
            
            # Construct the file path
            file_path = f'{folder}/{filename}'
            
            # Check if the file exists
            try:
                os.stat(file_path)
            except:
                return Response(json.dumps({"error": f"File {filename} not found in {folder}"}), 
                              status_code=404, headers={'Content-Type': 'application/json'})
            
            # Delete the file
            os.remove(file_path)
            
            # Force garbage collection
            # gc.collect()
            
            return Response(json.dumps({"status": "success", "message": f"File {filename} deleted from {folder}"}), 
                          headers={'Content-Type': 'application/json'})
        
        except Exception as e:
            print(f"Error deleting file: {e}")
            gc.collect()
            return Response(json.dumps({"error": str(e)}), 
                          status_code=500, headers={'Content-Type': 'application/json'})
    
    @app.route('/space', methods=['GET'])
    async def get_storage_space(request):
        try:
            import os
            
            # Get total space information using statvfs
            try:
                stats = os.statvfs('/')
                # Calculate total and free space in bytes
                block_size = stats[0]  # f_bsize - file system block size
                total_blocks = stats[2]  # f_blocks - total blocks in filesystem
                free_blocks = stats[3]  # f_bfree - free blocks
                
                total_space = block_size * total_blocks
                free_space = block_size * free_blocks
                used_space = total_space - free_space
                
            except Exception as e:
                print(f"Error getting statvfs: {e}")
                # Default values for ESP32 if statvfs fails
                total_space = 1024 * 1024 * 4  # 4MB
                used_space = 1024 * 1024 * 1   # Assume 1MB used
                free_space = total_space - used_space
                
            # Format as KB with one decimal place
            used_kb = round(used_space / 1024, 1)
            free_kb = round(free_space / 1024, 1)
            total_kb = round(total_space / 1024, 1)
            
            # Calculate percentage used
            percent_used = round((used_space / total_space) * 100 if total_space > 0 else 0, 1)
            
            # Return the data
            return Response(json.dumps({
                "used": used_space,
                "free": free_space,
                "total": total_space,
                "used_kb": used_kb,
                "free_kb": free_kb,
                "total_kb": total_kb,
                "percent_used": percent_used
            }), headers={'Content-Type': 'application/json', 'Cache-Control': 'no-cache'})
            
        except Exception as e:
            print(f"Error getting storage space: {e}")
            gc.collect()
            return Response(json.dumps({"error": str(e)}), status_code=500, 
                           headers={'Content-Type': 'application/json'})

    return app

async def release_port(port=80):
    """Attempt to release a port that might be in use"""
    try:
        print(f"Attempting to release port {port}...")
        # Create a socket and try to bind to the port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.close()
        await asyncio.sleep(0.1) # Add a small delay after closing
        print(f"Port {port} should be available now")
        return True
    except Exception as e:
        print(f"Failed to release port {port}: {e}")
        return False

async def run_server(autoconnect=True):
    app = await setup(autoconnect=autoconnect)
    ipaddr = wifi.ipaddr()
    if app:
        try:
            oledclear()
            oledprint(f"IP: {ipaddr}")
            await app.start_server(debug=True, port=80)
        except Exception as e:
            print(f"Error starting server: {e}")
            oledclear()
            if "address already in use" in str(e) or "EADDRINUSE" in str(e):
                print("Port 80 is already in use. Attempting to release it...")
                if await release_port(80):
                    print("Waiting a moment before retrying server start...")
                    await asyncio.sleep(0.5) # Add a delay before retrying
                    try:
                        oledprint("IP: {ipaddr}")
                        await app.start_server(debug=True, port=80)
                    except Exception as e2:
                        oledclear()
                        oledprint("err:{e2}")
                        print(f"Failed to start server after releasing port: {e2}")
                else:
                    print("Failed to release port 80. Exiting...")
            else:
                oledclear()
                oledprint("err:{e}")
                # Handle other potential startup errors if needed
                print(f"An unexpected error occurred during server startup: {e}")
                print("Server setup failed. Exiting...")
    else:
        oledclear()
        oledprint("Server setup failed")
        print("Server setup failed. Exiting...")

# Main function to run the server
def start():
    try:
        asyncio.run(run_server(autoconnect=True))
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

# If this file is run directly
if __name__ == "__main__":
    start()
