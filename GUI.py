from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import QObject, QThread, Signal
import time
import sys
import serial
import json

# 1. Define the Worker logic
class Worker(QObject):
    data_ready = Signal(dict)

    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        while self._running:
            if ser and ser.is_open:
                # readline() reads until \n and returns bytes
                line = ser.readline()
                
                # Convert bytes to string and remove trailing whitespace (\n, \r)
                decoded_line = line.decode('utf-8').strip()
                if decoded_line:
                    # 2. Parse the JSON string into a Python dictionary
                    data = json.loads(decoded_line)
                    print(data)
                    self.data_ready.emit(data)    # emit signal instead of queue

    def stop(self):
        self._running = False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Data Table")
        self.resize(400, 300)

        # 1. Setup Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Sensor Name", "Value","Timestamp","Status"])
        
        # Make columns stretch to fit window
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 2. Define rows for each sensor
        self.sensor_rows = {
            "Temperature": 0,
            "Humidity": 1,
            "Pressure": 2,
            "Speed": 3,
            "Counter": 4
        }
        self.table.setRowCount(len(self.sensor_rows))

        # Initialize table with sensor names
        for name, row in self.sensor_rows.items():
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem("---"))
            self.table.setItem(row, 2, QTableWidgetItem("---"))
            self.table.setItem(row, 3, QTableWidgetItem("---"))

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

    def update_table(self,data):
        name = data.get("name")
        if name in self.sensor_rows:
            row = self.sensor_rows[name]
            # Update specific cells
            self.table.setItem(row, 1, QTableWidgetItem(str(data.get("value"))))
            self.table.setItem(row, 2, QTableWidgetItem(str(data.get("timestamp"))))
            self.table.setItem(row, 3, QTableWidgetItem(data.get("status")))



#  --- Serial Setup ---
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

app = QApplication(sys.argv)

window = MainWindow()
window.show()

# Thread and worker setup
thread = QThread()
worker = Worker()
worker.moveToThread(thread)

# Connect signals
thread.started.connect(worker.run)       # start worker when thread starts
worker.data_ready.connect(lambda val: window.update_table(val))


# Stop thread properly on exit
def on_exit():
    worker.stop()
    thread.quit()
    thread.wait()

app.aboutToQuit.connect(on_exit)
thread.start() # MANDATORY: Start the thread!
app.exec()

