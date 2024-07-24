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
        self.regions = []

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.plotWidget = pg.PlotWidget(title="EEG Time Series")

        # Set background to white and axis and grid color to black
        self.plotWidget.setBackground('w')
        self.plotWidget.getAxis('left').setPen('k')
        self.plotWidget.getAxis('bottom').setPen('k')
        self.plotWidget.getAxis('left').setTextPen('k')
        self.plotWidget.getAxis('bottom').setTextPen('k')
        self.plotWidget.showGrid(x=True, y=True, alpha=0.5)

        self.plotWidget.setDownsampling(mode='peak')
        self.plotWidget.setClipToView(True)
        self.plotWidget.setMouseEnabled(x=True, y=True)
        self.plotWidget.setMenuEnabled(True)
        self.plotWidget.setLimits(xMin=0, xMax=None, yMin=0, yMax=None)

        self.toggleButton = QtWidgets.QPushButton("Switch to Zoom/Pan Mode")
        self.toggleButton.setFixedSize(200, 50)
        self.toggleButton.clicked.connect(self.toggleMode)

        self.addRegionButton = QtWidgets.QPushButton("Add Artifact Region")
        self.addRegionButton.setFixedSize(200, 50)
        self.addRegionButton.clicked.connect(self.addRegion)

        self.removeRegionsButton = QtWidgets.QPushButton("Interpolate Artifact Regions")
        self.removeRegionsButton.setFixedSize(200, 50)
        self.removeRegionsButton.clicked.connect(self.removeRegions)

        layout.addWidget(self.plotWidget)
        layout.addWidget(self.toggleButton)
        layout.addWidget(self.addRegionButton)
        layout.addWidget(self.removeRegionsButton)
        self.setLayout(layout)

    def toggleMode(self):
        if self.isScrollMode:
            self.plotWidget.getViewBox().setMouseMode(pg.ViewBox.RectMode)  # Enable rectangle zoom mode
            self.toggleButton.setText("Switch to Scroll Mode")
        else:
            self.plotWidget.getViewBox().setMouseMode(pg.ViewBox.PanMode)  # Enable pan mode
            self.toggleButton.setText("Switch to Zoom/Pan Mode")
        self.isScrollMode = not self.isScrollMode

    def addRegion(self):
        region = pg.LinearRegionItem()
        self.plotWidget.addItem(region)
        self.regions.append(region)

    def removeRegions(self):
        for region in self.regions:
            self.interpolateArtifactRegion(region.getRegion())
            self.plotWidget.removeItem(region)
        self.regions = []
        self.updatePlot(self.selected_channel_names)  # Refresh the plot with updated data

    def interpolateArtifactRegion(self, region):
        start, end = region
        start_idx = int(start * self.sf)
        end_idx = int(end * self.sf)
        for ch_idx in range(self.data.shape[0]):
            self.data[ch_idx, start_idx:end_idx] = self.interpolate(self.data[ch_idx, :], start_idx, end_idx)

    def interpolate(self, data, start_idx, end_idx):
        """Linearly interpolate the data between start_idx and end_idx."""
        if start_idx == 0:
            start_val = data[end_idx]
        else:
            start_val = data[start_idx - 1]

        if end_idx == len(data):
            end_val = data[start_idx - 1]
        else:
            end_val = data[end_idx]

        interp_values = np.linspace(start_val, end_val, end_idx - start_idx)
        return interp_values

    def plot(self, data, sf, channel_names, selected_channels):
        self.data = data
        self.sf = sf
        self.channel_names = channel_names
        self.selected_channel_names = selected_channels
        self.updatePlot(selected_channels)

    def updatePlot(self, selected_channels):
        if not selected_channels:
            return

        selected_channels = selected_channels[:self.max_display_channels]

        self.plotWidget.clear()
        time = np.arange(self.data.shape[1]) / self.sf
        offset = 0
        self.curves = []
        max_amplitude = np.nanmax(np.abs(self.data))  # Max amplitude for scaling
        margin = max_amplitude  # Add margin at the bottom

        for i, ch_name in enumerate(selected_channels):
            ch_idx = self.channel_names.index(ch_name)
            ch_data = self.data[ch_idx, :] + offset + margin  # Add margin to each channel
            curve = self.plotWidget.plot(time, ch_data, pen='k')  # Set pen color to black
            self.curves.append(curve)
            offset += max_amplitude * 2  # Adjust the offset for stacking

        self.plotWidget.setLabel('bottom', 'Time (s)', color='k')
        self.plotWidget.setLabel('left', 'Amplitude (uV)', color='k')

        # Set the y-axis range to fit the data
        self.plotWidget.setYRange(0, offset + margin)

        # Label each channel on the y-axis
        yticks = [(i * max_amplitude * 2 + margin, ch) for i, ch in enumerate(selected_channels)]
        self.plotWidget.getAxis('left').setTicks([yticks])
