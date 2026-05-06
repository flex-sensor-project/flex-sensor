#include <nrf_to_nrf.h>

nrf_to_nrf radio;

const uint8_t address[5] = {0x12, 0x34, 0x56, 0x78, 0x9A};
uint16_t receivedData[5];
bool thresholdStates[5] = {false, false, false, false, false};

const float VOLTAGE_THRESHOLD = 1.4f;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  
  uint32_t t = millis();
  while (!Serial && millis() - t < 3000);

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

  radio.writeAckPayload(1, &thresholdStates, sizeof(thresholdStates));
}

void loop() {
  if (radio.available()) {
    radio.read(&receivedData, sizeof(receivedData));
    
    for (int i = 0; i < 5; i++) {
      float currentVoltage = (receivedData[i] / 4095.0f) * 3.3f;
      thresholdStates[i] = currentVoltage > VOLTAGE_THRESHOLD;
    }
    
    radio.writeAckPayload(1, &thresholdStates, sizeof(thresholdStates));

    // Send exactly 10 raw bytes to the PC over USB
    Serial.write((uint8_t*)&receivedData, sizeof(receivedData));
  }
}