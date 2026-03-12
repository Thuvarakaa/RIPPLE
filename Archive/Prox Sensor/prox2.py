from machine import UART
import time

class ESP32_A02_Distance:
    def __init__(self, tx_pin=15, rx_pin=13):
        # Using UART 1 for ESP32-CA4
        self._ser = UART(1, baudrate=9600, tx=tx_pin, rx=rx_pin)
        self.distance = 0

    def getDistance(self):
        # The sensor sends 4 bytes. Wait until at least 4 are in the buffer.
        if self._ser.any() >= 4:
            # Clear the buffer until we find the start byte (0xFF)
            while self._ser.any() > 0:
                header = self._ser.read(1)
                if header == b'\xff':
                    break
            
            # Now read exactly the next 3 bytes
            data = self._ser.read(3)
            if data is not None and len(data) == 3:
                h_byte = data[0]
                l_byte = data[1]
                checksum = data[2]
                
                # Checksum: (Header + Data_H + Data_L) & 0xFF
                if (0xFF + h_byte + l_byte) & 0xFF == checksum:
                    self.distance = (h_byte << 8) + l_byte
                    return self.distance
        return None

# --- Main Loop ---
sensor = ESP32_A02_Distance(tx_pin=15, rx_pin=14)

print("Starting sensor...")
while True:
    dist = sensor.getDistance()
    if dist:
        print("Distance: {} mm".format(dist))
    else:
        # Check if the UART is actually receiving ANYTHING
        if sensor._ser.any() > 0:
             print("Receiving data, but not a valid packet yet...")
    
    time.sleep(0.1)