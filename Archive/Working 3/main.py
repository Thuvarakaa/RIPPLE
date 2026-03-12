# main.py
import picoweb
import wifi
import camera_service
import _thread
import time
from machine import UART
from shared import gps_data  # Changed this
from web_routes import ROUTES

SSID = "Vedashri"
PASSWORD = "vedashri18"

def gps_background_thread():
    uart = UART(1, baudrate=9600, bits=8, parity=None, rx=13, tx=14, stop=1)
    #print("GPS Thread active - Camera disabled")
    while True:
        while uart.any():
            line = uart.readline()
            if line:
                # ADD THIS PRINT: This will show you the raw NMEA strings
                print("Raw NMEA:", line)
                for b in line:
                    gps_data.update(chr(b))
        time.sleep_ms(100)

def main():
    camera_service.init()
    ip_addr = wifi.connect(SSID, PASSWORD)
    print("The IP Address is:", ip_addr)

    _thread.start_new_thread(gps_background_thread, ())

    ROUTES.append(("/video", camera_service.video))

    app = picoweb.WebApp(__name__, ROUTES)
    app.run(debug=1, port=80, host="0.0.0.0")
    
    if uart.any():
            line = uart.readline()
            print("Raw GPS:", line) # Add this line to see if data is arriving

if __name__ == "__main__":
    main()