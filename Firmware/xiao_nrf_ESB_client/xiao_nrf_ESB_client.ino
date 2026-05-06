#include <nrf_to_nrf.h>

nrf_to_nrf radio;

const uint8_t address[5] = {0x12, 0x34, 0x56, 0x78, 0x9A};
uint16_t receivedData[5];
bool thresholdStates[5] = {false, false, false, false, false};

const float VOLTAGE_THRESHOLD = 1.4f;

uint32_t packetCount = 0;
uint32_t lastCalcTime = 0;
uint32_t maxJitter = 0;
uint32_t lastPacketMs = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  
  uint32_t t = millis();
  while (!Serial && millis() - t < 3000);

  Serial.println("\n--- ESB Client Receiver ---");
  for (int i = 0; i < 4; i++) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(150);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(150);
  }

  Serial.println("Initializing radio...");

  sd_softdevice_disable();
  delay(100);

  if (!radio.begin()) {
    Serial.println("FATAL: radio.begin() failed");
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

  lastCalcTime = millis();
  Serial.println("Radio OK — listening.");
}

void loop() {
  if (radio.available()) {
    radio.read(&receivedData, sizeof(receivedData));
    
    for (int i = 0; i < 5; i++) {
      float currentVoltage = (receivedData[i] / 4095.0f) * 3.3f;
      thresholdStates[i] = currentVoltage > VOLTAGE_THRESHOLD;
    }
    
    radio.writeAckPayload(1, &thresholdStates, sizeof(thresholdStates));

    uint32_t now = millis();
    uint32_t interval = now - lastPacketMs;
    if (interval > maxJitter) maxJitter = interval;
    lastPacketMs = now;

    packetCount++;
  }

  uint32_t now = millis();
  if (now - lastCalcTime >= 1000) {
    uint32_t pps = packetCount;
    uint32_t jitter = maxJitter;
    packetCount = 0;
    maxJitter = 0;
    lastCalcTime = now;

    //Serial.print("PPS: ");
    Serial.print(pps);
    //Serial.print(" | MaxJitter: ");
    //Serial.print(jitter);
    Serial.print(" | Volts: ");
    
    //for (int i = 0; i < 5; i++) 
    {
      float displayVoltage = (receivedData[0] );
      Serial.print(displayVoltage, 3);
      Serial.print("V ");
    }
    
    Serial.print("| S: ");
    //for (int i = 0; i < 5; i++) 
    {
      Serial.print(thresholdStates[0]);
      Serial.print(" ");
    }
    Serial.println();
  }
}