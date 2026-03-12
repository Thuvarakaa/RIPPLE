# camera.py
import camera
import gc
import picoweb

def init():
    camera.deinit()
    camera.init(
        0,
        d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
        format=camera.JPEG,
        framesize=camera.FRAME_VGA,
        xclk_freq=camera.XCLK_20MHz,
        href=23, vsync=25, reset=-1, pwdn=-1,
        sioc=27, siod=26, xclk=21, pclk=22,
        fb_location=camera.PSRAM
    )

    camera.mirror(1)
    camera.quality(10)

def _frame_generator():
    while True:
        buf = camera.capture()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buf + b'\r\n')
        del buf
        gc.collect()

def video(req, resp):
    yield from picoweb.start_response(
        resp,
        content_type="multipart/x-mixed-replace; boundary=frame"
    )

    for frame in _frame_generator():
        yield from resp.awrite(frame)
