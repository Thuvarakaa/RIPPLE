# web_routes.py
import picoweb
import json
from shared import gps_data  # Changed this

def index(req, resp):
    yield from picoweb.start_response(resp, "text/html")
    with open("index.html", "r") as f:
        yield from resp.awrite(f.read())

def get_gps_json(req, resp):
    # Check if we have a valid fix before doing math
    # micropyGPS sets latitude[0] to 0 if no data is parsed yet
    if gps_data.latitude[0] == 0:
        data = {"lat": 0.0, "lon": 0.0, "fix": False}
    else:
        lat = gps_data.latitude[0] + (gps_data.latitude[1] / 60)
        if gps_data.latitude[2] == 'S': lat = -lat
        
        lon = gps_data.longitude[0] + (gps_data.longitude[1] / 60)
        if gps_data.longitude[2] == 'W': lon = -lon
        data = {"lat": lat, "lon": lon, "fix": True}
    
    yield from picoweb.start_response(resp, content_type="application/json")
    yield from resp.awrite(json.dumps(data))

ROUTES = [
    ("/", index),
    ("/api/gps", get_gps_json),
]