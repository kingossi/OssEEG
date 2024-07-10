import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets
from specparam_worker import SpecparamWorker
import hashlib

class SpecparamAnalysisPlot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.aperiodic_curve = None
        self.specparam_curve = None
        self.specparam_plot = None
        self.periodic_curve = None
        self.plotWidget = None
        self.psd_plot = None
        self.initUI()
        self.specparam_worker = None
        self.cache = {}

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.plotWidget = pg.GraphicsLayoutWidget()
        self.psd_plot = self.plotWidget.addPlot(title="Periodic Component")
        self.periodic_curve = self.psd_plot.plot(pen='m')

        self.specparam_plot = self.plotWidget.addPlot(title="Specparam Model Fit")
        self.specparam_curve = self.specparam_plot.plot(pen='r')
        self.aperiodic_curve = self.specparam_plot.plot(pen='g')

        layout.addWidget(self.plotWidget)
        self.setLayout(layout)

    def plot(self, data, sf):
        self.psd_plot.clear()
        self.specparam_plot.clear()

        # Create a unique hash for the data to use as a cache key
        data_hash = hashlib.md5(data.tobytes()).hexdigest()
        cache_key = (data.shape, data_hash, sf)

        print(f"Plotting with cache_key: {cache_key}")

        if cache_key in self.cache:
            print("Using cached data")
            freqs, modeled_spectrum, aperiodic_fit, periodic_fit = self.cache[cache_key]
            self.update_plot(freqs, modeled_spectrum, aperiodic_fit, periodic_fit)
        else:
            print("Starting SpecparamWorker")
            self.specparam_worker = SpecparamWorker(data, sf)
            self.specparam_worker.specparamFinished.connect(self.update_plot_and_cache)
            self.specparam_worker.start()

    def update_plot_and_cache(self, freqs, modeled_spectrum, aperiodic_fit, periodic_fit):
        data = self.specparam_worker.data
        sf = self.specparam_worker.sf

        # Create a unique hash for the data to use as a cache key
        data_hash = hashlib.md5(data.tobytes()).hexdigest()
        cache_key = (data.shape, data_hash, sf)

        print(f"Caching data with cache_key: {cache_key}")

        self.cache[cache_key] = (freqs, modeled_spectrum, aperiodic_fit, periodic_fit)
        self.update_plot(freqs, modeled_spectrum, aperiodic_fit, periodic_fit)

    def update_plot(self, freqs, modeled_spectrum, aperiodic_fit, periodic_fit):
        print("Updating plot")
        self.periodic_curve.setData(freqs, periodic_fit)  # Plot periodic component
        self.specparam_curve.setData(freqs, modeled_spectrum)
        self.aperiodic_curve.setData(freqs, aperiodic_fit)

        self.psd_plot.addItem(self.periodic_curve)
        self.specparam_plot.addItem(self.specparam_curve)
        self.specparam_plot.addItem(self.aperiodic_curve)
