from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,QLabel,QPlainTextEdit)
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import QTimer
from datetime import datetime
import pyqtgraph as pg
import traceback
import serial
import time
import json
import sys


# 1. Define the Worker logic
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


class SensorPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


        self.time_data = []   # timestamps (seconds)
        self.value_data = []  # sensor values
        self.window = 20      # seconds

        self.plot = pg.PlotWidget()
        self.plot.setBackground("w")
        self.plot.showGrid(x=True, y=True)

        self.curve = self.plot.plot(pen=pg.mkPen(color="b", width=2))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot)

    def add_point(self, value, timestamp):
        # 1. Append new data
        self.time_data.append(timestamp)
        self.value_data.append(value)

        # 2. Remove old data (rolling window)
        cutoff = time.time() - self.window
        while self.time_data and self.time_data[0] < cutoff:
            self.time_data.pop(0)
            self.value_data.pop(0)

        # 3. Convert to relative time (0 → window seconds)
        t0 = self.time_data[0]
        x = [t - t0 for t in self.time_data]

        # 4. Update plot
        self.curve.setData(x, self.value_data)



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Data Table")
        self.resize(400, 300)

        # 1. Setup Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Sensor Name", "Value","Timestamp","Status","Plot"])

        # Make columns stretch to fit window
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.sensor_ranges = {"Temperature": (-50.0, 50.0),
                              "Humidity": (10.0, 90.0),
                              "Pressure": (100.0, 900.0),
                              "Speed": (50.0, 200.0),
                              "Counter": (10.0, 400.0)}

        # 2. Define rows for each sensor
        self.sensor_rows = {
            "Temperature": 0,
            "Humidity": 1,
            "Pressure": 2,
            "Speed": 3,
            "Counter": 4
        }
        self.table.setRowCount(len(self.sensor_rows))

        self.value_items = {}
        self.timestamp_items = {}
        self.status_items = {}
        # Initialize table with sensor names
        for name, row in self.sensor_rows.items():
            self.table.setItem(row, 0, QTableWidgetItem(name))

            value_item = QTableWidgetItem("---")
            timestamp_item = QTableWidgetItem("---")
            status_item = QTableWidgetItem("---")

            self.table.setItem(row, 1, value_item)
            self.table.setItem(row, 2, timestamp_item)
            self.table.setItem(row, 3, status_item)

            self.value_items[name] = value_item
            self.timestamp_items[name] = timestamp_item
            self.status_items[name] = status_item

        self.plot_widgets = {}

        for name, row in self.sensor_rows.items():
            plot_widget = SensorPlotWidget()
            self.table.setCellWidget(row, 4, plot_widget)
            self.plot_widgets[name] = plot_widget

            self.table.setRowHeight(row, 150)

        self.table.setColumnWidth(4, 300)

        self.value_alarm_active = {name: False for name in self.sensor_rows}
        
        # 1. Create the Label
        self.indicator = QLabel("System Status")
        self.indicator.setStyleSheet("background-color: red; color: white; padding: 5px; font-weight: bold;")

        self.log_header = QLabel("<b>Alarm & Event History</b>")
        self.alarm_log = QPlainTextEdit()
        self.alarm_log.setReadOnly(True)
        self.alarm_log.setMaximumBlockCount(100) # Keep only the last 100 entries
        self.alarm_log.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")
        

        layout = QVBoxLayout(self)

        # 3. Add Label FIRST (Top)
        layout.addWidget(self.indicator)
        layout.addWidget(self.table)
        layout.addWidget(self.log_header)
        layout.addWidget(self.alarm_log)

        
    def update_table(self, data):
        try:
            name = data.get("name")
            val=data.get("value")
            stat=data.get("status")
            if name in self.sensor_rows:
                self.value_items[name].setText(str(data.get("value")))
                self.timestamp_items[name].setText(str(datetime.fromtimestamp(data.get("timestamp"))))
                self.status_items[name].setText(data.get("status"))
                # Update plot
                self.plot_widgets[name].add_point(data.get("value"),data.get("timestamp"))
                if self.sensor_ranges[name][0] <= val <= self.sensor_ranges[name][1] and stat=="OK":
                    for col in range(4):
                        self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#433F3F")))
                        self.value_alarm_active[name]=False
                elif self.sensor_ranges[name][0] > val:
                    for col in range(4):
                            self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#F70707")))
                            if self.value_alarm_active[name]==False:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                log_entry = f"[{timestamp}] ALARM: {name} value below Low limit! (Value: {val})"
                                self.alarm_log.appendPlainText(log_entry)
                                self.value_alarm_active[name]=True
            
                elif val > self.sensor_ranges[name][1]: 
                    for col in range(4):
                        self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#F70707")))
                        if self.value_alarm_active[name]==False:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_entry = f"[{timestamp}] ALARM: {name} value above High limit! (Value: {val})"
                            self.alarm_log.appendPlainText(log_entry)
                            self.value_alarm_active[name]=True

                elif stat=="FAULTY": 
                    for col in range(4):
                        self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#F70707")))
                        if self.value_alarm_active[name]==False:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_entry = f"[{timestamp}] ALARM: {name} Sensor is FAULTY!"
                            self.alarm_log.appendPlainText(log_entry)
                            self.value_alarm_active[name]=True
        except:
            print("CRASH INSIDE update_table:", e)
            traceback.print_exc()
                
        # 2. Extract all current statuses from the table items
        # This checks if ANY sensor row currently says something other than "OK"
        current_statuses = [item.text() for item in self.status_items.values()]
        
        if any(s != "OK" for s in current_statuses):
            self.update_status("FAULT")
            self.indicator.setText("System Status: FAULT DETECTED")
        else:
            self.update_status("OK")
            self.indicator.setText("System Status: ALL OK")

    def update_status(self, status):
        if status == "OK":
            # Green background with rounded corners
            self.indicator.setStyleSheet("background-color: green; border-radius: 10px;")
        else:
            self.indicator.setStyleSheet("background-color: red; border-radius: 10px;")
                


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

