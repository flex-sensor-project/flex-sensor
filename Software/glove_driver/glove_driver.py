import sys
import time

import asyncio

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

import threading

import tkinter as tk

service_uuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b'
characteristic_uuid = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'
notify_buffer = ""


def notify_handler(sender, data):
    payload = data.decode('utf-8')
    
    global notify_buffer
    notify_buffer += payload

    if 'E' in notify_buffer :

        print("Received: " + notify_buffer)
        dyn_val_raw.set(notify_buffer)
        notify_buffer = ""
    


#  main_connect(ble_address) by protobioengineering - protobioengineering.github.io
async def main_connect(ble_address):
    print(f'Looking for Bluetooth LE device at address `{ble_address}`...')
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: service_uuid.lower() in [uuid.lower() for uuid in ad.service_uuids],
        timeout=20.0
    )    
    
    if(device == None):
        print(f'A Bluetooth LE device with the address `{ble_address}` was not found.')
        button_connect.config(state="normal")
    else:
        print(f'Client found at address: {ble_address}')
        print(f'Connecting...')

        # This `async` block starts and keeps the Bluetooth LE device connection.
        # Once the `async` block exits, BLE device automatically disconnects.
        try:
            async with BleakClient(device) as client:
                print(f'Client connection = {client.is_connected}')

                await asyncio.sleep(2.0)

                await client.start_notify(characteristic_uuid, notify_handler)
                print("characteristic found")

                #await asyncio.sleep(float('inf'))
                stop_event = asyncio.Event()
                await stop_event.wait()
        except Exception as e:
            print("Error connection lost: " + e)
        finally:
            button_connect.config(state="normal")

        print(f'Disconnected from `{ble_address}`')




def _task_BLE():
    # This runs the async loop in the background thread
    asyncio.run(main_connect(service_uuid))

def on_button_click_connect():

    #asyncio.run(main_connect(sys.argv[1] if len(sys.argv) == 2 else address))

    button_connect.config(state="disabled")

    ble_thread = threading.Thread(target=_task_BLE, daemon=True)
    ble_thread.start()

    dyn_val_A.set("1234")
    dyn_val_B.set("1234")
    dyn_val_C.set("1234")
    dyn_val_D.set("1234")
    dyn_val_E.set("1234")
    #dyn_val_raw.set("A0000B0000C0000D0000E0000")
    return



window = tk.Tk()
window.title("Glove driver")
window.geometry("350x250")
window.minsize(350, 250)

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