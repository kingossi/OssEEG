import numpy as np
import pandas as pd
from scipy.signal import welch, decimate
import antropy as ant
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomComplexityCalculator:
    def __init__(self, data, sf, channel_names, downsample_factor=10):
        self.data = data
        self.sf = sf
        self.channel_names = channel_names
        self.downsample_factor = downsample_factor
        self.data = self.downsample_data(self.data, downsample_factor)
        self.sf /= downsample_factor
        logging.debug(f'Initialized CustomComplexityCalculator with {len(channel_names)} channels.')

    def downsample_data(self, data, factor):
        """Downsamples the data by the given factor."""
        return np.array([decimate(channel_data, factor) for channel_data in data])

    def approximate_entropy(self, m=2):
        """Compute approximate entropy (ApEn) for each channel in the data."""
        apen_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating approximate entropy for channel {self.channel_names[idx]}')
            apen = ant.app_entropy(channel_data, order=m)
            apen_df[self.channel_names[idx] + '_apen'] = [apen]
        return apen_df

    def permutation_entropy(self, order=3, delay=1, normalize=False):
        pe_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating permutation entropy for channel {self.channel_names[idx]}')
            pe = ant.perm_entropy(channel_data, order=order, delay=delay, normalize=normalize)
            pe_df[self.channel_names[idx] + '_pe'] = [pe]
        return pe_df

    def spectral_entropy(self):
        se_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating spectral entropy for channel {self.channel_names[idx]}')
            se = ant.spectral_entropy(channel_data, self.sf, method='welch', normalize=True)
            se_df[self.channel_names[idx] + '_se'] = [se]
        return se_df

    def svd_entropy(self):
        svd_entropy_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating SVD entropy for channel {self.channel_names[idx]}')
            svd_ent = ant.svd_entropy(channel_data, order=3)
            svd_entropy_df[self.channel_names[idx] + '_svd_entropy'] = [svd_ent]
        return svd_entropy_df

    def sample_entropy(self, m=2):
        sampen_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating sample entropy for channel {self.channel_names[idx]}')
            sampen = ant.sample_entropy(channel_data, order=m)
            sampen_df[self.channel_names[idx] + '_sampen'] = [sampen]
        return sampen_df

    def higuchi_fd(self, kmax=10):
        hfd_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating Higuchi fractal dimension for channel {self.channel_names[idx]}')
            hfd = ant.higuchi_fd(channel_data, kmax=kmax)
            hfd_df[self.channel_names[idx] + '_hfd'] = [hfd]
        return hfd_df

    def detrended_fluctuation_analysis(self):
        dfa_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating detrended fluctuation analysis for channel {self.channel_names[idx]}')
            dfa = ant.detrended_fluctuation(channel_data)
            dfa_df[self.channel_names[idx] + '_dfa'] = [dfa]
        return dfa_df

    def coastline(self):
        coastline_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating coastline for channel {self.channel_names[idx]}')
            coastline = np.abs(np.diff(channel_data)).sum()
            coastline_df[self.channel_names[idx] + '_coastline'] = [coastline]
        return coastline_df

    def welch_analysis(self):
        welch_df = pd.DataFrame()
        for idx, channel_data in enumerate(self.data):
            logging.debug(f'Calculating Welch analysis for channel {self.channel_names[idx]}')
            frequencies, power_spectral_density = welch(channel_data, fs=self.sf)
            power_spectral_density /= np.sum(power_spectral_density)
            welch_df['frequency'] = frequencies
            welch_df[self.channel_names[idx] + '_power'] = power_spectral_density
        return welch_df
