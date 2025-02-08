#include <i2c.h>
#include <i2c_BMP280.h>
#include <Wire.h>
#include <DHT11.h>
#include <SPI.h>
#include <SD.h>
#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>

//Modes of software
bool restrictedMode = false;
bool sdCardSaveMode = true;

//pin setup
BMP280 bmp280;    /// SCL A5, SDA A4, 3,3V.
DHT11 dht11(2);   /// 2 pin, 5V
const short chipSelect = 10;
SoftwareSerial gpsSerial(3, 4); // RX, TX
SoftwareSerial loraSerial(6, 7); // RX, TX

// The TinyGPS++ object
TinyGPSPlus gps;

void bmp280Measurement(float& altitudeArg, char* bmp280Data, size_t dataSize);
void dht11Measurement(char* dht11Data, size_t dataSize);
void gpsMeasurement(char* gpsData, size_t dataSize, const bool mode);
void saveData(const char* data);
void sendLine(const char* input, char* data, size_t dataSize);
void readResponse();

char fileName[13];
float previousAltitude = 0.0;
unsigned long lastTransmissionTime = 0;

void setup() 
{
  Serial.begin(115200);
  gpsSerial.begin(115200);
  loraSerial.begin(115200);

  // Initialize BMP280 sensor
  bmp280.awaitMeasurement();
  if (bmp280.initialize()) {Serial.println("okk");}
  else {
    Serial.println("ERROR\tSetup\tBMP280 sensor is missing");  
  }
  bmp280.setEnabled(0);
  bmp280.triggerMeasurement();

  // Initialize SD card
  if (!SD.begin(chipSelect)) {
    Serial.println("SD_err");
    sdCardSaveMode = false;
  } else {
    // Find the next non-existing txt file
    short fileIndex = 1;
    while (true) {
      snprintf(fileName, sizeof(fileName), "%d.txt", fileIndex);
      if (!SD.exists(fileName)) {
        break;
      }
      fileIndex++;
    }
    Serial.print(fileName);
  }
  // Initialize LoRa module
  loraSerial.println(F("radio set cr 4/5\r\n"));
  delay(1000);
  readResponse();
  loraSerial.println(F("radio set freq 868210000\r\n"));
  delay(1000);
  readResponse();
  loraSerial.println(F("radio set pwr 5\r\n"));
  delay(1000);
  readResponse();

  bmp280.awaitMeasurement();
  bmp280.getAltitude(previousAltitude);
  bmp280.triggerMeasurement();
}

void loop() 
{
  Serial.println("loop");
  float currentAltitude = 0.0;
  char data[80];
  bmp280Measurement(currentAltitude, data, sizeof(data));
  saveData(data);
  sendLine(data, data, sizeof(data));
  memset(data, 0, sizeof(data));
  readResponse();

  dht11Measurement(data, sizeof(data));
  saveData(data);
  memset(data, 0, sizeof(data));

  gpsMeasurement(data, sizeof(data), true);
  saveData(data);
  memset(data, 0, sizeof(data));
  gpsMeasurement(data, sizeof(data), false);
  sendLine(data, data, sizeof(data));
  readResponse();

  if (previousAltitude + 1 > currentAltitude || previousAltitude - 1 < currentAltitude) {
    delay(500);
  }
  previousAltitude = currentAltitude;
}

void bmp280Measurement(float& altitudeArg, char* bmp280Data, size_t dataSize)
{
  Serial.println("bmp");
  bmp280.awaitMeasurement();
  float pressure = 0.0;
  float altitude = 0.0;
  float temperature = 0.0;
  bmp280.getPressure(pressure);
  bmp280.getAltitude(altitude);
  bmp280.getTemperature(temperature);
  bmp280.triggerMeasurement();
  char altitudeStr[20];
  char temperatureStr[10];
  char pressureStr[30];
  dtostrf(altitude, 1, 2, altitudeStr);
  dtostrf(temperature, 1, 2, temperatureStr);
  dtostrf(pressure, 1, 2, pressureStr);
  snprintf(bmp280Data, dataSize, "BMP280\t%s\t%s\t%s\t%lu", temperatureStr, pressureStr, altitudeStr, millis());
  bmp280Data[dataSize - 1] = '\0'; // Ensure null-termination
  Serial.println(bmp280Data);
  altitudeArg = altitude;
}

void dht11Measurement(char* dht11Data, size_t dataSize)
{
  char temperatureStr[10];
  char humidityStr[10];
  dtostrf(dht11.readTemperature(), 1, 2, temperatureStr);
  dtostrf(dht11.readHumidity(), 1, 2, humidityStr);
  snprintf(dht11Data, dataSize, "DHT11\t%s\t%s\t%lu", temperatureStr, humidityStr, millis());
  dht11Data[dataSize - 1] = '\0'; // Ensure null-termination
  Serial.println(dht11Data);
}

void gpsMeasurement(char* gpsData, size_t dataSize, const bool mode)
{
  if (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
    if (gps.location.isUpdated()){
      char latitudeStr[10];
      char longitudeStr[10];
      char altitudeStr[10];
      char speedStr[10];
      dtostrf(gps.location.lat(), 1, 6, latitudeStr);
      dtostrf(gps.location.lng(), 1, 6, longitudeStr);
      dtostrf(gps.altitude.meters(), 1, 2, altitudeStr);
      dtostrf(gps.speed.mps(), 1, 2, speedStr);
      if (mode) {
      snprintf(gpsData, dataSize, "GPS\t%s\t%s\t%s\t%s\t%u\t%lu", latitudeStr, longitudeStr, altitudeStr, speedStr, gps.satellites.value(), millis());
      } else {
      snprintf(gpsData, dataSize, "GPS\t%s\t%s\t%lu", latitudeStr, longitudeStr, millis());
      }
      gpsData[dataSize - 1] = '\0'; // Ensure null-termination
      Serial.println(gpsData);
    }
  }
}

void saveData(const char* data) {
  if (sdCardSaveMode) {
    File dataFile = SD.open(fileName, FILE_WRITE);
    if (dataFile) {
      dataFile.println(data);
      dataFile.close();
    } else {
      Serial.println("ERROR\tsaveData\tFailed to save");
    }
  }
}

void sendLine(const char* input, char* data, size_t dataSize) {
  Serial.println("send");
  if (millis() - lastTransmissionTime < 4000) {
    return;
  } else {
    lastTransmissionTime = millis();
  }
  size_t inputLength = strlen(input);
  if (inputLength > 60) {
    Serial.println(F("input too long"));
    return;
  }
  if (dataSize < inputLength * 2 + 1) {
    // Output buffer is too small
    return;
  }
  //?
  data[0] = '\0';  // Clear the buffer
  for (size_t i = 0; i < inputLength; i++) {
    sprintf(&data[i * 2], "%02X", input[i]);
  }
  data[inputLength * 2] = '\0';  // Null-terminate the output string
  //?
  char cmd[50 + inputLength * 2];
  snprintf(cmd, sizeof(cmd), "radio tx %s 1\r\n", data);

  Serial.println(cmd);
  loraSerial.println(cmd);
}

void readResponse() {
  Serial.println("res");
  char response[50];
  size_t responseSize = sizeof(response);
  size_t index = 0;
  unsigned long startTime = millis();
  while (millis() - startTime < 1000) {
    while (loraSerial.available()) {
      char c = loraSerial.read();
      if (index < responseSize - 1) {
        response[index++] = c;
      }
      if (c == '\n') {  // End of response
        response[index] = '\0';  // Null-terminate the string
        Serial.print(F("response: "));
        Serial.println(response);
        return;
      }
    }
  }
  Serial.println(F("response timeout"));
}