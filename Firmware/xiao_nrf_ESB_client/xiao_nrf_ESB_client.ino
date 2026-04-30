#include <nrf_to_nrf.h>

nrf_to_nrf radio;

const uint8_t address[5]   = {0x12, 0x34, 0x56, 0x78, 0x9A};
float         receivedData[5];

uint32_t packetCount  = 0;
uint32_t lastCalcTime = 0;
uint32_t maxJitter    = 0;
uint32_t lastPacketMs = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);


  uint32_t t = millis();
  while (!Serial && millis() - t < 3000);

  Serial.println("\n--- ESB Client (Receiver) ---");


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
  radio.openReadingPipe(1, address);
  radio.startListening();

  lastCalcTime = millis();
  Serial.println("Radio OK — listening.");
}

void loop() {
  if (radio.available()) {
    radio.read(&receivedData, sizeof(receivedData));

    uint32_t now      = millis();
    uint32_t interval = now - lastPacketMs;
    if (interval > maxJitter) maxJitter = interval;
    lastPacketMs = now;

    packetCount++;

  
    //digitalWrite(LED_BUILTIN, packetCount % 2 == 0 ? LOW : HIGH);
  }

  uint32_t now = millis();
  if (now - lastCalcTime >= 1000) {
    uint32_t pps    = packetCount;
    uint32_t jitter = maxJitter;
    packetCount     = 0;
    maxJitter       = 0;
    lastCalcTime    = now;

    Serial.print("PPS: ");
    Serial.print(pps);
    Serial.print(" | MaxJitter: ");
    Serial.print(jitter);
    Serial.print("ms | ");
    for (int i = 0; i < 5; i++) {
      Serial.print(receivedData[i], 3);
      Serial.print(i < 4 ? "V  " : "V\n");
    }
  }
}