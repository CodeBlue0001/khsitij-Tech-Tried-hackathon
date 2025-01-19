#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <SoftwareSerial.h>
#include <Adafruit_Fingerprint.h>
#include <SPI.h>
#include <Base64.h> // Include Base64 library for encoding

// WiFi credentials
const char* ssid = "DEV_WITH_ME";
const char* password = "01100110";

// Server URL
const char* serverUrl = "http://10.147.49.92:3000/vote";

// OLED Display Configuration
#define i2c_Address 0x3C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Fingerprint Sensor setup
SoftwareSerial mySerial1(D5, D6); // RX, TX for Sensor 1 (TMCP)
SoftwareSerial mySerial2(D7, D0); // RX, TX for Sensor 2 (BJP)
Adafruit_Fingerprint finger1(&mySerial1); // Fingerprint Sensor for TMCP
Adafruit_Fingerprint finger2(&mySerial2); // Fingerprint Sensor for BJP

// WiFi Client
WiFiClient wifiClient;

// Initialization status
bool sensor1Ready = false;
bool sensor2Ready = false;

bool isSensorBlocked = false;  // Global flag to block/unblock both sensors

// Function prototypes
void displayFeedback(String message);
void blockSensors();
void unblockSensors();
String getFingerprintTemplate(Adafruit_Fingerprint& fingerSensor);
void sendTemplateToServer(String fingerprintTemplate, String party);

void setup() {
    Serial.begin(115200);

    // Initialize OLED
    Wire.begin(D2, D1);
    if (!display.begin(i2c_Address)) {
        Serial.println("OLED Initialization Failed");
        while (true);
    }
    display.clearDisplay();
    display.setTextColor(SH110X_WHITE);
    display.setTextSize(1);
    display.display();

    // Display "System Power On"
    displayFeedback("\n\n\n  SYSTEM POWER ON");
    delay(2000);

    // Connect to Wi-Fi
    connectToWiFi();

    // Initialize fingerprint sensors
    initializeSensors();
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        if (!sensor1Ready || !sensor2Ready) {
            displayFeedback("\n\nReinitializing Sensors...");
            initializeSensors();
        }

        if (sensor1Ready && sensor2Ready) {
            displayFeedback("\n\n Choose your party!");
            delay(1000);

            collectAndSendFingerprint(finger1, "TMCP");
            collectAndSendFingerprint(finger2, "BJP");
        }
    } else {
        displayFeedback("\n\n WiFi disconnected");
        WiFi.reconnect();
        delay(5000);
    }
    delay(100);
}

// Function to connect to Wi-Fi
void connectToWiFi() {
    displayFeedback("\n\n Connecting to WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    displayFeedback("\n\n Connected to WiFi");
    Serial.println("Connected to WiFi");
}

// Function to initialize fingerprint sensors
void initializeSensors() {
    sensor1Ready = false;
    sensor2Ready = false;

    finger1.begin(57600);
    finger2.begin(57600);

    if (finger1.verifyPassword()) {
        sensor1Ready = true;
        Serial.println("Sensor 1 Ready (TMCP)");
    } else {
        Serial.println("Sensor 1 Not Found (TMCP)");
    }

    if (finger2.verifyPassword()) {
        sensor2Ready = true;
        Serial.println("Sensor 2 Ready (BJP)");
    } else {
        Serial.println("Sensor 2 Not Found (BJP)");
    }

    if (sensor1Ready && sensor2Ready) {
        displayFeedback("\n\n Sensors Initialized");
        delay(1000);
    } else if (!sensor1Ready && !sensor2Ready) {
        displayFeedback("\n\n Both Sensors Failed");
        
    } else if (!sensor1Ready) {
        displayFeedback("\n\n Sensor 1 Failed");
        initializeSensors();
        delay(100);
    } else {
        displayFeedback("\n\n Sensor 2 Failed");
        initializeSensors();
        delay(100);
    }
}

// Function to collect fingerprint template and send it to the server
void collectAndSendFingerprint(Adafruit_Fingerprint& fingerSensor, String party) {
    int p = fingerSensor.getImage();  // Capture the fingerprint image
    bool serverResponse = false;

    if (isSensorBlocked) {
        Serial.println("Sensors are blocked due to ongoing fingerprint verification process.");
        return;  // If sensors are blocked, don't proceed
    }

    if (p == FINGERPRINT_NOFINGER) {
        Serial.println("No finger detected.");
        return;  // No finger detected
    }

    if (p == FINGERPRINT_OK) {
        Serial.println("Fingerprint image captured successfully.");

        p = fingerSensor.image2Tz();  // Convert the image to a template
        if (p == FINGERPRINT_OK) {
            Serial.println("Fingerprint image converted to template.");

            p = fingerSensor.storeModel(1);  // Store the model temporarily
            if (p == FINGERPRINT_OK) {
                Serial.println("Fingerprint template stored successfully.");

                // Show feedback for the chosen party
                displayFeedback("\n\n\n You choose " + party);
                delay(3000);
                displayFeedback("\n\n\n Please wait...");
                delay(3000);

                // Block both sensors before proceeding with the server communication
                blockSensors();

                // Get the actual fingerprint template data (raw data, array of integers)
                uint8_t templateBuffer[768]; // Buffer for storing fingerprint template
                int p = fingerSensor.getModel();

                if (p == FINGERPRINT_OK) {
                    Serial.println("Fingerprint model retrieved successfully!");

                    // Fill templateBuffer with fingerprint template data (depends on the library)
                    // For now, assume the templateBuffer is populated.

                    // Convert the buffer to a string for transmission
                    String fingerprintTemplate = "";
                    for (int i = 0; i < 768; i++) { // Use the actual size of the buffer
                        fingerprintTemplate += String(templateBuffer[i], HEX); // Hexadecimal encoding
                    }

                    // Base64 encode the fingerprint template
                    String fingerprintTemplateBase64 = base64::encode(fingerprintTemplate);

                    // Send to server
                    sendTemplateToServer(fingerprintTemplateBase64, party);

                } else {
                    Serial.println("Failed to retrieve fingerprint model.");
                }

                unblockSensors();
            } else {
                Serial.println("Error storing fingerprint template.");
            }
        } else {
            Serial.println("Error processing fingerprint.");
        }
    } else {
        Serial.println("Error capturing fingerprint.");
    }
}

// Function to send fingerprint template to the server
void sendTemplateToServer(String fingerprintTemplate, String party) {
    HTTPClient http;
    http.begin(wifiClient, serverUrl);
    http.addHeader("Content-Type", "application/json");

    String httpRequestData = "{\"fingerprint\":\"" + fingerprintTemplate + "\",\"party\":\"" + party + "\"}";

    int httpResponseCode = http.POST(httpRequestData);

    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.printf("HTTP Response Code: %d\n", httpResponseCode);
        Serial.println("Server Response: " + response);

        if (httpResponseCode == 200) {
            displayFeedback("Vote cast successfully for " + party);
            delay(2000);
        } else if (httpResponseCode == 404) {
            displayFeedback("User is not registered!!.");
            delay(2000);
        } else if (httpResponseCode == 409) {
            displayFeedback("Already processing. Try again.");
            delay(2000);
        } else if (httpResponseCode == 400) {
            displayFeedback("User already voted.");
            delay(2000);
        } else if (httpResponseCode == 500) {
            displayFeedback("Credentials are missing!!");
            delay(2000);
        }
    } else {
        Serial.printf("HTTP request failed. Error code: %d\n", httpResponseCode);
    }

    http.end();
}

// Function to block both fingerprint sensors
void blockSensors() {
    isSensorBlocked = true;
    Serial.println("Both fingerprint sensors are now blocked.");
}

// Function to unblock both fingerprint sensors
void unblockSensors() {
    isSensorBlocked = false;
    Serial.println("Both fingerprint sensors are now unblocked.");
}

// Function to display feedback on OLED
void displayFeedback(String message) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.print(message);
    display.display();
}
