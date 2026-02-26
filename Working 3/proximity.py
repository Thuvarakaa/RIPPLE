import time
from machine import UART, Pin
import sys

# Final Pins for Trigger Mode
RX_PIN = 13  # Receives data from White wire
TX_PIN = 14  # Sends trigger pulse to Yellow wire

def init_sensor():
    # Initialize UART on Pin 14
    uart = UART(1, baudrate=9600, bits=8, parity=None, rx=RX_PIN, tx=TX_PIN, stop=1)
    uart.init()
    
    # Set up Pin 13 as a standard Output pin for triggering
    global trigger
    trigger = Pin(TX_PIN, Pin.OUT)
    trigger.value(1) # Keep it High by default
    
    time.sleep_ms(500)
    print('RIPPLE System: Trigger Mode Active')
    return uart

def trigger_pulse():
    """Mimics 'touching the wire to ground'"""
    trigger.value(0)      # Pull Low (GND)
    time.sleep_us(10)     # Wait 10 microseconds
    trigger.value(1)      # Pull High again

def get_distance(uart):
    # 1. Clear the buffer
    if uart.any():
        uart.read(uart.any())
        
    # 2. Send the 'Tap'
    trigger_pulse()
    
    # 3. Wait for the 4-byte response
    start_time = time.ticks_ms()
    while (time.ticks_ms() - start_time) < 200:
        if uart.any() >= 4:
            if uart.read(1) == b'\xff':
                data = uart.read(3)
                if len(data) == 3:
                    # Validate Checksum: (Header + H + L) & 0xFF
                    if (0xff + data[0] + data[1]) & 0xFF == data[2]:
                        return (data[0] << 8) + data[1]
    return None

def main():
    uart = init_sensor()
    while True:
        try:
            dist = get_distance(uart)
            if dist is not None:
                print(f"Distance: {dist} mm")
            else:
                print("Waiting for trigger response...")
            
            time.sleep_ms(100) # Check 10 times per second
            
        except KeyboardInterrupt:
            sys.exit()

main()
