import asyncio

import threading


from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError


class BleakDriver:

    
    
    def __init__(self, parent):
        self.service_uuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b'   
        self.characteristic_uuid = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'
        self.notify_buffer = ""

        self.parent = parent
    
    def connect(self):
        ble_thread = threading.Thread(target=self._task_BLE, daemon=True)
        ble_thread.start()

    def _task_BLE(self):
        # This runs the async loop in the background thread
        asyncio.run(self._main_connect(self.service_uuid))

    
    def _notify_handler(self, sender, data):
        payload = data.decode('utf-8')
    
        
        self.notify_buffer += payload

        if 'E' in self.notify_buffer :

            if len(self.notify_buffer) != 25:
                print("Received an invalid: " + self.notify_buffer)
            #else:
                #print("Received: " + self.notify_buffer)
            self.parent.dyn_val_raw.set(self.notify_buffer)
            self.notify_buffer = ""

    #  main_connect(ble_address) by protobioengineering - protobioengineering.github.io
    async def _main_connect(self, ble_address):
        try:
            print(f'Looking for Bluetooth LE device at address `{ble_address}`...')
            device = await BleakScanner.find_device_by_filter(
                lambda d, ad: self.service_uuid.lower() in [uuid.lower() for uuid in ad.service_uuids],
                timeout=20.0
            )    
        
            if device == None:
                print(f'A Bluetooth LE device with the address `{ble_address}` was not found.')
            else:
                print(f'Client found at address: {ble_address}')
                print(f'Connecting...')

                async with BleakClient(device) as client:
                    print(f'Client connection = {client.is_connected}')
                    await asyncio.sleep(2.0)
                    await client.start_notify(self.characteristic_uuid, self._notify_handler)
                    print("characteristic found")

                    stop_event = asyncio.Event()
                    await stop_event.wait()
                
                print(f'Disconnected from `{ble_address}`')

        except Exception as e:
            print(f"Error connection lost or failed: {e}")
        
        finally:
           self.parent.button_connect.config(state="normal")