#include <btstack.h>

const char* target_name = "XIAO";


const uint8_t target_service_uuid[] = {0x4f, 0xaf, 0xc2, 0x01, 0x1f, 0xb5, 0x45, 0x9e, 0x8f, 0xcc, 0xc5, 0xc9, 0xc3, 0x31, 0x91, 0x4b};
const uint8_t target_char_uuid[]    = {0xbe, 0xb5, 0x48, 0x3e, 0x36, 0xe1, 0x46, 0x88, 0xb7, 0xf5, 0xea, 0x07, 0x36, 0x1b, 0x26, 0xa8};


static btstack_packet_callback_registration_t hci_event_callback_registration;
static hci_con_handle_t connection_handle = HCI_CON_HANDLE_INVALID;
static gatt_client_notification_t notification_listener;
static gatt_client_service_t found_service;
static gatt_client_characteristic_t found_char;

static bool service_found = false;
static bool char_found = false;
static bool is_subscribed = false;

unsigned long lastTime = 0;
volatile int packetCount = 0;

static void packet_handler(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size);
static void gatt_event_handler(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size);
static void on_characteristics_discovered(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size);
static void on_services_discovered(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size);

bool match_uuid(const uint8_t* raw_le_data, const uint8_t* target_be_uuid) {
  for (int k = 0; k < 16; k++) {
    if (raw_le_data[k] != target_be_uuid[15 - k]) return false;
  }
  return true;
}


void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("Pico W BTstack FPS Counter Initializing");

  l2cap_init();
  gatt_client_init();
  sm_init();
  sm_set_io_capabilities(IO_CAPABILITY_NO_INPUT_NO_OUTPUT);

  hci_event_callback_registration.callback = &packet_handler;
  hci_add_event_handler(&hci_event_callback_registration);

  hci_power_control(HCI_POWER_ON);
}

void loop() {
  unsigned long currentTime = millis();
  
  if (is_subscribed && (currentTime - lastTime >= 1000)) {
    Serial.print("FPS: ");
    Serial.println(packetCount);
    packetCount = 0;
    lastTime = currentTime;
  }
}

static void gatt_event_handler(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size) {
  if (packet_type != HCI_EVENT_PACKET) return;
  if (hci_event_packet_get_type(packet) == GATT_EVENT_NOTIFICATION) {
    packetCount++;
  }
}

static void on_characteristics_discovered(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size) {
  if (packet_type != HCI_EVENT_PACKET) return;
  uint8_t event = hci_event_packet_get_type(packet);

  if (event == GATT_EVENT_CHARACTERISTIC_QUERY_RESULT) {
    gatt_client_characteristic_t temp_char;
    gatt_event_characteristic_query_result_get_characteristic(packet, &temp_char);
    

    if (memcmp(temp_char.uuid128, target_char_uuid, 16) == 0) {
      found_char = temp_char;
      char_found = true;
    }
  } 
  else if (event == GATT_EVENT_QUERY_COMPLETE) {
    if (char_found && !is_subscribed) {
      Serial.println("Characteristic found. Subscribing");
      uint16_t cccd_handle = found_char.value_handle + 1;
      uint8_t enable_data[] = {0x01, 0x00};
      
      gatt_client_write_characteristic_descriptor_using_descriptor_handle(
          packet_handler, 
          connection_handle, 
          cccd_handle, 
          2, 
          enable_data
      );
      
      is_subscribed = true;
      lastTime = millis();
      packetCount = 0;

      //max 34 fps speed
      //gap_update_connection_parameters(connection_handle, 6, 12, 0, 0x0048);
    }
  }
}

static void on_services_discovered(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size) {
  if (packet_type != HCI_EVENT_PACKET) return;
  uint8_t event = hci_event_packet_get_type(packet);

  if (event == GATT_EVENT_SERVICE_QUERY_RESULT) {
    gatt_client_service_t service;
    gatt_event_service_query_result_get_service(packet, &service);
    

    if (memcmp(service.uuid128, target_service_uuid, 16) == 0) {
      found_service = service;
      service_found = true;
    }
  } 
  else if (event == GATT_EVENT_QUERY_COMPLETE) {
    if (service_found) {
      Serial.println("Service found. Discovering characteristics");
      gatt_client_discover_characteristics_for_service(&on_characteristics_discovered, connection_handle, &found_service);
    }
  }
}

static void packet_handler(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size) {
  if (packet_type != HCI_EVENT_PACKET) return;
  uint8_t event = hci_event_packet_get_type(packet);

  switch (event) {
    case BTSTACK_EVENT_STATE:
      if (btstack_event_state_get_state(packet) == HCI_STATE_WORKING) {
        Serial.println("Scanning for XIAO");
        gap_set_scan_parameters(1, 0x0030, 0x0030);
        gap_start_scan();
      }
      break;

    case GAP_EVENT_ADVERTISING_REPORT: {
      uint8_t event_type = gap_event_advertising_report_get_advertising_event_type(packet);
      if (event_type == 0 || event_type == 1 || event_type == 4) { 
        bd_addr_t address;
        gap_event_advertising_report_get_address(packet, address);
        uint8_t length = gap_event_advertising_report_get_data_length(packet);
        const uint8_t *data = gap_event_advertising_report_get_data(packet);
        
        int i = 0;
        while (i < length) {
          uint8_t len = data[i];
          if (len == 0) break;
          uint8_t type = data[i+1];
          
          if (type == 0x06 || type == 0x07) { 
            for (int j = 0; j < len - 1; j += 16) {
              if (match_uuid(&data[i+2+j], target_service_uuid)) {
                Serial.println("Found matching Service UUID! Connecting");
                gap_stop_scan();

                //fast maybe?
                gap_set_connection_parameters(0x0030, 0x0030, 6, 12, 0, 0x0048, 0, 0);
                
                gap_connect(address, (bd_addr_type_t)gap_event_advertising_report_get_address_type(packet));
                return;
              }
            }
          }
          i += len + 1;
        }
      }
      break;
    }

    case HCI_EVENT_LE_META:
      if (hci_event_le_meta_get_subevent_code(packet) == HCI_SUBEVENT_LE_CONNECTION_COMPLETE) {
        if (hci_subevent_le_connection_complete_get_status(packet) == 0) {
          Serial.println("Connected. Discovering services");
          connection_handle = hci_subevent_le_connection_complete_get_connection_handle(packet);
          
          service_found = false;
          char_found = false;
          is_subscribed = false;
          
          gatt_client_discover_primary_services_by_uuid128(on_services_discovered, connection_handle, target_service_uuid);
          gatt_client_listen_for_characteristic_value_updates(&notification_listener, &gatt_event_handler, connection_handle, NULL);
        } else {
          Serial.println("Connection failed, restarting scan");
          gap_start_scan();
        }
      }
      break;

    case HCI_EVENT_DISCONNECTION_COMPLETE:
      Serial.println("Disconnected! Restarting scan");
      is_subscribed = false;
      gap_start_scan();
      break;
  }
}