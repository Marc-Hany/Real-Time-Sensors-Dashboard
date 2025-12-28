import sys
import numpy as np
import random
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout, QWidget, QLabel)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont
import pyqtgraph as pg

# Configuration
SENSOR_COUNT = 5
BUFFER_SIZE = 100  # Number of points for 20 seconds at 5Hz
UPDATE_INTERVAL = 200  # ms (5 updates per second)

class SensorDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Sensor Dashboard (2025)")
        self.resize(900, 600)

        # 1. Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 2. Global System Status Indicator
        self.status_label = QLabel("SYSTEM STATUS: INITIALIZING")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setStyleSheet("background-color: gray; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.status_label)

        # 3. Sensor Table
        self.table = QTableWidget(SENSOR_COUNT, 5)
        self.table.setHorizontalHeaderLabels(["Sensor Name", "Latest Value", "Timestamp", "Status", "Real-time Plot"])
        self.table.setColumnWidth(4, 250) # Make plot column wider
        self.table.verticalHeader().setDefaultSectionSize(60) # Taller rows for plots
        layout.addWidget(self.table)

        # 4. Data Initialization
        self.sensor_data = {i: np.zeros(BUFFER_SIZE) for i in range(SENSOR_COUNT)}
        self.plots = []
        self.sensor_names = ["Temp_Core", "Pressure_A", "Flow_Main", "Voltage_B", "Humidity_Ext"]

        for i in range(SENSOR_COUNT):
            # Name
            self.table.setItem(i, 0, QTableWidgetItem(self.sensor_names[i]))
            
            # Sparkline Plot Widget
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground('w')
            plot_widget.setMouseEnabled(x=False, y=False) # Disable interaction
            plot_widget.hideAxis('bottom')
            plot_widget.hideAxis('left')
            
            curve = plot_widget.plot(pen=pg.mkPen(color='b', width=2))
            self.plots.append(curve)
            self.table.setCellWidget(i, 4, plot_widget)

        # 5. Timer for live updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(UPDATE_INTERVAL)

    def update_dashboard(self):
        worst_status = "GREEN"
        current_time = datetime.now().strftime("%H:%M:%S")

        for i in range(SENSOR_COUNT):
            # Simulate data
            new_val = random.uniform(20, 100)
            self.sensor_data[i] = np.roll(self.sensor_data[i], -1)
            self.sensor_data[i][-1] = new_val

            # Determine Status & Color
            status, color = "GREEN", QColor(144, 238, 144) # Light Green
            if new_val > 85:
                status, color = "RED", QColor(255, 182, 193) # Light Red
                worst_status = "RED"
            elif new_val > 65:
                status, color = "YELLOW", QColor(255, 255, 224) # Light Yellow
                if worst_status != "RED": worst_status = "YELLOW"

            # Update Table Items
            val_item = QTableWidgetItem(f"{new_val:.2f}")
            time_item = QTableWidgetItem(current_time)
            status_item = QTableWidgetItem(status)

            # Apply Color-Coding
            for col, item in enumerate([val_item, time_item, status_item], start=1):
                item.setBackground(color)
                self.table.setItem(i, col, item)

            # Update Sparkline
            self.plots[i].setData(self.sensor_data[i])

        # Update Global Indicator
        self.update_global_status(worst_status)

    def update_global_status(self, status):
        colors = {"GREEN": "#2ecc71", "YELLOW": "#f1c40f", "RED": "#e74c3c"}
        self.status_label.setText(f"SYSTEM STATUS: {status}")
        self.status_label.setStyleSheet(f"background-color: {colors[status]}; color: white; padding: 10px; border-radius: 5px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SensorDashboard()
    window.show()
    sys.exit(app.exec())
