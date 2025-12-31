# gui/plots.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import time

# Plot Widget
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