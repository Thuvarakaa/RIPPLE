import time
from machine import UART
import sys

uart1 = UART(1, baudrate=9600, bits=8, parity=None, rx=13, tx=14, stop=1)
uart1.init()
print('Successfully initialized')
for runs in range(0, 10):
    delay_gps = 0
    collect_flag = False
    for i in range(0, 40000):
        present = uart1.any()
        if present != 0:
            collect_flag = True
            break
        time.sleep_ms(10)
        delay_gps += 0.01
        if (delay_gps % 20) == 0:
            print('Still waiting...')
    if collect_flag == False:
        print('Unable to collect data.')
        sys.exit()
    else:
        print(f'Time to get data packet {runs+1}: {delay_gps}s')
        buf = uart1.readline().decode('utf-8')
        print(buf)
        
        
        

#time.sleep(0)
#one_line = uart1.read()
#print(type(one_line))
#print(one_line)