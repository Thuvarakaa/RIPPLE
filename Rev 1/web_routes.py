import json
import picoweb
from shared import gps_data, sensor_state

# This variable will hold the app instance if needed for templates
_app = None

def set_app(app_inst):
    global _app
    _app = app_inst

def get_sensor_data(req, resp):
    """API endpoint to return GPS and Proximity data as JSON"""
    
    # 1. Handle Latitude conversion logic
    lat_val = gps_data.latitude[0] + (gps_data.latitude[1] / 60)
    if gps_data.latitude[2] == 'S': 
        lat_val = -lat_val
    
    # 2. Handle Longitude conversion logic
    lon_val = gps_data.longitude[0] + (gps_data.longitude[1] / 60)
    if gps_data.longitude[2] == 'W': 
        lon_val = -lon_val

    # 3. Build the response data from shared.py objects
    data = {
        "lat": lat_val,
        "lon": lon_val,
        "sats": gps_data.satellites_in_use,
        "distance": sensor_state["distance"]  # Pulling from the shared dict
    }
    
    # 4. Send the HTTP response
    yield from resp.awrite("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
    yield from resp.awrite(json.dumps(data))

def index(req, resp):
    """Serves the main HTML page"""
    yield from resp.awrite("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    
    # Reading index.html in chunks to save RAM on the ESP32
    try:
        with open("index.html", "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                yield from resp.awrite(chunk)
    except OSError:
        yield from resp.awrite("<html><body><h1>index.html not found</h1></body></html>")

# --- ROUTES DEFINITION ---
# This must be at the end so all functions above are already defined
ROUTES = [
    ("/", index),
    ("/api/data", get_sensor_data)
]