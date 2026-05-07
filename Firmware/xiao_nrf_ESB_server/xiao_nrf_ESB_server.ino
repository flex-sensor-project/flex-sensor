#include <nrf_to_nrf.h>

nrf_to_nrf radio;

const uint8_t address[5] = {0x12, 0x34, 0x56, 0x78, 0x9A};
const int sensPins[] = {A0, A1, A2, A3, A4};
uint16_t rawAdc[5];
bool ackStates[5] = {false, false, false, false, false};

uint32_t lastPrintTime = 0;
uint32_t sentCount = 0;

void setup() {
  Serial.begin(115200);
  
  uint32_t t = millis();
  while (!Serial && millis() - t < 3000);

  Serial.println("\n--- ESB Server Transmitter ---");
  Serial.println("Initializing radio...");

  analogReadResolution(12);

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
  
  radio.openWritingPipe(address);
  radio.stopListening();

  Serial.println("Radio OK — transmitting.");
}

void loop() {
  for (int i = 0; i < 5; i++) {
    rawAdc[i] = analogRead(sensPins[i]);
  }

  bool tx_ok = radio.write(&rawAdc, sizeof(rawAdc));
  
  if (tx_ok) {
    sentCount++;
    if (radio.available()) {
      radio.read(&ackStates, sizeof(ackStates));
    }
  }
  
  delay(5);
  
  uint32_t now = millis();
  if (now - lastPrintTime >= 1000) {
    //Serial.print("TX PPS: ");
    Serial.print(sentCount);
    Serial.print(" | Raw ADC: ");
    
    //for (int i = 0; i < 5; i++) 
    {
      Serial.print(rawAdc[0]);
      Serial.print(" ");
    }
    
    Serial.print("| C: ");
    for (int i = 0; i < 5; i++) 
    {
      Serial.print(ackStates[i]);
      Serial.print(" ");
    }
    Serial.println();
    
    sentCount = 0;
    lastPrintTime = now;
  }
}