import serial
import time
from datetime import datetime
import json

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

temp_sensor.send_sensor_data()

# 3. (Optional) close port
ser.close()
