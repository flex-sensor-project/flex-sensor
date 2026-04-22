import tkinter as tk
from tkinter import ttk

from bleak_driver import BleakDriver
from GloveDataProcessor import GloveDataProcessor

import time

class windowGui:
    

    def __init__(self):
        self.window = tk.Tk()

        self.processor = GloveDataProcessor()
        self.latest_raw_data = None

        self.textbox_raw = tk.Text(self.window, height=36, width=40)
       
        self.bd = BleakDriver(self)
        self.selected_index = None

        self.window.title("Glove driver")
        self.window.geometry("350x680")
        self.window.minsize(350, 680)

        self.combobox_devices = tk.ttk.Combobox(self.window, state="readonly")
        self.combobox_devices.bind("<<ComboboxSelected>>", self._on_combobox_select)

        self.button_scan = tk.Button(self.window, text="scan", command=self.bd.scan)
        self.button_connect = tk.Button(self.window, text="connect", command=self._on_button_click_connect)
        self.button_disconnect = tk.Button(self.window, text="disconnect", command=self._on_button_click_disconnect)
        self.button_calibrate = tk.Button(self.window, text="calibrate", command=self._on_button_click_calibrate)  

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
        
    
        fixed_units = []
        for unit in data:
            temp = f"{unit[0]}, {unit[1]}, {unit[2]}, {unit[3]}, {unit[4]}"
            fixed_units.append(temp)
        self.textbox_raw.config(state="normal")
        self.textbox_raw.delete("1.0", tk.END)

        formatted_units = "\n".join(fixed_units)

        self.textbox_raw.insert(tk.END, formatted_units)
        self.textbox_raw.config(state="disabled")

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
        self.processor.calibrateAgain()

        self.bd.is_calibrated = False

        modal = tk.Toplevel(self.window)
        modal.title("Calibration")
        modal.geometry("300x200")
        modal.configure(bg="orange")

        modal.grab_set()

        instruction_label = tk.Label(modal, text="Ready to calibrate",font=("Arial", 14), bg="orange")
        
        instruction_label.pack(expand=True)

        poses = [0, 25, 50, 75, 100]
        
        for pose in poses:
            instruction_label.configure(text=f"Hold your hand at {pose}%")
            modal.update()
            time.sleep(1)

            if self.latest_raw_data is None:
                modal.configure(bg="red")
                instruction_label.configure(text="Error: No data received.", bg="red")
                time.sleep(1)
                return
            result = self.processor.addCalibrationPointAllFingers(self.latest_raw_data)

            if result["status"] != 0:
                modal.configure(bg="red")
                instruction_label.configure(text=f"Error: {result['message']}", bg="red")
                time.sleep(1)
                return
        
        modal.configure(bg="green")
        instruction_label.configure(text="Calibration complete!", bg="green")
        
        self.bd.is_calibrated = True

        time.sleep(2)
        self.window.after(0, modal.destroy)

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