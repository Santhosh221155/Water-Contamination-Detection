#include <WiFi.h>
#include <PubSubClient.h>

// Pin definitions (Using ADC1 only for WiFi compatibility)
const int POT_PH = 36;          // VP
const int POT_SULPHATE = 39;    // VN
const int POT_HARDNESS = 34;
const int POT_CONDUCTIVITY = 35;
const int POT_TDS = 32;
const int POT_TURBIDITY = 33;

const int LED_GREEN = 13; 
const int LED_RED = 12;

// Wi-Fi & MQTT Credentials
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "test.mosquitto.org";
const char* mqtt_topic = "water_quality/telemetry";

WiFiClient espClient;
PubSubClient client(espClient);

// Sensor ranges
struct SensorRange {
    float min;
    float max;
};

SensorRange ranges[] = {
    {5.5, 8.8},      
    {69, 496},       
    {66, 281},       
    {152, 895},      
    {137, 1178},     
    {1.3, 9.4}      
};

void setup_wifi() {
    delay(10);
    Serial.println("--- SETUP WIFI START ---");
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    int timeout = 0;
    while (WiFi.status() != WL_CONNECTED && timeout < 20) {
        delay(500);
        Serial.print(".");
        timeout++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("");
        Serial.println("WiFi connected");
        Serial.println("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n❌ WiFi Connection Failed! Check Wokwi Gateway.");
    }
}

int predict_water_quality(float pH, float sulphate, float hardness, 
                          float conductivity, float tds, float turbidity) {
    if (pH < 6.0 || pH > 8.5) return 0;
    if (turbidity > 6.0) return 0;
    if (tds > 900) return 0;
    return 1; 
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_RED, OUTPUT);
    analogReadResolution(12); 

    setup_wifi();
    client.setServer(mqtt_server, 1883);
}

float readSensor(int pin, int sensorIndex) {
    int rawValue = analogRead(pin);
    float value = map(rawValue, 0, 4095, 
                     ranges[sensorIndex].min * 100, 
                     ranges[sensorIndex].max * 100) / 100.0;
    return value;
}

void loop() {
    // Non-blocking MQTT connection
    if (!client.connected()) {
        String clientId = "ESP32Client-";
        clientId += String(random(0xffff), HEX);
        if (client.connect(clientId.c_str())) {
             Serial.println("MQTT Connected");
        }
    } else {
        client.loop();
    }

    float pH = readSensor(POT_PH, 0);
    float sulphate = readSensor(POT_SULPHATE, 1);
    float hardness = readSensor(POT_HARDNESS, 2);
    float conductivity = readSensor(POT_CONDUCTIVITY, 3);
    float tds = readSensor(POT_TDS, 4);
    float turbidity = readSensor(POT_TURBIDITY, 5);

    int prediction = predict_water_quality(
        pH, sulphate, hardness, conductivity, tds, turbidity
    );

    if (prediction == 1) {
        digitalWrite(LED_GREEN, HIGH);
        digitalWrite(LED_RED, LOW);
    } else {
        digitalWrite(LED_GREEN, LOW);
        digitalWrite(LED_RED, HIGH);
    }

    // Create JSON string
    String json = "{";
    json += "\"pH\":" + String(pH, 1) + ",";
    json += "\"Sulphate\":" + String(sulphate, 0) + ",";
    json += "\"Hardness\":" + String(hardness, 0) + ",";
    json += "\"Conductivity\":" + String(conductivity, 0) + ",";
    json += "\"TDS\":" + String(tds, 0) + ",";
    json += "\"Turbidity\":" + String(turbidity, 1) + ",";
    json += "\"prediction\":" + String(prediction) + ",";
    json += "\"prediction_text\":\"" + String(prediction == 1 ? "Safe" : "Unsafe") + "\"";
    json += "}";

    Serial.println(json);
    
    if (client.connected()) {
        client.publish(mqtt_topic, json.c_str());
    }

    delay(2000);
}
