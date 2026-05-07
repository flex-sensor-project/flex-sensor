#include <nrf_to_nrf.h>

nrf_to_nrf radio;

const uint8_t address[5] = {0x12, 0x34, 0x56, 0x78, 0x9A};
uint16_t receivedData[5];
bool thresholdStates[5] = {false, false, false, false, false};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);

  // Flash LED to show boot
  for (int i = 0; i < 4; i++) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(150);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(150);
  }

  sd_softdevice_disable();
  delay(100);

  if (!radio.begin()) {
    while (1) {
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
      delay(100);
    }
  }

  radio.setChannel(100);           
  radio.setDataRate(NRF_1MBPS);
  radio.enableDynamicPayloads();
  radio.setAutoAck(true);         
  radio.enableAckPayload();
  
  radio.openReadingPipe(1, address);
  radio.startListening();

  // Load the initial empty ack payload
  radio.writeAckPayload(1, &thresholdStates, sizeof(thresholdStates));
}

void loop() {
  // Step 1: Check for radio data from the Server
  if (radio.available()) {
    radio.read(&receivedData, sizeof(receivedData));
    
    // Send 10 bytes of raw ADC over USB to Python
    Serial.write((uint8_t*)&receivedData, sizeof(receivedData));
  }

  // Step 2: Check for incoming USB data from Python
  // We wait until all 5 bytes have arrived
  if (Serial.available() >= 5) {
    
    uint8_t incomingBytes[5];
    Serial.readBytes(incomingBytes, 5);
    
    // Convert the bytes back into true or false booleans
    for (int i = 0; i < 5; i++) {
      if (incomingBytes[i] > 0) {
        thresholdStates[i] = true;
      } else {
        thresholdStates[i] = false;
      }
    }
    
    // Load the new states into the Ack Payload for the next radio transmission
    radio.writeAckPayload(1, &thresholdStates, sizeof(thresholdStates));
  }
}