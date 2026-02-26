import time
from machine import UART, Pin
import sys
from micropyGPS import MicropyGPS

# --- PIN CONFIGURATION ---
PROX_RX = 13
PROX_TRIG = 14
GPS_RX_PIN = 15

def init_systems():
    # 1. Initialize Proximity (Hardware UART 1)
    prox_uart = UART(1, baudrate=9600, rx=PROX_RX, tx=PROX_TRIG)
    trigger = Pin(PROX_TRIG, Pin.OUT)
    trigger.value(1)
    
    # 2. Initialize GPS (Using UART 2 as Software UART on Pin 15)
    # Pin 12 is used as a placeholder TX pin since we only need to receive
    gps_uart = UART(2, baudrate=9600, rx=GPS_RX_PIN, tx=12) 
    
    print("--- RIPPLE SYSTEMS ONLINE ---")
    return prox_uart, gps_uart, trigger

def get_proximity(uart, trigger_pin):
    # Trigger the sensor
    trigger_pin.value(0)
    time.sleep_us(10)
    trigger_pin.value(1)
    
    start = time.ticks_ms()
    # Wait for the 4-byte response
    while (time.ticks_ms() - start) < 150:
        if uart.any() >= 4:
            data = uart.read(4)
            if data[0] == 0xFF:
                # Checksum validation
                if (data[0] + data[1] + data[2]) & 0xFF == data[3]:
                    return (data[1] << 8) + data[2]
    return None

def main():
    prox_uart, gps_uart, trigger = init_systems()
    my_gps = MicropyGPS()
    
    print("Monitoring sensors... Press Ctrl+C to stop.")
    
    while True:
        try:
            # --- PROXIMITY SECTION ---
            dist = get_proximity(prox_uart, trigger)
            if dist is not None:
                # Adding the print statement for proximity
                print(f"[PROX] Object at: {dist} mm")
            else:
                print("[PROX] No reading...")

            # --- GPS SECTION ---
            while gps_uart.any():
                char = chr(gps_uart.read(1)[0])
                my_gps.update(char)
            
            # Print GPS every few seconds if we have a valid fix
            if my_gps.satellites_in_use > 0:
                lat = my_gps.latitude_string()
                lon = my_gps.longitude_string()
                print(f"[GPS] Sats: {my_gps.satellites_in_use} | Loc: {lat}, {lon}")
            else:
                # Helps you know the GPS is powered but just searching
                print("[GPS] Searching for satellites...")
            
            print("-" * 30) # Visual separator for the shell
            time.sleep_ms(500) # Check twice per second
            
        except KeyboardInterrupt:
            print("\nShutting down RIPPLE...")
            break

if __name__ == "__main__":
    main()
