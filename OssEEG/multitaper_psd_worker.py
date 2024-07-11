import numpy as np
from PyQt6 import QtCore


class MultitaperPSDWorket(QtCore.QThread):
    resultReady = QtCore.pyqtSignal(np.ndarray, np.ndarray,tuple)

    def __init__(self, data, sf, max_freq, band_d, cache_key):
        super().__init__()
        self.data = data
        self.sf = sf
        self.max_freq = max_freq
        self.band_d = band_d
        self.cache_key = cache_key

    def run(self):
        if self.data.ndim == 2:
            p
