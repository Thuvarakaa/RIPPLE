import time
from machine import UART, Pin
import sys
from micropyGPS import MicropyGPS

RX_PIN = 13
TX_PIN = 14

def init():
    uart1 = UART(1, baudrate=9600, bits=8, parity=None, rx=RX_PIN, tx=TX_PIN, stop=1)
    uart1.init()
    print('Successfully initialized')
    return uart1

def acquire_data(uart, print_time=False):
    delay_gps = 0
    collect_flag = False
    for i in range(0, 4000):
        present = uart.any()
        if present != 0:
            collect_flag = True
            break
        time.sleep_ms(1)
        delay_gps += 1
    if collect_flag == False:
        print('Unable to collect data.')
        return ""
    else:
        if print_time == True:
            print(f'Time to get data: {delay_gps}ms')
        buf = uart.readline().decode('utf-8')
        return buf
    
def main():
    uart = init()
    my_gps = MicropyGPS()
    while True:
        try:
            buf = acquire_data()
            my_gps.update(buf)
            time.sleep_ms(100)
        except KeyboardInterrupt:
            sys.exit()