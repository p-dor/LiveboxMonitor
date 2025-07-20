### Livebox Monitor Call API dialog ###

import json

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import call_api_label as lx


# ################################ IPv6 dialog ################################
class CallApiDialog(QtWidgets.QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.resize(650, 900)
        self._app = parent
        self._session = session

        # Package/Module box
        package_label = QtWidgets.QLabel(lx("Package:"), objectName="packageLabel")
        self._package = QtWidgets.QLineEdit(objectName="package")
        module_label = QtWidgets.QLabel(lx("Service:"), objectName="moduleLabel")
        self._module = QtWidgets.QLineEdit(objectName="module")
        pmbox = QtWidgets.QHBoxLayout()
        pmbox.addWidget(package_label, 0)
        pmbox.addWidget(self._package, 1)
        pmbox.addWidget(module_label, 0)
        pmbox.addWidget(self._module, 1)

        # Parameters
        parameters_label = QtWidgets.QLabel(lx("Parameters (JSON):"), objectName="parametersLabel")
        self._parameters = QtWidgets.QTextEdit(objectName="parametersEdit")
        text_doc = QtGui.QTextDocument("{}")
        font = QtGui.QFont("Courier New", 9)
        text_doc.setDefaultFont(font)
        self._parameters.setDocument(text_doc)

        # Call button
        call_button = QtWidgets.QPushButton(lx("Call"), objectName="call")
        call_button.clicked.connect(self.call)

        # Reply
        self._reply = QtWidgets.QTextEdit(objectName="replyEdit")

        # Button bar
        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx("OK"), objectName="ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(pmbox, 0)
        vbox.addWidget(parameters_label, 0)
        vbox.addWidget(self._parameters, 1)
        vbox.addWidget(call_button, 1)
        vbox.addWidget(self._reply, 1)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, "callapi")

        self.setWindowTitle(lx("Call APIs"))
        self.setModal(True)
        self.show()


    def call(self):
        # Get package name
        package = self._package.text().strip()
        if not package:
            self.set_reply("You must specify a package name.")
            return

        # Get module name
        module = self._module.text().strip()

        # Get parameters
        args_text = self._parameters.toPlainText().strip()
        args = None
        if args_text:
            try:
                args = json.loads(args_text)
            except Exception as e:
                self.set_reply("Parameters are not valid JSON.")
                return

        # Trigger the call
        self.set_reply("")
        self._app._task.start()
        try:
            d = self._session.request(package, module or None, args or None, timeout=30)
        except Exception as e:
            self.set_reply(str(e))
            return
        finally:
             self._app._task.end()

        # Display the reply
        try:
            reply = json.dumps(d, indent=2)
        except Exception as e:
            reply = f"Bad JSON: {d}."
        self.set_reply(reply)


    def set_reply(self, text):
        text_doc = QtGui.QTextDocument(text)
        font = QtGui.QFont("Courier New", 9)
        text_doc.setDefaultFont(font)
        self._reply.setDocument(text_doc)
