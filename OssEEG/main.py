import sys
from PyQt6 import QtWidgets
from eeg_analyzer import EEGAnalyzer

import logging

logging.basicConfig(level=logging.WARNING)
def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = EEGAnalyzer()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
