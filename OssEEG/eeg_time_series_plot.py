import sys
import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtGui, QtCore


class EEGTimeSeriesPlot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.plotWidget = None
        self.toggleButton = None
        self.initUI()
        self.data = None
        self.sf = None
        self.channel_names = None
        self.max_display_channels = 20
        self.isScrollMode = True

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.plotWidget = pg.PlotWidget(title="EEG Time Series")
        self.plotWidget.setDownsampling(mode='peak')
        self.plotWidget.setClipToView(True)
        self.plotWidget.setMouseEnabled(x=True, y=True)
        self.plotWidget.setMenuEnabled(True)
        self.plotWidget.setLimits(xMin=0, xMax=None, yMin=0, yMax=None)

        self.toggleButton = QtWidgets.QPushButton("Switch to Zoom/Pan Mode")
        self.toggleButton.clicked.connect(self.toggleMode)

        layout.addWidget(self.plotWidget)
        layout.addWidget(self.toggleButton)
        self.setLayout(layout)

    def toggleMode(self):
        if self.isScrollMode:
            self.plotWidget.getViewBox().setMouseMode(pg.ViewBox.RectMode)  # Enable rectangle zoom mode
            self.toggleButton.setText("Switch to Scroll Mode")
        else:
            self.plotWidget.getViewBox().setMouseMode(pg.ViewBox.PanMode)  # Enable pan mode
            self.toggleButton.setText("Switch to Zoom/Pan Mode")
        self.isScrollMode = not self.isScrollMode

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
        for i, ch_name in enumerate(selected_channels):
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

        # Label each channel on the y-axis
        yticks = [(i * np.max(np.abs(self.data[self.channel_names.index(ch), :])) * 2, ch) for i, ch in
                  enumerate(selected_channels)]
        self.plotWidget.getAxis('left').setTicks([yticks])



