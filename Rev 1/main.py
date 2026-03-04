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

def sensor_background_thread():
    # Init Sensors (UART 1: Prox 13/14, UART 2: GPS 15)
    # Note: Pin 14 is handled by the UART peripheral as TX; no manual Pin(14) needed.
    prox_uart = UART(1, baudrate=9600, bits=8, parity=None, rx=13, tx=14, stop=1)
    gps_uart = UART(2, baudrate=9600, bits=8, parity=None, rx=15, tx=12, stop=1)
    
    print("Background Thread: Prox (13/14) and GPS (15) Active")

    while True:
        # --- 1. HANDLE GPS ---
        if gps_uart.any():
            lines = gps_uart.read() 
            for b in lines:
                gps_data.update(chr(b))
        
        # --- 2. HANDLE PROXIMITY ---
        # Clear any old data from the buffer to ensure a fresh reading
        while prox_uart.any():
            prox_uart.read()
            
        # Send the Trigger Byte (0x55) via UART
        # This replaces the manual trigger.value(0) / trigger.value(1) logic
        prox_uart.write(b'\x55') 
        
        # Immediate poll for the 4-byte response [0xFF, Data_H, Data_L, Checksum]
        deadline = time.ticks_add(time.ticks_ms(), 150)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            if prox_uart.any() >= 4:
                header = prox_uart.read(1)
                if header == b'\xff':
                    data = prox_uart.read(3)
                    if len(data) == 3:
                        # Checksum Validation: (Header + H + L) & 0xFF
                        if (0xff + data[0] + data[1]) & 0xFF == data[2]:
                            # Update the shared dictionary for web_routes to see
                            sensor_state["distance"] = (data[0] << 8) + data[1]
                            break # Success, exit polling
            time.sleep_ms(1) 
        
        time.sleep_ms(50) # Loop delay for stability

def main():
    camera_service.init() # Uncomment if camera is needed
    ip_addr = wifi.connect(SSID, PASSWORD) 
    print("The IP Address is:", ip_addr)

    # Start the background sensor thread
    _thread.start_new_thread(sensor_background_thread, ()) 

    # 1. Create the app first
    app = picoweb.WebApp(__name__, web_routes.ROUTES) 

    # 2. Pass the app instance to web_routes
    web_routes.set_app(app) 

    # 3. Add the camera route
    web_routes.ROUTES.append(("/video", camera_service.video)) 

    # Start the web server
    app.run(debug=1, port=80, host="0.0.0.0") 

if __name__ == "__main__":
    main()