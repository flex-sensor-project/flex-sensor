import asyncio

import datetime
from logging import log
import struct
import threading

import os

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

class Logger: 
    _instance = None
    _singleton_lock = threading.Lock()

    def __new__(cls):
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):    
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        self._write_lock = threading.Lock()
        now = datetime.datetime.now()
        date_hour_string = now.strftime("%Y-%m-%d_%H-%M")
        self.file_name =os.path.join(log_dir, date_hour_string + ".log")

        with open(self.file_name, 'a') as f:
            f.write(f"Log started at {now}\n")

    def log(self, msg):
        now = datetime.datetime.now()
        time_string = now.strftime("%H:%M:%S")
        log_entry = time_string + " - " + msg + "\n"

        with self._write_lock:
            with open(self.file_name, 'a') as f:
                f.write(log_entry)


class BleakDriver:

    logger = Logger()

    def __init__(self, parent):
        self.service_uuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b'   
        self.characteristic_uuid = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'
        
        
        self.packet_buffer = []

        self.parent = parent
        self.ble_unit_count = 0
        self.logger.log("BleakDriver initialized")
    
    def connect(self):
        ble_thread = threading.Thread(target=self._task_BLE, daemon=True)
        ble_thread.start()
        self.logger.log("Started BLE thread")

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
                    batch = self.packet_buffer.copy()
                    self.packet_buffer.clear()

                    self.parent.window.after(0, self.parent.update_raw, batch)

                #print("units per second: " + str(self.ble_unit_count))
                
                #self.parent.update_units(self.ble_unit_count)
               
               
                self.parent.window.after(0, self.parent.update_units, self.ble_unit_count)
                self.logger.log("Units per second: " + str(self.ble_unit_count))
                self.ble_unit_count = 0

                #self.parent.window.after(0, self.parent.update_raw, self.buffer)
        except asyncio.CancelledError:
            pass


    #  main_connect(ble_address) by protobioengineering - protobioengineering.github.io
    async def _main_connect(self, ble_address):
        try:
            #print(f'Looking for Bluetooth LE device at address `{ble_address}`...')
            self.logger.log("Looking for Bluetooth LE device with service UUID: " + str(ble_address))
            device = await BleakScanner.find_device_by_filter(
                lambda d, ad: self.service_uuid.lower() in [uuid.lower() for uuid in ad.service_uuids],
                timeout=20.0
            )    
        
            if device == None:
                #print(f'A Bluetooth LE device with the address `{ble_address}` was not found.')
                self.logger.log("No device found with service UUID: " + str(ble_address))
            else:
                
                #print(f'Client found at address: {ble_address}')
                #print(f'Connecting...')
                self.logger.log("Client found," + str(ble_address) + ", connecting")

                async with BleakClient(device) as client:
                    #print(f'Client connection = {client.is_connected}')
                    self.logger.log("Connected connection:" + str(client.is_connected))
                    await asyncio.sleep(2.0)
                    await client.start_notify(self.characteristic_uuid, self._notify_handler)
                    #print("characteristic found")
                    self.logger.log("Characteristic found")

                    units_task = asyncio.create_task(self._trigger_1s())


                    stop_event = asyncio.Event()
                    await stop_event.wait()
                
                    units_task.cancel()

                #print(f'Disconnected from `{ble_address}`')
                self.logger.log("Disconnected from:" + str(ble_address))
        except Exception as e:
            #print(f"Error connection lost or failed: {e}")
            self.logger.log("Error connection lost or failed: " +  str(e))
        
        finally:
           #self.parent.button_connect.config(state="normal")
           self.parent.window.after(0, self.parent.enable_button_connect)
           self.logger.log("BLE connection task ended, can connect again")