import json
import re
from os import PathLike
from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtWebChannel, QtWebSockets, QtWebEngine, QtWebEngineWidgets
from PyQt5.QtCore import QUrl, pyqtSignal, pyqtSlot

from browser.browser_grapper import start_server, stop_server, connect_server


class MainForm(QtWidgets.QMainWindow):
    """description of class"""

    #grapping_complete = pyqtSignal(list)
    inner_mc_inside_pages: list[str] = []

    def __init__(self):
        super(MainForm,
              self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi("ui\\MainWindow.ui", self)  # Load the .ui file
        self.show()  # Show the GUI

        self.pushButtonGetFromBrowser.released.connect(
            self.get_from_browser_button_clicked)

        #QtWidgets.QListWidget.currentItemChanged
        self.listWidgetMods.currentItemChanged.connect(
            self.mods_listwidget_item_change)

        #self.mainWebView.setEnabled(False)
        self.toolButtonChangeDownloadPath.released.connect(
            self.open_file_dialog)

    def get_from_browser_button_clicked(self):
        start_server()
        connect_server(self.stop_server_polling)
        self.pushButtonGetFromBrowser.setEnabled(False)

    def stop_server_polling(self, returned_list: list[str]):
        self.inner_mc_inside_pages = returned_list
        stop_server()
        self.pushButtonGetFromBrowser.setEnabled(True)
        self.add_tabs_in_listwidget()

    def add_tabs_in_listwidget(self):
        #QtWidgets.QListWidget.addItem()
        mods_set: set = set(self.inner_mc_inside_pages)
        for item in mods_set:
            if item.startswith("https://minecraft-inside.ru/mods"
                               ) and item.endswith(".html"):
                self.listWidgetMods.addItem(item)

    def mods_listwidget_item_change(self, item: QtWidgets.QListWidgetItem):
        #QtWebEngineWidgets.QWebEngineView.setUrl
        self.mainWebView.loadFinished.connect(self.get_html_from_site)
        self.mainWebView.setUrl(QUrl(item.text()))

    def change_download_path(self, path: str | PathLike):
        self.lineEditModsDownloadPath.setText(path)

    def open_file_dialog(self):
        fileName = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Open Directory", "")
        self.change_download_path(fileName)

    def get_html_from_site(self, ok: bool):
        self.mainWebView.loadFinished.disconnect(self.get_html_from_site)

        if not ok:
            return

        self.mainWebView.page().runJavaScript(
            """const links = document.getElementsByClassName('dl__link')
            const names = document.getElementsByClassName('dl__name')
            let result = "[";
            for (let i = 0; i < links.length; i++) {
              result += ('{\"' + names[i].innerHTML + '\":\"' + links[i].innerHTML + '\"}');
              if ((i + 1 < links.length)) {
                result += ",";
              }
            }
            result += "]"
        """, self.callback_function)

    def callback_function(self, html):
        regex = re.compile(r"\d+(\.\d+)*|\bfabric\b|\bquilt\b")
        res: list = json.loads(html)
        for item in res:
            for key in item.keys():
                mat = re.findall(regex, key)
                new_key = str(mat[0])
                item[new_key] = item.pop(str(key))
                if len(mat) > 1:
                    index = 1
                    if mat[index] == "fabric" or mat[index] == "forge":
                        item["loader"] = mat[index]
                    else:
                        item[mat[index]] = item[new_key]
                break

        #QtWidgets.QComboBox.addItem
        for item in res:
            for key in item.keys():
                self.comboBoxVersion.addItem(key)