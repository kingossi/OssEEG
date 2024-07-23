import os
from PyQt6 import QtCore
from matplotlib import pyplot as plt
from mne.preprocessing import ICA


class ICAWorker(QtCore.QThread):
    icaFinished = QtCore.pyqtSignal(object, str, object)

    def __init__(self, raw, parent=None):
        super().__init__(parent)
        self.raw = raw

    def run(self):
        filt_raw = self.raw.filter(1., 50., fir_design='firwin', n_jobs=-1)

        ica = ICA(n_components=15, random_state=97, max_iter="auto")
        ica.fit(self.raw)

        explained_var_ratio = ica.get_explained_variance_ratio(filt_raw)
        for channel_type, ratio in explained_var_ratio.items():
            print(f"Fraction of {channel_type} variance explained by all components: {ratio}")

        fig, axes = plt.subplots(3, 5, figsize=(15, 9))
        ica.plot_components(show=False, axes=axes)

        # Save the figure
        image_path = "ica_components.png"
        fig.savefig(image_path)
        plt.close(fig)

        self.icaFinished.emit(ica, image_path, fig)
