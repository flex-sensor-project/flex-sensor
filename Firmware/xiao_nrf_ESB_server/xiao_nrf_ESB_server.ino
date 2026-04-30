#include <nrf_to_nrf.h>

nrf_to_nrf radio;

const uint8_t address[5] = {0x12, 0x34, 0x56, 0x78, 0x9A};
const int     sensPins[] = {A0, A1, A2, A3, A4};
float         voltages[5];

uint32_t lastPrintTime = 0;
uint32_t sentCount     = 0;

void setup() {
  Serial.begin(115200);

  
  uint32_t t = millis();
  while (!Serial && millis() - t < 3000);

  Serial.println("\n--- ESB Server (Transmitter) ---");
  Serial.println("Initializing radio...");

  analogReadResolution(12);


  sd_softdevice_disable();
  delay(100);

  if (!radio.begin()) {
    Serial.println("FATAL: radio.begin() failed — check SoftDevice conflict");
    while (1) {
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
      delay(100);
    }
  }

  radio.setChannel(100);           
  radio.setDataRate(NRF_1MBPS);   //  NRF_2MBPS
  radio.setPayloadSize(20);        
  radio.setAutoAck(false);         
  radio.openWritingPipe(address);
  radio.stopListening();

  Serial.println("Radio OK — transmitting.");
}

void loop() {
  for (int i = 0; i < 5; i++) {
    voltages[i] = (analogRead(sensPins[i]) / 4095.0f) * 3.3f;
  }

  radio.write(&voltages, sizeof(voltages));
  sentCount++;
  delay(5);                        

  // Print TX rate to serial every second
  uint32_t now = millis();
  if (now - lastPrintTime >= 1000) {
    Serial.print("TX PPS: ");
    Serial.print(sentCount);
    Serial.print(" | ");
    for (int i = 0; i < 5; i++) {
      Serial.print(voltages[i], 3);
      Serial.print(i < 4 ? "V  " : "V\n");
    }
    sentCount     = 0;
    lastPrintTime = now;
  }
}