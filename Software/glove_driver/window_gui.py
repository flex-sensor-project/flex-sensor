import tkinter as tk
from tkinter import ttk

from bleak_driver import BleakDriver

class windowGui:
    

    def __init__(self):
        self.window = tk.Tk()


        self.textbox_raw = tk.Text(self.window, height=32, width=40)
       
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
       
        #self.label_raw = tk.Label(self.window, text="Raw:")
        self.label_A = tk.Label(self.window, text="Index A:")
        self.label_B = tk.Label(self.window, text="Middle B:")
        self.label_C = tk.Label(self.window, text="Ring C:")
        self.label_D = tk.Label(self.window, text="Pinky D:")
        self.label_E = tk.Label(self.window, text="Thumb E:")

        self.dyn_val_units = tk.StringVar()

        #self.dyn_val_raw = tk.StringVar()
        self.dyn_val_A  = tk.StringVar()
        self.dyn_val_B = tk.StringVar()
        self.dyn_val_C = tk.StringVar()
        self.dyn_val_D = tk.StringVar()
        self.dyn_val_E = tk.StringVar()

        self.lbl_val_units = tk.Label(self.window, textvariable=self.dyn_val_units)

        #self.lbl_val_raw = tk.Label(self.window, textvariable=self.dyn_val_raw)
        self.lbl_val_A = tk.Label(self.window, textvariable=self.dyn_val_A)
        self.lbl_val_B = tk.Label(self.window, textvariable=self.dyn_val_B)
        self.lbl_val_C = tk.Label(self.window, textvariable=self.dyn_val_C)
        self.lbl_val_D = tk.Label(self.window, textvariable=self.dyn_val_D)
        self.lbl_val_E = tk.Label(self.window, textvariable=self.dyn_val_E)

        

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

    def update_units(self, val):
        self.dyn_val_units.set(str(val))

    def update_combobox_devices(self, names):
        self.combobox_devices['values'] = names
        return

    def update_textbox(self, val):
        self.textbox_raw.config(state="normal")
        self.textbox_raw.delete("1.0", tk.END)
        self.textbox_raw.insert(tk.END, val)
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

        if len(data) > 0:
            first_packet = data[0]
            self.dyn_val_A.set(str(first_packet[0]))
            self.dyn_val_B.set(str(first_packet[1]))
            self.dyn_val_C.set(str(first_packet[2]))
            self.dyn_val_D.set(str(first_packet[3]))
            self.dyn_val_E.set(str(first_packet[4]))


    def _on_combobox_select(self, event):
        self.selected_index = self.combobox_devices.current()
        selected_uuid = self.bd.device_uuids[self.selected_index]

        if selected_uuid is not None:
            self.bd.service_uuid = selected_uuid
            self.update_textbox(f"Selected device: {self.bd.device_names[self.selected_index]} with UUID: {selected_uuid}")
        else:
            self.update_textbox("Warning: Selected device does not have a service UUID. Connection may fail.")
            self.bd.service_uuid = None
        return

    def _on_button_click_connect(self):

        #asyncio.run(main_connect(sys.argv[1] if len(sys.argv) == 2 else address))

        if self.combobox_devices.get() == "":
            self.update_textbox("Please select a device before connecting.")
        elif self.bd.service_uuid is None:
            self.update_textbox("Warning: Selected device does not have a service UUID. Connection may fail.")  
        else:
            self.button_connect.config(state="disabled")
        
            self.bd.connect()

        #self.dyn_val_A.set("1234")
        #self.dyn_val_B.set("1234")
        #self.dyn_val_C.set("1234")
        #self.dyn_val_D.set("1234")
        #self.dyn_val_E.set("1234")
        #self.dyn_val_raw.set("A0000B0000C0000D0000E0000")
        return

    def _on_button_click_disconnect(self):
        self.bd.disconnect()
        self.button_connect.config(state="normal")
        self.button_disconnect.config(state="disabled")
        return
    
    def _define_view(self):
        self.dyn_val_units.set("0")

        
        #self.label_raw.grid(row=0, column=2)
        #self.lbl_val_raw.grid(row=0, column=4)
        self.label_A.grid(row=0, column=0)
        self.lbl_val_A.grid(row=0, column=1)
        self.label_B.grid(row=1, column=0)
        self.lbl_val_B.grid(row=1, column=1)
        self.label_C.grid(row=2, column=0)
        self.lbl_val_C.grid(row=2, column=1)
        self.label_D.grid(row=3, column=0)
        self.lbl_val_D.grid(row=3, column=1)
        self.label_E.grid(row=4, column=0)
        self.lbl_val_E.grid(row=4, column=1)

        self.lbl_val_units.grid(row=5, column=2)

        self.combobox_devices.grid(row=6, column=0, columnspan=2, pady=10)

        self.button_scan.grid(row=6, column=2)
        self.button_connect.grid(row=6, column=3)
        self.button_disconnect.grid(row=6, column=4)

        self.textbox_raw.grid(row=7, column=0, columnspan=5, pady=10)

        return