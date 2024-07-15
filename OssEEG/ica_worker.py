from PyQt6 import QtCore
from mne.preprocessing import ICA

class ICAWorker(QtCore.QThread):
    icaFinished = QtCore.pyqtSignal(object, object)

    def __init__(self, raw, parent=None):
        super().__init__(parent)
        self.raw = raw

    def run(self):
        filt_raw = self.raw.filter(1., 50., fir_design='firwin', n_jobs=-1)

        ica = ICA(n_components=15, random_state=97, max_iter="auto")
        ica.fit(self.raw)

        explained_var_ratio = ica.get_explained_variance_ratio(filt_raw)
        for channel_type, ratio in explained_var_ratio.items():
            print(
                f"Fraction of {channel_type} variance explained by all components: " f"{ratio}"
            )
        ica_fig = ica.plot_components(show=False)
        self.icaFinished.emit(ica, ica_fig)