import sys
import logging

# Configure logging to suppress debug messages
logging.basicConfig(level=logging.WARNING)

logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('numba.core').setLevel(logging.WARNING)

from PyQt6 import QtWidgets
from eeg_analyzer import EEGAnalyzer

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = EEGAnalyzer()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
