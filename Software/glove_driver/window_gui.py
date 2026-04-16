import tkinter as tk

from bleak_driver import BleakDriver

class windowGui:
    

   

    def __init__(self):
        self.window = tk.Tk()

        self.bd = BleakDriver(self)

        self.window.title("Glove driver")
        self.window.geometry("350x250")
        self.window.minsize(350, 250)

        self.button_connect = tk.Button(self.window, text="connect", command=self._on_button_click_connect)

        self.label_raw = tk.Label(self.window, text="Raw:")
        self.label_A = tk.Label(self.window, text="Index A:")
        self.label_B = tk.Label(self.window, text="Middle B:")
        self.label_C = tk.Label(self.window, text="Ring C:")
        self.label_D = tk.Label(self.window, text="Pinky D:")
        self.label_E = tk.Label(self.window, text="Thumb E:")

        self.dyn_val_raw = tk.StringVar()
        self.dyn_val_A  = tk.StringVar()
        self.dyn_val_B = tk.StringVar()
        self.dyn_val_C = tk.StringVar()
        self.dyn_val_D = tk.StringVar()
        self.dyn_val_E = tk.StringVar()

        self.lbl_val_raw = tk.Label(self.window, textvariable=self.dyn_val_raw)
        self.lbl_val_A = tk.Label(self.window, textvariable=self.dyn_val_A)
        self.lbl_val_B = tk.Label(self.window, textvariable=self.dyn_val_B)
        self.lbl_val_C = tk.Label(self.window, textvariable=self.dyn_val_C)
        self.lbl_val_D = tk.Label(self.window, textvariable=self.dyn_val_D)
        self.lbl_val_E = tk.Label(self.window, textvariable=self.dyn_val_E)

        self._define_view()

    def run(self):
        self.window.mainloop()
        return

    def update_raw_value(self, val):
        self.dyn_val_raw.set(val)

    def enable_button_connect(self):
        self.button_connect.config(state="normal")

    def _on_button_click_connect(self):

        #asyncio.run(main_connect(sys.argv[1] if len(sys.argv) == 2 else address))

        self.button_connect.config(state="disabled")

        self.bd.connect()

        self.dyn_val_A.set("1234")
        self.dyn_val_B.set("1234")
        self.dyn_val_C.set("1234")
        self.dyn_val_D.set("1234")
        self.dyn_val_E.set("1234")
        #self.dyn_val_raw.set("A0000B0000C0000D0000E0000")
        return


    def _define_view(self):
        self.label_raw.grid(row=0, column=2)
        self.lbl_val_raw.grid(row=0, column=4)
        self.label_A.grid(row=1,column=0)
        self.lbl_val_A.grid(row=1, column=1)
        self.label_B.grid(row=2,column=0)
        self.lbl_val_B.grid(row=2, column=1)
        self.label_C.grid(row=3,column=0)
        self.lbl_val_C.grid(row=3, column=1)
        self.label_D.grid(row=4,column=0)
        self.lbl_val_D.grid(row=4, column=1)
        self.label_E.grid(row=5,column=0)
        self.lbl_val_E.grid(row=5, column=1)

        self.button_connect.grid(row=6, column=2)

        return