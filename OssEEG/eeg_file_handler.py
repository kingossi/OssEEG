import os
import mne


class EEGFileHandler:
    def __init__(self):
        self.raw = None
        self.data = None

    def load_file(self, file_name):
        if file_name.endswith('.fif'):
            self.raw = mne.io.read_raw_fif(file_name, preload=True)
        elif file_name.endswith('.eeg'):
            hdr_file = file_name.replace('.eeg', '.vhdr')
            if not os.path.exists(hdr_file):
                raise FileNotFoundError(f"Header file not found: {hdr_file}")
            self.raw = mne.io.read_raw_brainvision(hdr_file, preload=True)
        elif file_name.endswith('.edf'):
            self.raw = mne.io.read_raw_edf(file_name, preload=True)
        else:
            raise ValueError('Unsupported file format')

        self.raw.pick_types(meg=False, eeg=True)
        self.data = self.raw.get_data()  # Get data for all channels
        return self.raw, self.data

