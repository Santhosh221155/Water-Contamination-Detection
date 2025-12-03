#include <WiFi.h>
#include <PubSubClient.h>

// ADC pins (ESP32 ADC1 - stable for WiFi use)
#define PIN_PH          36   // VP
#define PIN_SULPHATE    39   // VN
#define PIN_HARDNESS    34
#define PIN_CONDUCT     35
#define PIN_TDS         32
#define PIN_TURBIDITY   33

// WiFi & MQTT
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "test.mosquitto.org";

const char* PUBLISH_TOPIC = "tn/water/telemetry";

WiFiClient espClient;
PubSubClient client(espClient);

// Sensor range mapping (min, max) for potentiometers → real scale
struct Range {
  float min;
  float max;
};

Range sensorRanges[] = {
  {5.0,  9.5},    // pH
  {60,  900},     // Sulphate
  {40,  800},     // Hardness
  {150, 3000},    // Conductivity
  {100, 2000},    // TDS
  {1.0, 25.0}     // Turbidity
};

void setup_wifi() {
  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(300);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected ✔");
    Serial.println("IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n⚠ WiFi FAILED! Check Wokwi settings.");
  }
}

void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    String clientId = "ESP32-" + String(random(9999));
    if (client.connect(clientId.c_str())) {
      Serial.println("MQTT connected ✔");
    } else {
      delay(1000);
    }
  }
}

float readMappedValue(int pin, Range r) {
  int raw = analogRead(pin);
  float mapped = map(raw, 0, 4095, r.min * 100, r.max * 100) / 100.0;
  return mapped;
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) reconnect_mqtt();
  client.loop();

  // Read all sensors
  float pH          = readMappedValue(PIN_PH, sensorRanges[0]);
  float sulphate    = readMappedValue(PIN_SULPHATE, sensorRanges[1]);
  float hardness    = readMappedValue(PIN_HARDNESS, sensorRanges[2]);
  float conductivity= readMappedValue(PIN_CONDUCT, sensorRanges[3]);
  float tds         = readMappedValue(PIN_TDS, sensorRanges[4]);
  float turbidity   = readMappedValue(PIN_TURBIDITY, sensorRanges[5]);

  // Create JSON string for ML backend
  String json = "{";
  json += "\"pH\":" + String(pH, 2) + ",";
  json += "\"Sulphate\":" + String(sulphate, 2) + ",";
  json += "\"Hardness\":" + String(hardness, 2) + ",";
  json += "\"Conductivity\":" + String(conductivity, 2) + ",";
  json += "\"TDS\":" + String(tds, 2) + ",";
  json += "\"Turbidity\":" + String(turbidity, 2);
  json += "}";

  Serial.println("📤 Sending: " + json);

  client.publish(PUBLISH_TOPIC, json.c_str());

  delay(1000);  // send every second
}
