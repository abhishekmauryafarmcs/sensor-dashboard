#include "DHT.h"
#include <Wire.h>
#include <BH1750.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define DHTPIN 4
#define DHTTYPE DHT11
#define SDA_PIN 21
#define SCL_PIN 22

// Ultrasonic sensor pins
const int trigPin = 5;
const int echoPin = 18;

// Define sound speed in cm/uS
#define SOUND_SPEED 0.034
#define CM_TO_INCH 0.393701

// Soil moisture sensor variables
int _moisture, sensor_analog;
const int sensor_pin = 34;  // Soil moisture sensor O/P pin

// WiFi credentials
const char* ssid = "ABHISHEK FarmCS";
const char* password = "123456789";

// Your local server address
const char* serverName = "http://192.168.1.4/dht11/test_data.php";

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;
bool lightSensorFound = false;

// Ultrasonic sensor variables
long duration;
float distanceCm;

void setup() {
  Serial.begin(115200);
  Serial.println("\nInitializing...");
  
  // Initialize pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(sensor_pin, INPUT);
  
  // Initialize I2C
  Wire.begin(SDA_PIN, SCL_PIN);
  
  // Initialize DHT11
  dht.begin();
  Serial.println("DHT11 Initialized");
  
  // Initialize BH1750 with error checking
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("BH1750 Light Sensor Initialized");
    lightSensorFound = true;
  } else {
    Serial.println("Error initializing BH1750 Light Sensor! Check your wiring...");
    lightSensorFound = false;
  }
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Read DHT11 sensor
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  // Read light sensor with error checking
  float lux = 0;
  if (lightSensorFound) {
    lux = lightMeter.readLightLevel();
    if (lux < 0) {
      Serial.println("Error reading light sensor!");
      lux = 0;
    }
  }
  
  // Read ultrasonic sensor
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distanceCm = duration * SOUND_SPEED/2;
  
  // Read soil moisture sensor
  sensor_analog = analogRead(sensor_pin);
  _moisture = ( 100 - ( (sensor_analog/4095.00) * 100 ) );
  
  // Print all sensor readings to Serial Monitor
  Serial.println("\n--- Sensor Readings ---");
  
  // DHT11 readings
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT11 sensor!");
  } else {
    Serial.print("Temperature: ");
    Serial.print(t);
    Serial.print("°C, Humidity: ");
    Serial.print(h);
    Serial.println("%");
  }
  
  // Light sensor readings
  Serial.print("Light: ");
  Serial.print(lux);
  Serial.println(" lx");
  
  // Distance readings
  Serial.print("Distance: ");
  Serial.print(distanceCm);
  Serial.println(" cm");
  
  // Moisture readings
  Serial.print("Soil Moisture: ");
  Serial.print(_moisture);
  Serial.println("%");

  // Check WiFi connection status
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    http.begin(serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    // Send HTTP POST request with all sensor data
    String httpRequestData = "temperature=" + String(t) + 
                           "&humidity=" + String(h) + 
                           "&light=" + String(lux) + 
                           "&distance=" + String(distanceCm) +
                           "&moisture=" + String(_moisture);
    
    // Print request data for debugging
    Serial.print("Sending data: ");
    Serial.println(httpRequestData);
    
    int httpResponseCode = http.POST(httpRequestData);
    
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    }
    else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  }
  else {
    Serial.println("WiFi Disconnected");
    WiFi.begin(ssid, password);
  }
  
  delay(2000);  // Wait for 2 seconds before next reading
}