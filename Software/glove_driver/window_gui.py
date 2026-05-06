import tkinter as tk
from tkinter import ttk

from serial_driver import SerialDriver
from GloveDataProcessor import GloveDataProcessor

import time

import threading

from logger import Logger

class windowGui:
    
    logger = Logger()

    def __init__(self):
        self.window = tk.Tk()

        self.processor = GloveDataProcessor()
        self.latest_raw_data = None
        self.latest_processed_data = None

        self.textbox_raw = tk.Text(self.window, height=36, width=46)
       
        self.bd = SerialDriver(self)
        self.selected_index = None

        self.window.title("Glove driver")
        self.window.geometry("450x680")
        self.window.minsize(450, 680)

        self.combobox_devices = tk.ttk.Combobox(self.window, state="readonly")
        self.combobox_devices.bind("<<ComboboxSelected>>", self._on_combobox_select)

        self.button_scan = tk.Button(self.window, text="scan", command=self.bd.scan)
        self.button_connect = tk.Button(self.window, text="connect", command=self._on_button_click_connect)
        self.button_disconnect = tk.Button(self.window, text="disconnect", command=self._on_button_click_disconnect)
        self.button_calibrate = tk.Button(self.window, text="calibrate", command=self._on_button_click_calibrate, state="disabled")  

        self.label_units = tk.Label(self.window, text="Units:")
        self.label_combobox = tk.Label(self.window, text="Select device:")

        self.dyn_val_units = tk.StringVar()

        self.lbl_val_units = tk.Label(self.window, textvariable=self.dyn_val_units)

   
        self._define_view()

        self.button_disconnect.config(state="disabled")

    def run(self):
        self.window.mainloop()
        return

    @DeprecationWarning
    def update_raw_value(self, val):
        #self.dyn_val_raw.set(val)
        return

    def enable_button_connect(self):
        self.button_connect.config(state="normal")
        self.button_disconnect.config(state="disabled")

    def update_units(self, val):
        self.dyn_val_units.set(str(val))

    def update_combobox_devices(self, names):
        self.combobox_devices['values'] = names
        return

    def update_textbox(self, val):
        self.textbox_raw.config(state="normal")
        #self.textbox_raw.delete("1.0", tk.END)
        self.textbox_raw.insert(tk.END, f"{val}\n")
        self.textbox_raw.see(tk.END)
        self.textbox_raw.config(state="disabled")
        return

    def update_raw(self, data):
        
        if not data:
            return

        latest_packet = data[-1]
        
        raw_vals = latest_packet[0]
        proc_vals = latest_packet[1]

        raw_str = f"Live ADC:{raw_vals[0]},{raw_vals[1]},{raw_vals[2]},{raw_vals[3]},{raw_vals[4]}"
        proc_str = ""

        if proc_vals is not None:
            proc_str = f"Processed:{proc_vals[0]},{proc_vals[1]},{proc_vals[2]},{proc_vals[3]},{proc_vals[4]}"
        else:
            proc_str = "Processed: N/A"
        
        formatted_text = f"{raw_str}\n{proc_str}\n\n"
        
        self.textbox_raw.config(state="normal")
        self.textbox_raw.delete("1.0", tk.END)
        self.textbox_raw.insert(tk.END, formatted_text)
        self.textbox_raw.config(state="disabled")

        
        #fixed_units = []
        #for unit in data:
        #    temp = f"{unit[0]}, {unit[1]}, {unit[2]}, {unit[3]}, {unit[4]}"
        #    fixed_units.append(temp)
        #self.textbox_raw.config(state="normal")
        #self.textbox_raw.delete("1.0", tk.END)

        #formatted_units = "\n".join(fixed_units)

        #self.textbox_raw.insert(tk.END, formatted_units)
        #self.textbox_raw.config(state="disabled")

    def show_calibration_warning(self):
        self.textbox_raw.config(state="normal")
        self.textbox_raw.delete("1.0", tk.END)
        self.textbox_raw.insert(tk.END, "Please calibrate the glove to see processed data.\n")
        self.textbox_raw.config(state="disabled")


    def _on_combobox_select(self, event):
        self.selected_index = self.combobox_devices.current()
        selected_uuid = self.bd.device_uuids[self.selected_index]

        self.bd.selected_device = self.bd.devices[self.selected_index]

        if selected_uuid is not None:
            self.bd.service_uuid = selected_uuid
            self.update_textbox(f"Selected device: {self.bd.device_names[self.selected_index]} with UUID: {selected_uuid}")
        else:
            self.update_textbox("Warning: Selected device does not have a service UUID. Connection may fail.")
            self.bd.service_uuid = None
        return

    def _on_button_click_connect(self):

        if self.combobox_devices.get() == "":
            self.update_textbox("Please select a device before connecting.")
        elif self.bd.service_uuid is None:
            self.update_textbox("Warning: Selected device does not have a service UUID. Connection may fail.")  
        else:
            self.button_connect.config(state="disabled")
            self.button_disconnect.config(state="normal")
            self.button_calibrate.config(state="normal")

            self.bd.connect()

        return

    def _on_button_click_disconnect(self):
        self.bd.disconnect()
        self.button_connect.config(state="normal")
        self.button_disconnect.config(state="disabled")
        self.button_calibrate.config(state="disabled")
        return
    
    def _on_button_click_calibrate(self):
        self.button_calibrate.config(state="disabled")

        self.processor.calibrateAgain()

        self.bd.is_calibrated = False

        modal = tk.Toplevel(self.window)
        modal.title("Calibration")
        modal.geometry("300x200")
        modal.configure(bg="orange")

        modal.grab_set()

        instruction_label = tk.Label(modal, text="Ready to calibrate",font=("Arial", 14), bg="orange")
        
        instruction_label.pack(expand=True)

        
        cal_thread = threading.Thread(target=self._task_calibration, args=(modal, instruction_label))

        cal_thread.start()

    def _task_calibration(self, modal, instruction_label):
        poses = [0, 25, 50, 75, 100]
        
        self.logger.log("Starting calibration process")
        
        for pose in poses:
            self.window.after(0, lambda: modal.configure(bg="orange"))
            self.window.after(0, lambda: instruction_label.configure(bg="orange"))

            for i in range (5, 0, -1):
                text = f"Move Hand to {pose}%\nCapturing in {i}"
                self.window.after(0, lambda t=text: instruction_label.configure(text=t))
                time.sleep(1)
            
            self.latest_raw_data = None
            timeout = 2.5
            start_wait = time.time()
            
            self.logger.log(f"Waiting for data for pose {pose}%.")

            while self.latest_raw_data is None and (time.time() - start_wait) < timeout:
                time.sleep(0.001)

            if self.latest_raw_data is None:
                self.logger.log(f"Error: No data received for pose {pose}%. Calibration failed.")
                self.window.after(0, lambda: modal.configure(bg="red"))
                self.window.after(0, lambda: instruction_label.configure(text="Error: No data received or glove disconnected.", bg="red"))
                time.sleep(3)
                self.window.after(0, modal.destroy)
                self.window.after(0, lambda: self.button_calibrate.config(state="normal"))
                return
            
            self.logger.log(f"Data received for pose {pose}%: {self.latest_raw_data}")

            result = self.processor.addCalibrationPointAllFingers(self.latest_raw_data)

            self.logger.log(f"Calibration result for pose {pose}%: {result}")

            if result["status"] != 0:
                self.window.after(0, lambda: modal.configure(bg="red"))
                self.window.after(0, lambda msg=result['message']: instruction_label.configure(text=f"Error: {msg}", bg="red"))
                time.sleep(3)
                self.window.after(0, modal.destroy)
                self.window.after(0, lambda: self.button_calibrate.config(state="normal"))
                return

            self.window.after(0, lambda: modal.configure(bg="green"))
            self.window.after(0, lambda p=pose: instruction_label.configure(text=f"Successfully captured {p}%", bg="green"))
            time.sleep(2)

        self.logger.log("Calibration process completed successfully.")
        self.window.after(0, lambda: modal.configure(bg="green"))
        self.window.after(0, lambda: instruction_label.configure(text="Calibration completely finished!", bg="green"))
        
        self.bd.is_calibrated = True

        time.sleep(3)
        self.window.after(0, modal.destroy)
        self.window.after(0, lambda: self.button_calibrate.config(state="normal"))
        #self.window.after(0, modal.destroy)

        return
    

    def _define_view(self):
        self.dyn_val_units.set("0")

        self.label_combobox.grid(row=0, column=0)  

        self.label_units.grid(row=0, column=3)
        self.lbl_val_units.grid(row=0, column=4)

        self.combobox_devices.grid(row=1, column=0, columnspan=2, pady=10)

        self.button_scan.grid(row=1, column=2)
        self.button_connect.grid(row=1, column=3)
        self.button_disconnect.grid(row=1, column=4)
        self.button_calibrate.grid(row=1, column=5)

        self.textbox_raw.grid(row=2, column=0, columnspan=5, pady=10)

        return