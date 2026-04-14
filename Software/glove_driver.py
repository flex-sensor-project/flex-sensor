import sys
import time
import bleak
import tkinter as tk

def on_button_click_connect():

    dyn_val_A.set("1234")
    dyn_val_B.set("1234")
    dyn_val_C.set("1234")
    dyn_val_D.set("1234")
    dyn_val_E.set("1234")
    dyn_val_raw.set("A0000B0000C0000D0000E0000")
    return



window = tk.Tk()

button_connect = tk.Button(window, text="connect", command=on_button_click_connect)

label_raw = tk.Label(window, text="Raw:")
label_A = tk.Label(window, text="Index A:")
label_B = tk.Label(window, text="Middle B:")
label_C = tk.Label(window, text="Ring C:")
label_D = tk.Label(window, text="Pinky D:")
label_E = tk.Label(window, text="Thumb E:")

dyn_val_raw = tk.StringVar()
dyn_val_A = tk.StringVar()
dyn_val_B = tk.StringVar()
dyn_val_C = tk.StringVar()
dyn_val_D = tk.StringVar()
dyn_val_E = tk.StringVar()

lbl_val_raw = tk.Label(window, textvariable=dyn_val_raw)
lbl_val_A = tk.Label(window, textvariable=dyn_val_A)
lbl_val_B = tk.Label(window, textvariable=dyn_val_B)
lbl_val_C = tk.Label(window, textvariable=dyn_val_C)
lbl_val_D = tk.Label(window, textvariable=dyn_val_D)
lbl_val_E = tk.Label(window, textvariable=dyn_val_E)



def define_view():
    
    label_raw.grid(row=0, column=2)
    lbl_val_raw.grid(row=0, column=4)
    label_A.grid(row=1,column=0)
    lbl_val_A.grid(row=1, column=1)
    label_B.grid(row=2,column=0)
    lbl_val_B.grid(row=2, column=1)
    label_C.grid(row=3,column=0)
    lbl_val_C.grid(row=3, column=1)
    label_D.grid(row=4,column=0)
    lbl_val_D.grid(row=4, column=1)
    label_E.grid(row=5,column=0)
    lbl_val_E.grid(row=5, column=1)

    button_connect.grid(row=6, column=2)

    return
    



def main():
    #print("test")
    
    define_view()

    window.mainloop()
    return


if __name__ == "__main__":
    main()