// ESP32 Water Quality Monitor with On-Board ML Prediction
// This code runs the ML model directly on ESP32

#include <Arduino.h>

// Include the ML model (choose one)
// Option 1: Simple rule-based (RECOMMENDED - small and fast)
// Option 2: Random Forest (better accuracy but larger)

// ============================================================
// OPTION 1: SIMPLE RULE-BASED CLASSIFIER (RECOMMENDED)
// ============================================================

int predict_water_quality(float pH, float sulphate, float hardness, 
                          float conductivity, float tds, float turbidity) {
    // Safe ranges for Tamil Nadu water quality
    const float pH_MIN = 6.5f;
    const float pH_MAX = 8.5f;
    const float SULPHATE_MIN = 100.0f;
    const float SULPHATE_MAX = 400.0f;
    const float HARDNESS_MIN = 80.0f;
    const float HARDNESS_MAX = 250.0f;
    const float CONDUCTIVITY_MIN = 200.0f;
    const float CONDUCTIVITY_MAX = 800.0f;
    const float TDS_MIN = 200.0f;
    const float TDS_MAX = 1000.0f;
    const float TURBIDITY_MIN = 1.5f;
    const float TURBIDITY_MAX = 5.0f;
    
    // Check if all parameters are within safe ranges
    if (pH >= pH_MIN && pH <= pH_MAX &&
        sulphate >= SULPHATE_MIN && sulphate <= SULPHATE_MAX &&
        hardness >= HARDNESS_MIN && hardness <= HARDNESS_MAX &&
        conductivity >= CONDUCTIVITY_MIN && conductivity <= CONDUCTIVITY_MAX &&
        tds >= TDS_MIN && tds <= TDS_MAX &&
        turbidity >= TURBIDITY_MIN && turbidity <= TURBIDITY_MAX) {
        return 1; // Safe
    } else {
        return 0; // Unsafe
    }
}

// ============================================================
// SENSOR READING SIMULATION (using potentiometers)
// ============================================================

// Pin definitions for potentiometers
const int POT_PH = 34;          // GPIO34 (ADC1_CH6)
const int POT_SULPHATE = 35;    // GPIO35 (ADC1_CH7)
const int POT_HARDNESS = 32;    // GPIO32 (ADC1_CH4)
const int POT_CONDUCTIVITY = 33; // GPIO33 (ADC1_CH5)
const int POT_TDS = 25;         // GPIO25 (ADC2_CH8)
const int POT_TURBIDITY = 26;   // GPIO26 (ADC2_CH9)

// LED pins
const int LED_GREEN = 2;  // Safe
const int LED_RED = 4;    // Unsafe

// Sensor value ranges (for mapping potentiometer readings)
struct SensorRange {
    float min;
    float max;
};

SensorRange ranges[] = {
    {5.5, 8.8},      // pH
    {69, 496},       // Sulphate
    {66, 281},       // Hardness
    {152, 895},      // Conductivity
    {137, 1178},     // TDS
    {1.3, 9.4}       // Turbidity
};

void setup() {
    Serial.begin(115200);
    
    // Configure LED pins
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_RED, OUTPUT);
    
    // Configure ADC
    analogReadResolution(12); // 12-bit ADC (0-4095)
    
    Serial.println("ESP32 Water Quality Monitor - On-Board ML");
    Serial.println("==========================================");
    delay(1000);
}

float readSensor(int pin, int sensorIndex) {
    int rawValue = analogRead(pin);
    // Map ADC value (0-4095) to sensor range
    float value = map(rawValue, 0, 4095, 
                     ranges[sensorIndex].min * 100, 
                     ranges[sensorIndex].max * 100) / 100.0;
    return value;
}

void loop() {
    // Read sensor values from potentiometers
    float pH = readSensor(POT_PH, 0);
    float sulphate = readSensor(POT_SULPHATE, 1);
    float hardness = readSensor(POT_HARDNESS, 2);
    float conductivity = readSensor(POT_CONDUCTIVITY, 3);
    float tds = readSensor(POT_TDS, 4);
    float turbidity = readSensor(POT_TURBIDITY, 5);
    
    // Run ML prediction on ESP32
    int prediction = predict_water_quality(pH, sulphate, hardness, 
                                          conductivity, tds, turbidity);
    
    // Control LEDs
    if (prediction == 1) {
        digitalWrite(LED_GREEN, HIGH);
        digitalWrite(LED_RED, LOW);
    } else {
        digitalWrite(LED_GREEN, LOW);
        digitalWrite(LED_RED, HIGH);
    }
    
    // Output JSON with prediction
    Serial.print("{");
    Serial.print("\"pH\":");
    Serial.print(pH, 1);
    Serial.print(",\"Sulphate\":");
    Serial.print(sulphate, 0);
    Serial.print(",\"Hardness\":");
    Serial.print(hardness, 0);
    Serial.print(",\"Conductivity\":");
    Serial.print(conductivity, 0);
    Serial.print(",\"TDS\":");
    Serial.print(tds, 0);
    Serial.print(",\"Turbidity\":");
    Serial.print(turbidity, 1);
    Serial.print(",\"prediction\":");
    Serial.print(prediction);
    Serial.print(",\"prediction_text\":\"");
    Serial.print(prediction == 1 ? "Safe" : "Unsafe");
    Serial.println("\"}");
    
    delay(2000); // Send data every 2 seconds
}
