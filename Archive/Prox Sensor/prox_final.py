import time
from machine import UART, Pin
import sys

# Using the pins you've confirmed work on your ESP32-CAM
RX_PIN = 13
TX_PIN = 14

def init_sensor():
    """Initializes UART1 with the settings that worked for your GPS."""
    uart = UART(1, baudrate=9600, bits=8, parity=None, rx=RX_PIN, tx=TX_PIN, stop=1)
    uart.init()
    time.sleep_ms(500) # Wait for stabilization
    print('RIPPLE Sensor System: Online')
    return uart

def get_distance(uart):
    """
    Finds the 0xFF header and calculates distance.
    Purges stale data to prevent 'freezing'.
    """
    # 1. Purge the buffer if it's too full (prevents lag)
    if uart.any() > 20:
        uart.read(uart.any())

    # 2. Search for the 0xFF header
    start_time = time.ticks_ms()
    while (time.ticks_ms() - start_time) < 200: # 200ms timeout
        if uart.any() > 0:
            if uart.read(1) == b'\xff':
                # Found header, now wait for the remaining 3 bytes
                # We loop briefly to ensure they arrive
                for _ in range(10): 
                    if uart.any() >= 3:
                        data = uart.read(3)
                        h_byte = data[0]
                        l_byte = data[1]
                        checksum = data[2]
                        
                        # Validate checksum
                        if (0xff + h_byte + l_byte) & 0xFF == checksum:
                            return (h_byte << 8) + l_byte
                        break
                    time.sleep_ms(2)
    return None

def main():
    uart = init_sensor()
    consecutive_fails = 0

    while True:
        try:
            dist = get_distance(uart)
            
            if dist is not None:
                print(f"Distance: {dist} mm")
                consecutive_fails = 0
            else:
                consecutive_fails += 1
                # If it fails 10 times in a row, reset the UART
                if consecutive_fails > 10:
                    print("Connection lost. Resetting UART...")
                    uart.init()
                    consecutive_fails = 0
            
            time.sleep_ms(100) # 10Hz reading rate

        except KeyboardInterrupt:
            print("Shutdown.")
            sys.exit()

if __name__ == "__main__":
    main()