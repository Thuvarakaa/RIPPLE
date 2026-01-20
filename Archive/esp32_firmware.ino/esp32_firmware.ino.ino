/**
 * ESP32-CAM RIPPLE Firmware
 * * Hardware Requirements:
 * 1. ESP32-CAM (AI-Thinker Model)
 * 2. GPS Module (NEO-6M or BN-220)
 * * Wiring:
 * - GPS VCC -> 5V (or 3.3V depending on module)
 * - GPS GND -> GND
 * - GPS TX  -> ESP32 GPIO 13
 * - GPS RX  -> ESP32 GPIO 14
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <TinyGPS++.h>

// ==========================================
// CONFIGURATION (EDIT THIS!)
// ==========================================
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// ==========================================
// PIN DEFINITIONS (AI-Thinker ESP32-CAM)
// ==========================================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// GPS Pins (We use Serial1)
#define GPS_RX_PIN 13 // Connect to GPS TX
#define GPS_TX_PIN 14 // Connect to GPS RX
#define GPS_BAUD 9600

// Flashlight Pin
#define FLASH_GPIO_NUM 4

// ==========================================
// GLOBALS
// ==========================================
WebServer server(80);
TinyGPSPlus gps;
HardwareSerial gpsSerial(1); // UART 1

// ==========================================
// CAMERA FUNCTIONS
// ==========================================
void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Low quality for smooth streaming over WiFi
  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 12;          // 0-63, lower is better quality
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_CIF;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

// ==========================================
// SERVER HANDLERS
// ==========================================

// 1. Root Handler: Tells you the system is alive
void handleRoot() {
  server.send(200, "text/plain", "RIPPLE System Online. Open index.html on your computer.");
}

// 2. GPS API: Returns JSON data
void handleGPS() {
  String json = "{";
  json += "\"lat\":" + String(gps.location.isValid() ? gps.location.lat() : 0.0, 6) + ",";
  json += "\"lon\":" + String(gps.location.isValid() ? gps.location.lng() : 0.0, 6) + ",";
  json += "\"speed\":" + String(gps.speed.isValid() ? gps.speed.kmph() : 0.0) + ",";
  json += "\"satellites\":" + String(gps.satellites.isValid() ? gps.satellites.value() : 0);
  json += "}";
  server.send(200, "application/json", json);
}

// 3. Control API: Toggle Flashlight
void handleControl() {
  if (server.hasArg("var") && server.hasArg("val")) {
    if (server.arg("var") == "flash") {
       // Toggle LED (Pin 4)
       // Note: ESP32-CAM flash logic can vary, usually HIGH is ON
       static bool flashState = false;
       flashState = !flashState;
       pinMode(FLASH_GPIO_NUM, OUTPUT);
       digitalWrite(FLASH_GPIO_NUM, flashState ? HIGH : LOW);
    }
  }
  server.send(200, "text/plain", "OK");
}

// 4. Video Stream Handler (MJPEG)
// Note: This runs on port 81 usually, but for simplicity here we serve it via standard method or specific port.
// For robust streaming, we use a raw socket loop on a separate function.
void handleStream() {
  WiFiClient client = server.client();
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
  server.sendContent(response);

  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }
    
    // Write the frame
    server.sendContent("--frame\r\n");
    server.sendContent("Content-Type: image/jpeg\r\n");
    server.sendContent("Content-Length: " + String(fb->len) + "\r\n\r\n");
    client.write(fb->buf, fb->len);
    server.sendContent("\r\n");
    
    esp_camera_fb_return(fb);
    
    // Simple delay to control framerate
    delay(50); 
  }
}

// ==========================================
// MAIN SETUP & LOOP
// ==========================================

void setup() {
  Serial.begin(115200);
  
  // 1. Start GPS Serial
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  // 2. Start Camera
  setupCamera();

  // 3. Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP Address: ");
  Serial.println(WiFi.localIP());

  // 4. Start Web Server Routes
  server.on("/", handleRoot);
  server.on("/api/gps", handleGPS);
  server.on("/control", handleControl);
  server.on("/stream", handleStream); // Stream on main port 80 for simplicity

  server.begin();
}

void loop() {
  // Handle Incoming Web Requests
  server.handleClient();
  
  // Read Incoming GPS Data constantly
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }
}