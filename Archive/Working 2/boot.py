# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

#exec(open('gps.py').read(), globals())
#exec(open('gps_test.py').read(), globals())
exec(open('main.py').read(), globals())
