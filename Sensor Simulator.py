import serial
import time
from datetime import datetime
import json
import tkinter as tk
from tkinter import ttk

current_time=datetime.now()

class Sensor:
    # Constructor method to initialize new objects
    def __init__(self, name, value,Timestamp,Status):
        self.name = name                # Instance attribute
        self.value = value              # Instance attribute
        self.Timestamp = Timestamp      # Instance attribute
        self.Status = Status            # Instance attribute

    
    def send_sensor_data(self):

        # 1. Prepare data dictionary
        data = {
            "name": self.name,
            "value": self.value,
            "timestamp": int(time.time()),
            "status": self.Status
        }
        
        # 2. Serialize to a JSON string and add newline
        # Using json.dumps ensures proper formatting
        json_payload = json.dumps(data) + "\n"
        
        # 3. Encode and send
        ser.write(json_payload.encode('utf-8'))
        print(f"Sent JSON: {json_payload.strip()}")



# 1. Open serial port (UART init)
ser = serial.Serial(
    port='COM1',        # change this to your COM port
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1           # seconds
)

# Give the port time to initialize
time.sleep(1)

# Create an instance (object)
temp_sensor = Sensor("Temp",25,current_time,"OK")

# --- GUI Functions ---
def handle_send():
    # 1. Update the object with current GUI values
    temp_sensor.value = round(slider.get(), 2)
    temp_sensor.Status = status_var.get()
    
    # 2. Trigger the class method
    if ser:
        temp_sensor.send_sensor_data()
        log.insert(tk.END, f"Sent: {temp_sensor.value}, {temp_sensor.Status}\n")
    else:
        log.insert(tk.END, "Error: Serial Port Not Found\n")
    log.see(tk.END)

# --- UI Layout ---
root = tk.Tk()
root.title("Sensor Controller")
root.geometry("350x450")

# Value Control
tk.Label(root, text=f"Sensor Name: {temp_sensor.name}", font=('Arial', 12, 'bold')).pack(pady=10)
tk.Label(root, text="Adjust Value:").pack()
slider = tk.Scale(root, from_=0, to=100, orient='horizontal', length=250, resolution=0.1)
slider.set(temp_sensor.value)
slider.pack(pady=5)

# Status Control
tk.Label(root, text="Select Status:").pack(pady=(10, 0))
status_var = tk.StringVar(value=temp_sensor.Status)
status_menu = ttk.Combobox(root, textvariable=status_var, values=("OK", "WARNING", "ERROR"), state="readonly")
status_menu.pack(pady=5)

# Action Button
send_btn = tk.Button(root, text="SEND DATA", command=handle_send, bg="#2196F3", fg="white", width=20)
send_btn.pack(pady=20)

# Monitoring Log
log = tk.Text(root, height=10, width=40, font=('Consolas', 9))
log.pack(padx=10, pady=10)

root.mainloop()

# Clean up
if ser:
    ser.close()
