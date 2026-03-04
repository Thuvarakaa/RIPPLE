# wifi.py
import network
import utime

def connect(ssid, password, timeout=5):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(ssid, password)

        start = utime.time()
        while not wlan.isconnected():
            utime.sleep(1)
            if utime.time() - start > timeout:
                raise RuntimeError("WiFi connection failed")

    return wlan.ifconfig()
