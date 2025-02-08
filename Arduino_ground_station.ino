#include <SoftwareSerial.h>

#define BAUD_RATE 115200  // Default baud rate from manual

// Define the frequency to be set (in Hz)
long frequency = 868210000;  // Example: 868.210 MHz

SoftwareSerial Serial1(6, 7);

void readResponse(bool isHex=false);
String hexToString(String& hexInput);

void setup() {
  Serial.begin(9600);           // Start serial communication for feedback
  Serial.println("test");
  Serial1.begin(BAUD_RATE); // Start UART communication

  // Wait for the serial monitor to be ready
  while (!Serial) {
    delay(100);
  }

  Serial.println("WLR089 get frequency");
  String cmd = "radio get freq\r\n";  // Construct the command
  Serial.print("Sending command: ");
  Serial.println(cmd);
  Serial1.print(cmd);
  delay(2000);
  readResponse();

  Serial.println("WLR089 Set frequency");
  cmd = "radio set freq " + String(frequency) + "\r\n";  // Construct the command
  Serial.print("Sending command: ");
  Serial.println(cmd);
  // Send the command to the WLR089 module over UART
  Serial1.print(cmd);
  delay(2000);  // Give more time for the module to process (increased delay)
  // Echo back the response from the module
  readResponse();

  Serial.println("WLR089 set LoRa communication");
  cmd = "radio set mod lora\r\n";  // Construct the command
  Serial.print("Sending command: ");
  Serial.println(cmd);
  Serial1.print(cmd);
  delay(2000);
  readResponse();

  Serial.println("Set Continuous Reception mode");
  cmd = "radio rx 0\r\n";
  Serial.print("Sending command: ");
  Serial.println(cmd);
  Serial1.print(cmd);
  delay(2000);
  readResponse();

  /*Serial.println("Send message");
  cmd = "radio tx 68656C6C6F5F776F726C64 5\r\n";
  Serial.print("Sending command: ");
  Serial.println(cmd);
  Serial1.print(cmd);
  delay(2000);
  readResponse();*/
}

void loop() {
  // Continuously check for responses from the WLR089 module
  readResponse(true);
  delay(500);  // Adjust delay as needed
}

// Function to read and print the module's response
void readResponse(bool isHex=false) {
  if (Serial1.available()) {
    String response = Serial1.readStringUntil('\n');  // Read response line by line
    Serial.print("Module Response: ");
    Serial.println(response);
    if(isHex) {
      // Transform hex data back into readable text
      String readableText = hexToString(response);
      Serial.print("Readable Text: ");
      Serial.println(readableText);
    }
    Serial.println();
  }
}

String hexToString(String& hexInput) {
  String textString;
  // Remove "radio_rx " from the input string
  hexInput.remove(0, 9);
  for (int i = 0; i < hexInput.length(); i += 2) {
    String hexChar = hexInput.substring(i, i + 2);
    char charValue = (char) strtol(hexChar.c_str(), NULL, 16);
    textString += charValue;
  }
  return textString;
}