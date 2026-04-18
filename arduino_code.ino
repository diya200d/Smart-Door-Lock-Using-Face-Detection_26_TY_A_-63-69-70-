#include <WiFi.h>
#include <WebServer.h>

const char* WIFI_SSID     = "Galaxy F41048C";
const char* WIFI_PASSWORD = "11111111";

// Static IP — never changes
// Use the same 192.168.0.x LAN as your laptop (e.g., 192.168.0.112)
IPAddress local_IP(192, 168, 0, 118);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

#define RELAY_PIN  12
#define GREEN_LED  13
#define RED_LED    14

#define UNLOCK_DURATION_MS  4000   // 4 seconds unlock hold

WebServer server(80);

bool isUnlocked = false;
unsigned long unlockTime = 0;

void setLocked() {
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED,   HIGH);
  isUnlocked = false;
  Serial.println("[LOCK] Door locked.");
}

void setUnlocked() {
  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED,   LOW);
  isUnlocked = true;
  unlockTime = millis();
  Serial.println("[UNLOCK] Door unlocked for 4 seconds.");
}

void handleUnlock() {
  setUnlocked();
  server.send(200, "text/plain", "unlocked");
}

void handleLock() {
  // Only lock if not currently in an unlock window
  if (!isUnlocked) {
    setLocked();
  }
  server.send(200, "text/plain", "locked");
}

void handleStatus() {
  server.send(200, "text/plain", isUnlocked ? "unlocked" : "locked");
}

void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED,   OUTPUT);

  setLocked();

  WiFi.config(local_IP, gateway, subnet);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempts++;
    if (attempts > 40) {
      Serial.println("\n[ERROR] WiFi failed. Restarting...");
      ESP.restart();
    }
  }

  Serial.println("\n[WiFi] Connected!");
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());

  server.on("/unlock", HTTP_GET, handleUnlock);
  server.on("/lock",   HTTP_GET, handleLock);
  server.on("/status", HTTP_GET, handleStatus);
  server.begin();
  Serial.println("[HTTP] Server ready.");

  // Blink green twice = ready
  for (int i = 0; i < 2; i++) {
    digitalWrite(GREEN_LED, HIGH); delay(200);
    digitalWrite(GREEN_LED, LOW);  delay(200);
  }
  digitalWrite(RED_LED, HIGH);
}

void loop() {
  server.handleClient();

  // Auto-lock after unlock duration
  if (isUnlocked && (millis() - unlockTime >= UNLOCK_DURATION_MS)) {
    Serial.println("[AUTO-LOCK] Time expired. Locking.");
    setLocked();
  }
}
