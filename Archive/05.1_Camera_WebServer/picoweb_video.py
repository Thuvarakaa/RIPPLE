# This section uses firmware from Lemariva's Micropython-camera-driver.  
# for details, please refer to: https://github.com/lemariva/micropython-camera-driver  
import picoweb
import utime
import camera
import gc

SSID = "Vedashri"         # Enter your WiFi name
PASSWORD = "vedashri18"     # Enter your WiFi password

# Let ESP32 connect to wifi.
def wifi_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PASSWORD) 
    start = utime.time()
    while not wlan.isconnected():
        utime.sleep(1)
        if utime.time()-start > 5:
            print("connect timeout!")
            break
    if wlan.isconnected():
        print('network config:', wlan.ifconfig())

# Initializing the Camera
def camera_init():
    # Disable camera initialization
    camera.deinit()
    # Enable camera initialization
    camera.init(0, d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                format=camera.JPEG, framesize=camera.FRAME_VGA, 
                xclk_freq=camera.XCLK_20MHz,
                href=23, vsync=25, reset=-1, pwdn=-1,
                sioc=27, siod=26, xclk=21, pclk=22, fb_location=camera.PSRAM)

    camera.framesize(camera.FRAME_VGA) # Set the camera resolution
    # The options are the following:
    # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
    # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
    # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA
    # Note: The higher the resolution, the more memory is used.
    # Note: And too much memory may cause the program to fail.
    
    camera.flip(0)                       # Flip up and down window: 0-1
    camera.mirror(1)                     # Flip window left and right: 0-1
    camera.saturation(0)                 # saturation: -2,2 (default 0). -2 grayscale 
    camera.brightness(0)                 # brightness: -2,2 (default 0). 2 brightness
    camera.contrast(0)                   # contrast: -2,2 (default 0). 2 highcontrast
    camera.quality(10)                   # quality: # 10-63 lower number means higher quality
    # Note: The smaller the number, the sharper the image. The larger the number, the more blurry the image
    
    camera.speffect(camera.EFFECT_NONE)  # special effects:
    # EFFECT_NONE (default) EFFECT_NEG EFFECT_BW EFFECT_RED EFFECT_GREEN EFFECT_BLUE EFFECT_RETRO
    camera.whitebalance(camera.WB_NONE)  # white balance
    # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME

# HTTP Response Content  
index_web="""
HTTP/1.0 200 OK\r\n
<html>
<head>
    <title>RIPPLE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- We still need Leaflet for the Map because making a map from scratch is too hard -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        /* Simple CSS Styles */
        body {
            font-family: Lato, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }

        h1 {
            color: #333;
            text-align: center;
        }

        .container {
            max-width: 800px;
            margin: 0 auto; /* Centers the div */
            background-color: white;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
        }

        .section {
            margin-bottom: 20px;
            padding: 10px;
            border: 2px solid #ddd;
        }

        /* Make the video image responsive */
        #cam-stream {
            width: 100%;
            height: auto;
            display: block;
            margin-bottom: 10px;
            background-color: #000;
        }

        /* Map Settings */
        #map {
            height: 300px;
            width: 100%;
        }

        /* Stat numbers styling */
        .stat {
            font-size: 1.2em;
            font-weight: bold;
            color: blue;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>RIPPLE</h1>

        <!-- SECTION 1: VIDEO -->
        <div class="section">
            <h2>Live Camera</h2>
            <!-- The source will be set by JavaScript below -->
            <img src="/video" margin-top:100px; style="transform:rotate(180deg)"; />
            
           
        </div>

        <!-- SECTION 2: GPS DATA -->
        <div class="section">
            <h2>GPS Location</h2>
            <p>Latitude: <span id="lat" class="stat">--</span></p>
            <p>Longitude: <span id="lon" class="stat">--</span></p>
            <!-- <p>Speed: <span id="speed" class="stat">0</span> km/h</p> -->
            <!-- <p>Satellites: <span id="sats" class="stat">0</span></p> -->
        </div>

        <!-- SECTION 3: MAP -->
        <div class="section">
            <h2>Map View</h2>
            <div id="map"></div>
        </div>
    </div>

    <script>
        // --- SETTINGS ---
        // If testing on computer, we use a fake image.
        // If on the ESP32, we use the real stream.
        var isLocal = window.location.hostname === "localhost" || window.location.protocol === 'file:';
        var streamUrl = isLocal ? "https://www.water.com/media/cms/a-us.storyblok.com/f/1021132/2800x986/f420e28233/types-of-water-water-surface.webp?quality=85&width=1024&dpr=2" : window.location.origin + ":81/stream";
        
        // 1. Setup the Map
        var map = L.map('map').setView([0, 0], 2); // Start at zoom level 2
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);

        var marker = null; // We will add this later when we get data

        // 2. Set the Camera Image
        document.getElementById('cam-stream').src = streamUrl;

        // 3. Function to get Data from ESP32
        function getGPSData() {
            // We ask the ESP32 for the data at this address
            fetch('/api/gps')
                .then(response => response.json()) // Convert text to JSON
                .then(data => {
                    // Update the HTML text
                    document.getElementById('lat').innerText = data.lat.toFixed(6);
                    document.getElementById('lon').innerText = data.lon.toFixed(6);
                    // document.getElementById('speed').innerText = data.speed.toFixed(1);
                    // document.getElementById('sats').innerText = data.satellites;

                    // Update the Map
                    updateMap(data.lat, data.lon);
                })
                .catch(error => {
                    console.log("Error getting data: " + error);
                    // For testing on computer, create fake movement
                    if (isLocal) simulateData(); 
                });
        }

        // 4. Function to move the map marker
        function updateMap(lat, lon) {
            // If GPS is 0,0 it means no signal, so don't move map
            if (lat === 0 && lon === 0) return;

            if (marker === null) {
                // If marker doesn't exist, create it
                marker = L.circleMarker([lat, lon], {
                    color: '#007bff',      // Blue border
                    fillColor: '#007bff',  // Blue fill
                    fillOpacity: 0.5,      // Semi-transparent (The "Ripple" look)
                    radius: 12             // Size
                }).addTo(map);
                
                map.setView([lat, lon], 15); // Zoom in
            } else {
                // If marker exists, just move it
                marker.setLatLng([lat, lon]);
            }
        }

        // 5. Button Functions
        function refreshStream() {
            var img = document.getElementById('cam-stream');
            // Adding a random number (?t=...) forces the browser to reload the image
            img.src = streamUrl + "?t=" + new Date().getTime();
        }

        function toggleFlash() {
            fetch('/control?var=flash&val=toggle');
        }

        // --- SIMULATION (Just for testing on your PC) ---
        var simLat = 40.7128;
        var simLon = -74.0060;
        function simulateData() {
            simLat += 0.0001;
            simLon += 0.0001;
            document.getElementById('lat').innerText = simLat.toFixed(6);
            document.getElementById('lon').innerText = simLon.toFixed(6);
            // document.getElementById('speed').innerText = (Math.random() * 10).toFixed(1);
            updateMap(simLat, simLon);
        }

        // 6. Run the loop
        // Run getGPSData every 2000 milliseconds (2 seconds)
        setInterval(getGPSData, 2000);

    </script>
</body>
</html>
"""

# HTTP Response
def index(req, resp):
    # You can construct an HTTP response completely yourself, having
    yield from resp.awrite(index_web)

# Send camera pictures
def send_frame():
    buf = camera.capture()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n'
           + buf + b'\r\n')
    del buf
    gc.collect()
        
# Video transmission
def video(req, resp):
    yield from picoweb.start_response(resp, content_type="multipart/x-mixed-replace; boundary=frame")
    while True:
        yield from resp.awrite(next(send_frame()))
        gc.collect()


ROUTES = [
    # You can specify exact URI string matches...
    ("/", index),
    ("/video", video),
]


if __name__ == '__main__':
    
    import ulogging as logging
    logging.basicConfig(level=logging.INFO)
    camera_init()
    wifi_connect()

    #Create an app object that contains two decorators
    app = picoweb.WebApp(__name__, ROUTES)
    
    app.run(debug=1, port=80, host="0.0.0.0")
    # debug values:
    # -1 disable all logging
    # 0 (False) normal logging: requests and errors
    # 1 (True) debug logging
    # 2 extra debug logging


