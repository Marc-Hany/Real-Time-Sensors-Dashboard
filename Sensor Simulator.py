import serial
import time
import json
import tkinter as tk
from tkinter import ttk

class Sensor:
    def __init__(self, name, value, status,Low,High):
        self.name = name
        self.value = value
        self.status = status
        self.Low=Low    #Minimum bound
        self.High=High  #Maximum bound

    def send_sensor_data(self):
        data = {
            "name": self.name,
            "value": self.value,
            "timestamp": int(time.time()), # Generates fresh timestamp on send
            "status": self.status
        }
        json_payload = json.dumps(data) + "\n"
        ser.write(json_payload.encode('utf-8'))
        # print(f"Sent JSON: {json_payload.strip()}")

    def update_value(self,val):
         # If original value was int, store as int; otherwise float
        if isinstance(self.value, int):
            self.value = int(float(val))
        else:
            self.value = float(val)
        # print(self.value)

    def update_status(self,event):
        self.status = event.widget.get()
        # print(self.status)   


# --- Serial Setup ---
try:
    # Open serial port (UART init)
    ser = serial.Serial(
        port='COM1',        # change this to your COM port
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1           # seconds
    )
    time.sleep(1)
except Exception as e:
    print(f"Serial Error: {e}. Running in simulation mode (no hardware).")
    ser = None


# --- 1. Define your Sensors ---
my_sensors = [
    Sensor("Temperature", 25.0, "OK",-100,100),
    Sensor("Humidity", 50.0, "OK",0,100),
    Sensor("Pressure", 52.2, "OK",0,1000),
    Sensor("Speed", 100.0, "OK",0,255),
    Sensor("Counter", 0, "OK",0,500)
]

# --- 2. Generic GUI Handler ---
def handle_send():
        # # Update the specific sensor object with values from its specific UI widgets
        # sensor.value = round(slider.get(), 2)
        # sensor.status = status_var.get()
        for sensor in my_sensors:
            # Send the data
            sensor.send_sensor_data()
            
            # Log to screen
            log.insert(tk.END, f"[{sensor.name}] Value: {sensor.value}, Status: {sensor.status}\n")
            log.see(tk.END)
        root.after(500,handle_send)
# --- 3. Building the UI ---
root = tk.Tk()
root.title("Sensors Dashboard")

# Container for all sensors
main_frame = tk.Frame(root)
main_frame.pack(padx=20, pady=20)

for s in my_sensors:
    # Create a visual "Card" for each sensor
    frame = tk.LabelFrame(main_frame, text=f" {s.name} ", padx=10, pady=10)
    frame.pack(fill="x", pady=5)

    # 2. Container for the slider and its min/max labels
    slider_container = tk.Frame(frame)
    slider_container.pack(side="left")

    # Low Bound Label
    tk.Label(slider_container, text=str(s.Low)).pack(side="left")

    # The Slider
    res = 0.1 if isinstance(s.value, float) else 1
    val_slider = tk.Scale(
        slider_container, 
        from_=s.Low, to=s.High, 
        orient='horizontal', 
        resolution=res,
        length=500, # Increased length for better visibility
        showvalue=True, # Keeps the current value floating above the handle
        command=lambda v, s=s: s.update_value(v),
        label='Value'
    )
    val_slider.set(s.value)
    val_slider.pack(side="left", padx=5)

    # High Bound Label
    tk.Label(slider_container, text=str(s.High)).pack(side="left")
    
    # Dropdown for this sensor
    stat_var = tk.StringVar(value=s.status)
    stat_menu = ttk.Combobox(frame, textvariable=stat_var, values=("OK", "FAULTY"), width=7)
    # BIND the selection event to your update function
    stat_menu.bind("<<ComboboxSelected>>", lambda e, s=s: s.update_status(e))
    stat_menu.pack(side="left", padx=10)

    # Button linked to THIS sensor instance
    # We use 'lambda' to "freeze" the current sensor and its widgets into the button
    # btn = tk.Button(frame, text="Send", 
    #                 command=lambda s=s, sl=val_slider, sv=stat_var: handle_send(s, sl, sv))
    # btn.pack(side="right")

# Action Button
# send_btn = tk.Button(root, text="SEND DATA", command=handle_send, bg="#2196F3", fg="white", width=20)
# send_btn.pack(pady=20)

# Activity Log
log = tk.Text(root, height=10, width=50)
log.pack(padx=20, pady=10)

root.after(500,handle_send)
root.mainloop()

if ser: ser.close()