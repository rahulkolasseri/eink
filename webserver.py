import system
import time
from microdot.microdot import Microdot, Response, Request

def start_server():
    """Start the web server after connecting to WiFi - this will block the UI"""
    # Clear screen and show initial message
    system.oledclear()
    system.oledprint("Starting web server...\n")
    
    # Setup WiFi
    system.oledprint("Connecting to WiFi...")
    try:
        # Get available networks
        nets, ssidpass = system.known_networks()
        
        # Try to connect
        wlan = system.wlansetup()
        
        if not wlan.isconnected() and len(nets) > 0:
            for net in nets:
                ssid = net[0].decode()
                if ssid in ssidpass:
                    password = ssidpass[ssid]
                    system.oledclear()
                    system.oledprint(f"Connecting to\n{ssid}...")
                    wlan.connect(ssid, password)
                    
                    # Wait for connection with timeout
                    max_wait = 20
                    while max_wait > 0 and not wlan.isconnected():
                        time.sleep(1)
                        max_wait -= 1
                    
                    if wlan.isconnected():
                        break
        
        if not wlan.isconnected():
            system.oledclear()
            system.oledprint("WiFi connection\nfailed!")
            system.pulse_vibe_motor(100)
            time.sleep(3)
            return
        
        # Get and display IP
        ip_address = wlan.ifconfig()[0]
        system.oledclear()
        system.oledprint(f"Connected!\nIP: {ip_address}")
        system.pulse_vibe_motor(65)
        time.sleep(1)
        
        # Setup web server
        system.oledclear()
        system.oledprint(f"Starting server...\nIP: {ip_address}")
        
        app = Microdot()
        shutdown_requested = False
        
        @app.route('/')
        def index(request):
            try:
                with open('webpage/index.html', 'r') as f:
                    html = f.read()
                return Response(body=html, headers={'Content-Type': 'text/html'})
            except Exception as e:
                return Response(body=f"Error: {str(e)}", status_code=500)
        
        @app.route('/status')
        def status(request):
            bat_voltage, _ = system.get_battery_voltage()
            return Response(body=f'{{"battery": "{bat_voltage:.2f}V"}}', 
                           headers={'Content-Type': 'application/json'})
        
        @app.route('/shutdown', methods=['POST'])
        def shutdown(request):
            nonlocal shutdown_requested
            system.oledclear()
            system.oledprint("Shutting down server...")
            system.pulse_vibe_motor(100)
            
            # Set flag to exit the server loop
            shutdown_requested = True
            
            return Response(body='{"status": "shutting_down"}', 
                           headers={'Content-Type': 'application/json'})
        
        # Start server (blocking)
        system.oledclear()
        system.oledprint(f"Server running!\nIP: {ip_address}\nhttp://{ip_address}/")
        
        # Create a custom request handler that checks for shutdown
        original_handler = app._handle_request
        
        def shutdown_aware_handler(request, *args, **kwargs):
            if shutdown_requested:
                # Stop accepting new requests if shutdown was requested
                raise StopIteration("Shutdown requested")
            return original_handler(request, *args, **kwargs)
        
        app._handle_request = shutdown_aware_handler
        
        # Custom server loop that can be exited gracefully
        server_socket = app._prepare_server_socket(port=80)
        
        try:
            while not shutdown_requested:
                try:
                    # Process one request at a time
                    app._handle_one_request(server_socket)
                except StopIteration:
                    # Exit the loop when shutdown is requested
                    break
                except Exception as e:
                    if not shutdown_requested:
                        print(f"Error handling request: {e}")
        finally:
            # Clean up
            server_socket.close()
            
        # Show shutdown complete message
        system.oledclear()
        system.oledprint("Server shut down\nreturning to menu...")
        time.sleep(2)
        
    except Exception as e:
        system.oledclear()
        system.oledprint(f"Error: {str(e)}")
        system.pulse_vibe_motor(100)
        time.sleep(3)
