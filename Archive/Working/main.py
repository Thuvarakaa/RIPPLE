# main.py
import picoweb
import wifi
import camera_service
from web_routes import ROUTES

SSID = "Vedashri"
PASSWORD = "vedashri18"

def main():
    camera_service.init()
    wifi.connect(SSID, PASSWORD)

    ROUTES.append(("/video", camera_service.video))

    app = picoweb.WebApp(__name__, ROUTES)
    app.run(debug=1, port=80, host="0.0.0.0")

main()