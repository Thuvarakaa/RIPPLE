import time
from machine import UART, Pin
import sys
from micropyGPS import MicropyGPS
 
RX_PIN = 13
TX_PIN = 14
WAIT_MS = 4000
POLL_PRINT_TIME_S = 5
 
def init():
    uart1 = UART(1, baudrate=9600, bits=8, parity=None, rx=RX_PIN, tx=TX_PIN, stop=1)
    uart1.init()
    print('Successfully initialized')
    return uart1
 
def acquire_data(uart, print_time=False):
    delay_gps = 0
    collect_flag = False
    for i in range(0, WAIT_MS):
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
        buf = uart.readline().decode('ascii')
        return buf

def main():
    uart = init()
    my_gps = MicropyGPS()
    start_time = time.time()
    last_print_time = start_time - start_time
    while True:
        try:
            buf = acquire_data(uart=uart)
            for char in buf:
                my_gps.update(char)
            time.sleep_ms(100)
            cur_time = time.time()
            if (((cur_time - start_time) % POLL_PRINT_TIME_S) < 0.1) and ((cur_time - start_time) != last_print_time):
                print(f"Time elapsed: {cur_time - start_time}")
                print(my_gps.latitude)
                print(my_gps.longitude)
                last_print_time = cur_time - start_time
        except KeyboardInterrupt:
            print("Program stopped.")
            sys.exit()

main()

 