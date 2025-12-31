# gui/main.py
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread
from worker import Worker
from plots import SensorPlotWidget
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,QLabel,QPlainTextEdit)
from PySide6.QtCore import QThread
from PySide6.QtGui import QColor, QBrush
from datetime import datetime
import traceback
import threading
import requests
import json
import sys

# Webhook URL and Functions
WEBHOOK_URL="https://webhook.site/22d55c77-d3a2-4a36-9112-fd2b6e170b4c"

def send_webhook(payload):
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        print("Webhook sent:", response.status_code)
    except Exception as e:
        print("Webhook failed:", e)

def trigger_webhook_async(payload):
    threading.Thread(
        target=send_webhook,
        args=(payload,),
        daemon=True
    ).start()



# Main Window
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
        
        # Load the configuration file for sensors ranges
        with open('config/ranges.json', 'r') as f:
            self.sensor_ranges = json.load(f)

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
        
        # Create the Label for global status
        self.indicator = QLabel("System Status")
        self.indicator.setStyleSheet("background-color: red; color: white; padding: 5px; font-weight: bold;")

        self.log_header = QLabel("<b>Alarm & Event History</b>")
        self.alarm_log = QPlainTextEdit()
        self.alarm_log.setReadOnly(True)
        self.alarm_log.setMaximumBlockCount(100) # Keep only the last 100 entries
        self.alarm_log.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")
        

        layout = QVBoxLayout(self)

        # Add Widgets to Layout
        layout.addWidget(self.indicator)
        layout.addWidget(self.table)
        layout.addWidget(self.log_header)
        layout.addWidget(self.alarm_log)

        
    def update_table(self, data):
        try:
            name = data.get("name")
            val=data.get("value")
            stat=data.get("status")
            # Update Values
            if name in self.sensor_rows:
                self.value_items[name].setText(str(data.get("value")))
                self.timestamp_items[name].setText(str(datetime.fromtimestamp(data.get("timestamp"))))
                self.status_items[name].setText(data.get("status"))
                # Update plot
                self.plot_widgets[name].add_point(data.get("value"),data.get("timestamp"))

                # Check for errors and set alarms
                if self.sensor_ranges[name].get("low") <= val <= self.sensor_ranges[name].get("high") and stat=="OK":
                    for col in range(4):
                        self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#433F3F")))
                        self.value_alarm_active[name]=False
                        
                elif self.sensor_ranges[name].get("low") > val:
                    for col in range(4):
                            self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#F70707")))
                            if self.value_alarm_active[name]==False:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                log_entry = f"[{timestamp}] ALARM: {name} value below Low limit! (Value: {val})"
                                self.alarm_log.appendPlainText(log_entry)
                                self.value_alarm_active[name]=True
                                payload = {
                                            "event": "ALARM_TRIGGERED",
                                            "sensor": name,
                                            "value": val,
                                            "timestamp": data.get("timestamp"),
                                            "message": f"{name} Below Low limit"
                                        }
                                trigger_webhook_async(payload)
            
                elif val > self.sensor_ranges[name].get("high"): 
                    for col in range(4):
                        self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#F70707")))
                        if self.value_alarm_active[name]==False:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_entry = f"[{timestamp}] ALARM: {name} value above High limit! (Value: {val})"
                            self.alarm_log.appendPlainText(log_entry)
                            self.value_alarm_active[name]=True
                            payload = {
                                            "event": "ALARM_TRIGGERED",
                                            "sensor": name,
                                            "value": val,
                                            "timestamp": data.get("timestamp"),
                                            "message": f"{name} Above High limit"
                                        }
                            trigger_webhook_async(payload)

                elif stat=="FAULTY": 
                    for col in range(4):
                        self.table.item(self.sensor_rows.get(name),col).setBackground(QBrush(QColor("#F70707")))
                        if self.value_alarm_active[name]==False:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_entry = f"[{timestamp}] ALARM: {name} Sensor is FAULTY!"
                            self.alarm_log.appendPlainText(log_entry)
                            self.value_alarm_active[name]=True
                            payload = {
                                            "event": "ALARM_TRIGGERED",
                                            "sensor": name,
                                            "value": val,
                                            "timestamp": data.get("timestamp"),
                                            "message": f"{name} Sensor Faulty"
                                        }
                            trigger_webhook_async(payload)

        except Exception as e:
            print("CRASH INSIDE update_table:", e)
            traceback.print_exc()
                
        # Extract all current statuses from the table items
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
                

# Main App
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

