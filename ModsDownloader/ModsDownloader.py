from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys

from ui.main_form import MainForm
from browser.browser_grapper import start_server

app = QtWidgets.QApplication(sys.argv)

window = MainForm()

app.exec()
