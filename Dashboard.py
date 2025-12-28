import serial
import time
import json
import threading

def read_serial_line(ser):
    """
    Reads from the serial port until a newline character is found.
    """
    while True:
        if ser and ser.is_open:
            # readline() reads until \n and returns bytes
            line = ser.readline()
            
            # Convert bytes to string and remove trailing whitespace (\n, \r)
            decoded_line = line.decode('utf-8').strip()

            if decoded_line:
                    # 2. Parse the JSON string into a Python dictionary
                    data = json.loads(decoded_line)
                    print(data)
                    # 3. Extract specific values using their keys
                    # Example: If your JSON is {"name": "Temp", "value": 25.5}
                    name = data.get("name", "Unknown")
                    val = data.get("value", 0.0)
                    timestamp = data.get("timestamp", 0.0)
                    status = data.get("status", "N/A")
                    # print(name,val,timestamp,status)
            
            # if decoded_line:
            #     print(f"Received: {decoded_line}")
            # return decoded_line
        # return None

# --- Serial Setup ---
try:
    # Open serial port (UART init)
    ser = serial.Serial(
        port='COM2',        # change this to your COM port
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

# Create the thread
t = threading.Thread(target=read_serial_line,args=(ser,))

# Start the thread
t.start()

# Main thread continues
while True:
    print("Main thread running")
    time.sleep(2)