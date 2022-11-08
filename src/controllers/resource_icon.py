import os
from PyQt6.QtCore import QDir
pyqt_version = "pyqt6"

CURRENT_DIRECTORY = os.path.abspath(os.getcwd())
QDir.addSearchPath("icons", CURRENT_DIRECTORY + "/models/moilutils/icons")
