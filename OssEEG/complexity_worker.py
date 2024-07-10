from PyQt6.QtCore import QThread, pyqtSignal
from custom_complexity_calculator import CustomComplexityCalculator
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ComplexityWorker(QThread):
    complexityFinished = pyqtSignal(str)

    def __init__(self, data, sf, channel_names, downsample_factor=10):
        super().__init__()
        self.data = data
        self.sf = sf
        self.channel_names = channel_names
        self.downsample_factor = downsample_factor
        logging.debug(f'Initialized ComplexityWorker with {len(channel_names)} channels.')

    def run(self):
        calculator = CustomComplexityCalculator(self.data, self.sf, self.channel_names, self.downsample_factor)
        text = "Complexity Measures:\n\n"

        logging.debug('Starting complexity calculations.')

        apen_df = calculator.approximate_entropy()
        logging.debug('Finished approximate entropy calculations.')

        pe_df = calculator.permutation_entropy()
        logging.debug('Finished permutation entropy calculations.')

        se_df = calculator.spectral_entropy()
        logging.debug('Finished spectral entropy calculations.')

        svd_entropy_df = calculator.svd_entropy()
        logging.debug('Finished SVD entropy calculations.')

        sampen_df = calculator.sample_entropy()
        logging.debug('Finished sample entropy calculations.')

        hfd_df = calculator.higuchi_fd()
        logging.debug('Finished Higuchi fractal dimension calculations.')

        dfa_df = calculator.detrended_fluctuation_analysis()
        logging.debug('Finished detrended fluctuation analysis calculations.')

        for channel in self.channel_names:
            text += f"Channel: {channel}\n"
            text += "--------------------------------\n"
            text += f"- Approximate Entropy: {apen_df[channel + '_apen'].values[0]:.6f}\n"
            text += f"- Permutation Entropy: {pe_df[channel + '_pe'].values[0]:.6f}\n"
            text += f"- Spectral Entropy: {se_df[channel + '_se'].values[0]:.6f}\n"
            text += f"- SVD Entropy: {svd_entropy_df[channel + '_svd_entropy'].values[0]:.6f}\n"
            text += f"- Sample Entropy: {sampen_df[channel + '_sampen'].values[0]:.6f}\n"
            text += f"- Higuchi Fractal Dimension: {hfd_df[channel + '_hfd'].values[0]:.6f}\n"
            text += f"- Detrended Fluctuation Analysis: {dfa_df[channel + '_dfa'].values[0]:.6f}\n"
            text += "\n"

        logging.debug('Finished all complexity calculations.')

        self.complexityFinished.emit(text)
