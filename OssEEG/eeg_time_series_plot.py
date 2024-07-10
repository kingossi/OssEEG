import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets

class EEGTimeSeriesPlot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.plotWidget = None
        self.initUI()
        self.data = None
        self.sf = None
        self.channel_names = None
        self.max_display_channels = 20

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.plotWidget = pg.PlotWidget(title="EEG Time Series")
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)

    def plot(self, data, sf, channel_names, selected_channels):
        self.data = data
        self.sf = sf
        self.channel_names = channel_names
        self.updatePlot(selected_channels)

    def updatePlot(self, selected_channels):
        if not selected_channels:
            return

        selected_channels = selected_channels[:self.max_display_channels]

        self.plotWidget.clear()
        time = np.arange(self.data.shape[1]) / self.sf
        offset = 0
        curves = []
        for ch_name in selected_channels:
            ch_idx = self.channel_names.index(ch_name)
            ch_data = self.data[ch_idx, :] + offset
            curve = self.plotWidget.plot(time, ch_data, pen='b')
            curves.append(curve)
            offset += np.max(np.abs(self.data[ch_idx, :])) * 2  # Adjust the offset for stacking

        self.plotWidget.setLabel('bottom', 'Time (s)')
        self.plotWidget.setLabel('left', 'Channels')
        self.plotWidget.showGrid(x=True, y=True)

        # Set the y-axis range to fit the data
        self.plotWidget.setYRange(0, offset)
