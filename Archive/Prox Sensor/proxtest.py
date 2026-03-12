import time
from machine import UART, Pin
import sys

# Using the pins you've confirmed work on your ESP32-CAM
RX_PIN = 13
TX_PIN = 14

def init_sensor():
    """Initializes UART1 with the settings that worked for your GPS."""
    # We use the exact same setup you confirmed works for your GPS
    uart = UART(1, baudrate=9600, bits=8, parity=None, rx=RX_PIN, tx=TX_PIN, stop=1)
    uart.init()
    time.sleep_ms(500) 
    print('RIPPLE Sensor System: Active & Monitoring')
    return uart

def get_distance(uart):
    """
    Constantly scans the buffer for the 0xFF header.
    Works best with Sensor RX (Yellow) DISCONNECTED.
    """
    # 1. Clear old data to prevent reading 'stale' or 'laggy' distances
    if uart.any() > 20:
        uart.read(uart.any())

    # 2. Look for the start of a packet (0xFF)
    # We check for up to 150ms (the sensor sends data every 100ms)
    start_search = time.ticks_ms()
    while (time.ticks_ms() - start_search) < 150:
        if uart.any() > 0:
            if uart.read(1) == b'\xff':
                # Header found! Wait briefly for the next 3 bytes to arrive
                time.sleep_ms(10) 
                if uart.any() >= 3:
                    data = uart.read(3)
                    h_byte = data[0]
                    l_byte = data[1]
                    checksum = data[2]
                    
                    # Verify integrity: (0xFF + Data_H + Data_L) & 0xFF
                    if (0xff + h_byte + l_byte) & 0xFF == checksum:
                        return (h_byte << 8) + l_byte
    return None

def main():
    uart = init_sensor()
    last_valid_dist = 0
    fail_count = 0

    while True:
        try:
            dist = get_distance(uart)
            
            if dist is not None:
                last_valid_dist = dist
                fail_count = 0 # Reset fails on success
                print(f"Distance: {dist} mm")
            else:
                fail_count += 1
                # If we miss 10 checks (~1 second), force a UART reset
                if fail_count >= 10:
                    print("⚠️ Sensor timeout. Attempting hardware reset...")
                    uart.init()
                    fail_count = 0
                else:
                    print(f"Reading missed. Last stable: {last_valid_dist} mm")

            # High-frequency check (10 times per second)
            time.sleep_ms(100)

        except KeyboardInterrupt:
            print("System Shutdown.")
            sys.exit()

if __name__ == "__main__":
    main()