# main.py
import picoweb
import wifi
import camera_service
import _thread
import time
import web_routes
from machine import UART, Pin
from shared import gps_data, sensor_state

SSID = "Vedashri"
PASSWORD = "vedashri18"

# Global variable to store the latest distance for the web API
current_distance = 0

def sensor_background_thread():
    global current_distance
    
    # Init Sensors (UART 1: Prox 13/14, UART 2: GPS 15)
    prox_uart = UART(1, baudrate=9600, bits=8, parity=None, rx=13, tx=14, stop=1)
    trigger = Pin(14, Pin.OUT)
    trigger.value(1)
    
    gps_uart = UART(2, baudrate=9600, bits=8, parity=None, rx=15, tx=12, stop=1)
    
    print("Background Thread: Prox (13/14) and GPS (15) Active")

    while True:
        # --- 1. HANDLE GPS ---
        # Read available GPS data without letting it block the loop
        if gps_uart.any():
            lines = gps_uart.read() # Read all available bytes at once
            for b in lines:
                gps_data.update(chr(b))
        
        # --- 2. HANDLE PROXIMITY (High Priority Window) ---
        # Clear any old data from the buffer before triggering
        while prox_uart.any():
            prox_uart.read()
            
        # Send the Trigger Pulse
        trigger.value(0)
        time.sleep_us(20) # Slightly longer pulse for stability
        trigger.value(1)
        
        # Immediate poll for the 4-byte response
        # We use ticks_us for higher precision timing
        deadline = time.ticks_add(time.ticks_ms(), 150)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            if prox_uart.any() >= 4:
                header = prox_uart.read(1)
                if header == b'\xff':
                    data = prox_uart.read(3)
                    if len(data) == 3:
                        # Checksum Validation
                        if (0xff + data[0] + data[1]) & 0xFF == data[2]:
                            # Update the shared dictionary instead of a local variable
                            sensor_state["distance"] = (data[0] << 8) + data[1]
                            sensor_state["last_update"] = time.ticks_ms()
            time.sleep_ms(1) # Small yields to prevent CPU hogging
        
        time.sleep_ms(50) # Faster loop for more responsive proximity

def main():
    #camera_service.init() #
    ip_addr = wifi.connect(SSID, PASSWORD) #
    print("The IP Address is:", ip_addr)

    _thread.start_new_thread(sensor_background_thread, ()) #

    # 1. Create the app first
    app = picoweb.WebApp(__name__, web_routes.ROUTES) #

    # 2. Pass the app instance to web_routes so it can render templates
    web_routes.set_app(app) #

    # 3. Add the camera route
    web_routes.ROUTES.append(("/video", camera_service.video)) #

    app.run(debug=1, port=80, host="0.0.0.0") #

if __name__ == "__main__":
    main()
