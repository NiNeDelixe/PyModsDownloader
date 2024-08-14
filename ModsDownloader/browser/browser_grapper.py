from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import threading
from werkzeug.serving import make_server
from flask import Flask, render_template, render_template_string, request, jsonify
import json


class ServerThread(threading.Thread, QtCore.QObject):
    returned_text = pyqtSignal(list)

    def __init__(self, app: Flask):
        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()
        self.app = app

        @app.route("/", methods=["GET", "POST"])
        def index():
            if request.method == "GET":
                return render_template("index.html")
            elif request.method == "POST":
                mc_inside_pages: list[str] = []
                try:
                    data = json.loads(request.data)
                    if "tabs" in data:
                        value = self._validate(data["tabs"])
                        for x in value:
                            if x["url"].startswith(
                                    "https://minecraft-inside.ru/mods"):
                                mc_inside_pages.append(x["url"])
                        self.returned_text.emit(mc_inside_pages)
                        return jsonify({"message": "Success!"}), 200
                    else:
                        raise KeyError("Value key not found")
                except (KeyError, json.JSONDecodeError) as e:
                    return jsonify({"error": "Invalid data format"}), 400

    def _validate(self, value):
        return value

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()


def start_server():
    global server

    app = Flask(__name__, template_folder="template")

    server = ServerThread(app)
    server.start()


def stop_server():
    global server
    server.shutdown()


def connect_server(slot):
    global server
    server.returned_text.connect(slot)