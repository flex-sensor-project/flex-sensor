#include <bluefruit.h>

// Custom UUIDs for the Service and Characteristic
BLEUuid svc_uuid = BLEUuid("4fafc201-1fb5-459e-8fcc-c5c9c331914b");
BLEUuid chr_uuid = BLEUuid("beb5483e-36e1-4688-b7f5-ea07361b26a8");

BLEService gloveService(svc_uuid);
BLECharacteristic gloveCharacteristics(chr_uuid);

//BLEHidGamepad blehid;

char sendBuffer[64];


void setup() {
  Serial.begin(115200);

  Bluefruit.configPrphConn(64, BLE_GAP_EVENT_LENGTH_DEFAULT, BLE_GATTS_HVN_TX_QUEUE_SIZE_DEFAULT, BLE_GATTC_WRITE_CMD_TX_QUEUE_SIZE_DEFAULT);


  Bluefruit.begin();
  Bluefruit.setName("XIAO");

  Bluefruit.Periph.setConnInterval(6,12);
 // blehid.begin();

  gloveService.begin();

  gloveCharacteristics.setProperties(CHR_PROPS_READ | CHR_PROPS_NOTIFY);
  gloveCharacteristics.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  gloveCharacteristics.setMaxLen(10);
  gloveCharacteristics.begin();

  gloveCharacteristics.setUserDescriptor("glove data");





  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  
  
  Bluefruit.Advertising.addService(gloveService);
  Bluefruit.Advertising.addName();
  
  //Bluefruit.Advertising.addService(blehid);

  Bluefruit.Advertising.restartOnDisconnect(true);
  

  Bluefruit.Advertising.start(0);
  
  Serial.println("Waiting for a client connection to notify...");
}

void loop() {

  if (Bluefruit.connected()) {

    int16_t fingers[5];

    fingers[0] = random(1000, 5500);
    fingers[1] = random(1000, 5500);
    fingers[2] = random(1000, 5500);
    fingers[3] = random(1000, 5500);
    fingers[4] = random(1000, 5500);
    

    gloveCharacteristics.notify(fingers, sizeof(fingers));

    delay(8);
  
  }
}