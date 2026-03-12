from micropyGPS import MicropyGPS

gps_data = MicropyGPS()

# This allows main.py to write to it and web_routes.py to read it
sensor_state = {
    "distance": 0,
    "last_update": 0
}