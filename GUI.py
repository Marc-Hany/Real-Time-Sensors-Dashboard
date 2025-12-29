from PySide6.QtWidgets import (QApplication, QMainWindow,QWidget, QLabel, QVBoxLayout)
from PySide6.QtCore import QObject, QThread, Signal, Slot
import time
import sys
import random
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
            else:
                print("shit")

    def stop(self):
        self._running = False


class SensorCard(QWidget):
    def __init__(self, name):
        super().__init__()

        self.name=name
        self.name_label = QLabel(name)
        self.value_label = QLabel("Value: ---")
        self.status_label = QLabel("Status: ---")

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def update_data(self,data):
        if data["name"]==self.name:
            value= data["value"]
            status= data["status"]
            self.value_label.setText(f"Value: {value}")
            self.status_label.setText(f"Status: {status}")


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

main = QWidget()
layout = QVBoxLayout(main)

temp_card = SensorCard("Temperature")
hum_card = SensorCard("Humidity")
Pre_card = SensorCard("Pressure")
Speed_card = SensorCard("Speed")
Count_card = SensorCard("Counter")

layout.addWidget(temp_card)
layout.addWidget(hum_card)
layout.addWidget(Pre_card)
layout.addWidget(Speed_card)
layout.addWidget(Count_card)

main.show()
# Thread and worker setup
thread = QThread()
worker = Worker()
worker.moveToThread(thread)

# Connect signals
thread.started.connect(worker.run)       # start worker when thread starts
worker.data_ready.connect(lambda val: temp_card.update_data(val))
worker.data_ready.connect(lambda val: hum_card.update_data(val))
worker.data_ready.connect(lambda val: Pre_card.update_data(val))
worker.data_ready.connect(lambda val: Speed_card.update_data(val))
worker.data_ready.connect(lambda val: Count_card.update_data(val))


# Stop thread properly on exit
def on_exit():
    worker.stop()
    thread.quit()
    thread.wait()

app.aboutToQuit.connect(on_exit)
thread.start() # MANDATORY: Start the thread!
app.exec()

