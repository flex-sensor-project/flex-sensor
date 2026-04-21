import asyncio

import datetime
from logging import log
import struct
import threading

import os

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

from logger import Logger


class BleakDriver:

    logger = Logger()

    def __init__(self, parent):
        #self.service_uuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b'   
        #self.characteristic_uuid = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'
        
        self.service_uuid = None
        self.characteristic_uuid = None

        self.selected_device = None

        self.devices = []
        self.device_names = []
        self.device_uuids = []

        self.packet_buffer = []


        self.parent = parent
        self.ble_unit_count = 0
        
        self.connected = False

        self.logger.log("BleakDriver initialized")
        self.parent.update_textbox("BleakDriver initialized.")
    
    def scan(self):
        #self.devices = ["1", "2", "3"]
        scan_thread = threading.Thread(target=self._task_scan, daemon=True)
        scan_thread.start()
        self.logger.log("Started BLE scan thread")
        self.parent.update_textbox("Started BLE scan thread.")

        return

    def connect(self):
        ble_thread = threading.Thread(target=self._task_BLE, daemon=True)
        ble_thread.start()
        self.logger.log("Started BLE thread")
        #self.parent.update_textbox("Started BLE thread.")

    def disconnect(self):
        self.connected = False
        self.logger.log("BLE disconnect requested")
        #self.parent.update_textbox("BLE disconnect requested.")


    def _task_scan(self):
        asyncio.run(self._async_scan())

    async def _async_scan(self):
        discovered = await BleakScanner.discover(return_adv=True, timeout=5.0)

        self.devices = []
        self.device_names = []
        self.device_uuids = []

        for address, (device, adv_data) in discovered.items():
            name = device.name if device.name else "Unknown"
            self.devices.append(device)
            self.device_names.append(name)

            if adv_data.service_uuids:
                self.device_uuids.append(adv_data.service_uuids[0])
            else:
                self.device_uuids.append(None)
        
        self.parent.window.after(0, self.parent.update_combobox_devices, self.device_names)
        
        return

    def _task_BLE(self):
        # This runs the async loop in the background thread
        asyncio.run(self._main_connect(self.service_uuid))

    
    def _notify_handler(self, sender, data):
    
        if len(data) == 10:
            values = struct.unpack('<5H', data)
        
            self.packet_buffer.append(values)
            self.ble_unit_count += 1
        #TODO implement validating received payload
        #if 'E' in self.notify_buffer :
            #if len(self.notify_buffer) < 25:
                #print("Received an invalid: " + self.notify_buffer)
            #else:
                #print("Received: " + self.notify_buffer)
            #self.parent.dyn_val_raw.set(self.notify_buffer)
           
            #self.parent.window.after(0, self.parent.update_raw_value, self.notify_buffer)
            #self.notify_buffer = ""
            

    async def _trigger_1s(self):
        try:
            while True:
                await asyncio.sleep(1.0)

                if len(self.packet_buffer) > 0:
                    batch = self.packet_buffer
                    self.packet_buffer = []

                    self.parent.window.after(0, self.parent.update_raw, batch)

               
                self.parent.window.after(0, self.parent.update_units, self.ble_unit_count)
                self.logger.log(f"Units per second: {self.ble_unit_count}.")
                self.ble_unit_count = 0

        except asyncio.CancelledError:
            pass


    def _dynamic_char_search(self, client):
        target_service = client.services.get_service(self.service_uuid)

        if target_service:
            for char in target_service.characteristics:
                if "notify" in char.properties:
                    return char.uuid
        return None


    #  main_connect(ble_address) by protobioengineering - protobioengineering.github.io
    async def _main_connect(self, ble_uuid):
        try:
            if self.selected_device is None:
                    self.logger.log("Connection aborted: No device selected.")
                    self.parent.window.after(0, self.parent.update_textbox, "Connection aborted: No device selected.")  
                    return

            #if ble_uuid is None:
            #   self.logger.log("Connection aborted: No service UUID specified.")
            #    self.parent.window.after(0, self.parent.update_textbox, "Connection aborted: No service UUID specified.")  
            #    return
            
            
            #elf.logger.log(f"Looking for Bluetooth LE device with service UUID: {ble_uuid}.")
            #self.parent.window.after(0, self.parent.update_textbox, f"Looking for Bluetooth LE device with service UUID: {ble_uuid}.")
            #device = await BleakScanner.find_device_by_filter(
            #    lambda d, ad: self.service_uuid.lower() in [uuid.lower() for uuid in ad.service_uuids],
            #    timeout=20.0
            #)    
        
            #if device == None:
            #    self.logger.log("No device found with service UUID: " + str(ble_uuid))
            #    self.parent.window.after(0, self.parent.update_textbox, f"No device found with service UUID: {ble_uuid}.")
            #else:
                
            
                #self.logger.log("Client found, " + str(ble_uuid) + ", connecting")
                #self.parent.window.after(0, self.parent.update_textbox, "Client found," + str(ble_uuid) + ", connecting")

            self.logger.log(f"Attempting to connect to device: {self.selected_device.name} with address: {self.selected_device.address}.")
            self.parent.window.after(0, self.parent.update_textbox, f"Attempting to connect to device: {self.selected_device.name} with address: {self.selected_device.address}.")

            async with BleakClient(self.selected_device) as client:
                
                self.logger.log("Connected, now pairing...")
                self.parent.window.after(0, self.parent.update_textbox, "Connected, now pairing")
                await client.pair()
                
                self.characteristic_uuid = self._dynamic_char_search(client)



                if self.characteristic_uuid is None:
                    self.logger.log("COnnection failed: No characteristic with notify found.")
                    self.parent.window.after(0, self.parent.update_textbox, "Connection failed: No characteristic with notify found.")
                    return 

                self.logger.log(f"Connected to device, found notify characteristic: {self.characteristic_uuid}.") 
                self.parent.window.after(0, self.parent.update_textbox, f"Connected to device, found notify characteristic: {self.characteristic_uuid}.")    

                    
                self.logger.log("Connected connection status: " + str(client.is_connected))
                self.parent.window.after(0, self.parent.update_textbox, f"Connected, connection status: {client.is_connected}.")
                    
                await asyncio.sleep(2.0)
                await client.start_notify(self.characteristic_uuid, self._notify_handler)
                    
                self.logger.log("Characteristic found")
                self.parent.window.after(0, self.parent.update_textbox, "Characteristic found.")
                    
                units_task = asyncio.create_task(self._trigger_1s())

                self.connected = True
                while self.connected:
                    await asyncio.sleep(0.5)

                units_task.cancel()

                
            self.logger.log("Disconnected from: " + str(ble_uuid))
            self.parent.window.after(0, self.parent.update_textbox, f"Disconnected from: {ble_uuid}.") 
        
        except Exception as e:
            self.logger.log("Error connection lost or failed: " +  str(e))
            self.parent.window.after(0, self.parent.update_textbox, f"Error connection lost or failed: {e}.")
        
        finally:
            self.parent.window.after(0, self.parent.enable_button_connect)
            self.logger.log("BLE connection task ended, can connect again.")
            self.parent.window.after(0, self.parent.update_textbox, "BLE connection task ended, can connect again.")