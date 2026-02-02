#include <WiFi.h>

// 1. Replace with your Network Credentials
const char* ssid = "Vedashri's iPhone";
const char* password = "vedashri18";

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  
  // 2. Set WiFi mode to Station (connects to an existing AP)
  WiFi.mode(WIFI_STA); 
  
  Serial.print("Connecting to WiFi..");
  
  // 3. Begin connection
  WiFi.begin(ssid, password);

  // 4. Loop until connected
  // This blocks the setup until a connection is established
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // 5. Success! Print the assigned IP Address
  Serial.println("\nConnected to the WiFi network");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal Strength (RSSI): ");
  Serial.println(WiFi.RSSI());
}

void loop() {
  // Your code here
  // Check connection status periodically if needed
  if (WiFi.status() == WL_CONNECTED) {
    // Connection is healthy
  } else {
    // Connection lost
  }
}