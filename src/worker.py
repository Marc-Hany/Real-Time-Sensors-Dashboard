# gui/worker.py
from PySide6.QtCore import QObject, Signal
import serial, time, json

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