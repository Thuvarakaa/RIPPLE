from micropyGPS import MicropyGPS

# Keep your existing GPS object
gps_data = MicropyGPS()

# Add a simple dictionary or class for the Proximity data
# This allows main.py to write to it and web_routes.py to read it
sensor_state = {
    "distance": 0,
    "last_update": 0
}