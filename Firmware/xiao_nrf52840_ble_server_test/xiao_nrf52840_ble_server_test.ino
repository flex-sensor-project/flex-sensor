#include <bluefruit.h>

//#define PIN_VBAT A6
//#define PIN_VBAT_ENABLE 14



BLEUuid svc_uuid = BLEUuid("4fafc201-1fb5-459e-8fcc-c5c9c331914b");
BLEUuid chr_uuid = BLEUuid("beb5483e-36e1-4688-b7f5-ea07361b26a8");

BLEService gloveService(svc_uuid);
BLECharacteristic gloveCharacteristics(chr_uuid);

//BLEBas batteryService;

char sendBuffer[64];

//uint32_t timer_battery_update = 0;
//int debug_adc = 0;

void setup() {
  Serial.begin(115200);

  Bluefruit.begin();
  Bluefruit.setName("XIAO_Sensor");

  Bluefruit.Periph.setConnInterval(6,12);

  //batteryService.begin();
  //batteryService.write(100);

  pinMode(VBAT_ENABLE, OUTPUT);
  digitalWrite(VBAT_ENABLE, HIGH);

  Bluefruit.configPrphConn(64, BLE_GAP_EVENT_LENGTH_DEFAULT, BLE_GATTS_HVN_TX_QUEUE_SIZE_DEFAULT, BLE_GATTC_WRITE_CMD_TX_QUEUE_SIZE_DEFAULT);






  gloveService.begin();


  gloveCharacteristics.setProperties(CHR_PROPS_READ | CHR_PROPS_NOTIFY);
  gloveCharacteristics.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  gloveCharacteristics.setMaxLen(10);
  gloveCharacteristics.begin();

  gloveCharacteristics.setUserDescriptor("glove data");


 // gloveCharacteristics.write("A100B100C100D100E100");


  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();

  Bluefruit.Advertising.addService(gloveService);
  //Bluefruit.Advertising.addService(batteryService);

  Bluefruit.Advertising.addName();
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
    
   
    

    //uint16_t raw_val = debug_adc;
    gloveCharacteristics.notify(fingers, sizeof(fingers));

    //timer_battery_update += 1;
    delay(10);
  }
}