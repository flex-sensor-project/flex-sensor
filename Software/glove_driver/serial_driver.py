import serial
import serial.tools.list_ports
import struct
import threading
import time

from logger import Logger


class SerialDriver:
    
    logger = Logger()

    def __init__(self, parent):
        self.parent = parent

       

        self.selected_device = None
        self.devices = []
        self.device_names = []

        self.packet_buffer = []
        self.ble_unit_count = 0
        self.connected = False
        self.serial_port = None

        self.logger.log("SerialDriver initialized")
        
        self.parent.window.after(0, self.parent.update_combobox_devices, self.device_names)
    
    def scan(self):
        ports = serial.tools.list_ports.comports()

        self.devices = [port.device for port in ports]
        self.device_names = [f"{port.device} - {port.description}" for port in ports]   
        
        self.parent.window.after(0, self.parent.update_combobox_devices, self.device_names)

        self.logger.log(f"Started serial scan")
        
        self.parent.window.after(0, self.parent.update_textbox, "Started serial scan")

    def connect(self, device_index):
        if self.parent.selected_index is None:
            self.logger.log("Connection stopped: No Com port selected")
            #TODO refactor to async gui update
            self.parent.update_textbox("Connection stopped: No Com port selected")
            return
        
        self.selected_device = self.devices[self.parent.selected_index]
        self.connected = True

        serial_thread = threading.Thread(target=self._task_serial, daemon=True)
        serial_thread.start()
        self.logger.log(f"Started serial thread")

    def disconnect(self):
        self.connected = False
        self.logger.log(f"Disconnected from serial port")
    
    def _task_serial(self):
        try:
            self.serial_port = serial.Serial(self.selected_device, baudrate=115200, timeout=1)

            self.logger.log(f"Connected to {self.selected_device}")
            #TODO refactor to async gui update
            self.parent.update_textbox(f"Connected to {self.selected_device}")

            timer_thread = threading.Thread(target=self._trigger_1s, daemon=True)
            timer_thread.start()

            while self.connected:
                if self.serial_port.in_waiting >= 10:
                    data = self.serial_port.read(10)

                    if len(data) == 10:
                        values = struct.unpack('<5H', data)

                        self.parent.latest_raw_data = values
                        self.packet_buffer.append((values, None))
                        self.ble_unit_count += 1
                    
                else:
                    time.sleep(0.001)
        
        except Exception as e:
            self.logger.log("Error connection lost or failed")
            self.parent.window.after(0, self.parent.update_textbox, "Error connection lost or failed")
        
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.connected = False
            self.parent.window.after(0, self.parent.enable_button_connect)
            self.logger.log("Serial connection task ended, can connect again")
            self.parent.window.after(0, self.parent.update_textbox, "Serial connection task ended, can connect again")

    
    def _trigger_1s(self):
        while self.connected:
            time.sleep(1.0)
            
            if len(self.packet_buffer) > 0:
                batch, self.packet_buffer = self.packet_buffer, []
                self.parent.window.after(0, self.parent.update_raw, batch)
            
            self.parent.window.after(0, self.parent.update_units, self.ble_unit_count)
            self.logger.log(f"Units per second: {self.ble_unit_count}")
            self.ble_unit_count = 0