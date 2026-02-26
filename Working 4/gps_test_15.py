import time
from machine import UART, Pin

# Using UART 2 for the software-based connection
# Pin 12 is a dummy TX since we only need to receive data from the GPS
GPS_RX_PIN = 15
DUMMY_TX_PIN = 12 

def test_gps():
    print("--- RIPPLE GPS Pulse Test (GPIO 15) ---")
    
    # Initialize UART
    # 9600 is the standard baud rate for almost all GPS modules
    gps_serial = UART(2, baudrate=9600, rx=GPS_RX_PIN, tx=DUMMY_TX_PIN, timeout=1000)
    
    print("Listening for NMEA sentences...")
    print("(If you see nothing, try swapping GPS TX to a different pin or check power)")

    while True:
        try:
            if gps_serial.any():
                # Read whatever is in the buffer
                raw_data = gps_serial.read()
                
                try:
                    # GPS data is standard ASCII text
                    text_data = raw_data.decode('utf-8')
                    print(text_data, end='')
                except:
                    # If decoding fails, show the raw bytes
                    print("Raw Bytes:", raw_data)
            else:
                # If the buffer is empty, show the physical pin state
                p15 = Pin(GPS_RX_PIN, Pin.IN)
                print(f"Polling... Pin 15 State: {p15.value()}")
                
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nTest stopped.")
            break

if __name__ == "__main__":
    test_gps()