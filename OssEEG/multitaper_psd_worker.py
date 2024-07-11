import numpy as np
from PyQt6 import QtCore
from mne.time_frequency import psd_array_multitaper


class MultitaperPSDWorker(QtCore.QThread):
    resultReady = QtCore.pyqtSignal(np.ndarray, np.ndarray,tuple)

    def __init__(self, data, sf, max_freq, band_d, cache_key):
        super().__init__()
        self.data = data
        self.sf = sf
        self.max_freq = max_freq
        self.band_d = band_d
        self.cache_key = cache_key

    def run(self):
        if self.data.ndim == 2:  # Handle multi-channel data
            psd_all = []
            for channel in self.data:
                psd, freqs = psd_array_multitaper(channel, sfreq=self.sf, fmax=self.max_freq, adaptive=True, low_bias=True, normalization='full', verbose=0)
                psd_all.append(psd)
            psd = np.mean(psd_all, axis=0)
        else:  # Handle single-channel data
            psd, freqs = psd_array_multitaper(self.data, sfreq=self.sf, fmax=self.max_freq, adaptive=True, low_bias=True, normalization='full', verbose=0)

        self.resultReady.emit(freqs, psd, self.cache_key)
