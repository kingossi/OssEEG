import os
import logging
import matplotlib.pyplot as plt
from PyQt6 import QtCore
from mne.preprocessing import ICA
import mne

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)


class ICAWorker(QtCore.QThread):
    icaFinished = QtCore.pyqtSignal(object, object)

    def __init__(self, raw, parent=None):
        super().__init__(parent)
        self.raw = raw

    def run(self):
        # Set montage if no digitization points are found
        if not self.raw.info['dig']:
            montage = mne.channels.make_standard_montage('standard_1020')
            self.raw.set_montage(montage)

        filt_raw = self.raw.filter(1., 50., fir_design='firwin', n_jobs=-1)

        ica = ICA(n_components=15, random_state=97, max_iter="auto")
        ica.fit(self.raw)

        explained_var_ratio = ica.get_explained_variance_ratio(filt_raw)
        for channel_type, ratio in explained_var_ratio.items():
            print(f"Fraction of {channel_type} variance explained by all components: {ratio}")

        fig, axes = plt.subplots(3, 5, figsize=(15, 9))
        ica.plot_components(show=False, axes=axes)

        # Emit the ICA object and the figure
        self.icaFinished.emit(ica, fig)
