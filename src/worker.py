# gui/worker.py
from PySide6.QtCore import QObject, Signal
import serial, time, json

# Map JSON strings to PySerial constants
PARITY_MAP = {
    "N": serial.PARITY_NONE,
    "E": serial.PARITY_EVEN,
    "O": serial.PARITY_ODD
}

# Load the config
with open('config/ranges.json', 'r') as f:
    config = json.load(f)

# Extract serial settings
s_cfg = config['serial_config']

# Define the Worker logic (Serial Receive)
class Worker(QObject):
    data_ready = Signal(dict)

    def __init__(self):
        super().__init__()
        self._running = True
                #  --- Serial Setup ---
        try:
            # Open serial port (UART init)
            self.ser = serial.Serial(
                port=s_cfg['port'],
                baudrate=s_cfg['baudrate'],
                bytesize=s_cfg['bytesize'],
                parity=PARITY_MAP.get(s_cfg['parity'], serial.PARITY_NONE),
                stopbits=s_cfg['stopbits'],
                timeout=s_cfg['timeout']
            )
            time.sleep(1)
        except Exception as e:
            print(f"Serial Error: {e}. Running in simulation mode (no hardware).")
            self.ser = None

    def run(self):
        while self._running:
            if self.ser and self.ser.is_open:
                try:
                    # readline() reads until \n and returns bytes
                    line = self.ser.readline()
                    
                    # Convert bytes to string and remove trailing whitespace (\n, \r)
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line:
                        # 2. Parse the JSON string into a Python dictionary
                        data = json.loads(decoded_line)
                        # print(data)
                        self.data_ready.emit(data)    # emit signal instead of queue
                except Exception as e:
                    print(f"Error: {e}")

    def stop(self):
        self._running = False