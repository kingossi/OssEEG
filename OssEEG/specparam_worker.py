import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from specparam import SpectralModel
from scipy import signal
import concurrent.futures

class SpecparamWorker(QThread):
    specparamFinished = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray)

    def __init__(self, data, sf, min_width, max_width, max_n_peaks, min_peak_height):
        super().__init__()
        self.data = data
        self.sf = sf
        self.min_width = min_width
        self.max_width = max_width
        self.max_n_peaks = max_n_peaks
        self.min_peak_height = min_peak_height
        self.sm = None  # Add this attribute to store the SpectralModel

    def run(self):
        print("SpecparamWorker started")

        # Use ThreadPoolExecutor to parallelize the computation
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.process_channel, self.data))

        all_freqs, all_modeled_spectrum, all_aperiodic_fit, all_periodic_fit = zip(*results)

        # Assuming that all channels have the same frequency range
        avg_freqs = np.mean(all_freqs, axis=0)
        avg_modeled_spectrum = np.mean(all_modeled_spectrum, axis=0)
        avg_aperiodic_fit = np.mean(all_aperiodic_fit, axis=0)
        avg_periodic_fit = np.mean(all_periodic_fit, axis=0)

        print("SpecparamWorker finished processing")
        self.specparamFinished.emit(avg_freqs, avg_modeled_spectrum, avg_aperiodic_fit, avg_periodic_fit)

    def process_channel(self, channel_data):
        freqs, psd = signal.welch(channel_data, self.sf, nperseg=4 * self.sf)

        if freqs[0] == 0:
            freqs = freqs[1:]
            psd = psd[1:]

        freqs = np.asarray(freqs)
        psd = np.asarray(psd)

        model = SpectralModel(peak_width_limits=[self.min_width, self.max_width],
                              max_n_peaks=self.max_n_peaks,
                              min_peak_height=self.min_peak_height)
        model.fit(freqs, psd)
        modeled_spectrum = model.modeled_spectrum_
        aperiodic_fit = model._ap_fit
        periodic_fit = modeled_spectrum - aperiodic_fit  # Extract periodic component

        if self.sm is None:
            self.sm = model  # Store the SpectralModel instance

        return freqs, modeled_spectrum, aperiodic_fit, periodic_fit
