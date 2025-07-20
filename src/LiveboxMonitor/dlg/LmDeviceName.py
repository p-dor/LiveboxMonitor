### Livebox Monitor device name dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import get_device_name_label as lx


# ################################ Set device name dialog ################################
class SetDeviceNameDialog(QtWidgets.QDialog):
    def __init__(self, device_key, name, livebox_name, dns_name, parent=None):
        super().__init__(parent)
        self.resize(350, 200)

        label = QtWidgets.QLabel(lx("Names for [{}] device:").format(device_key), objectName="mainLabel")

        self._name_checkbox = QtWidgets.QCheckBox(lx("Local Name"), objectName="nameCheckBox")
        self._name_checkbox.clicked.connect(self.name_click)
        self._name_edit = QtWidgets.QLineEdit(objectName="nameEdit")
        if name is None:
            self._name_checkbox.setChecked(False)
            self._name_edit.setDisabled(True)
            self._current_name = ""
        else:
            self._name_checkbox.setChecked(True)
            self._current_name = name
            self._name_edit.setText(self._current_name)

        self._livebox_name_checkbox = QtWidgets.QCheckBox(lx("Livebox Name"), objectName="liveboxNameCheckBox")
        self._livebox_name_checkbox.clicked.connect(self.livebox_name_click)
        self._livebox_name_edit = QtWidgets.QLineEdit(objectName="liveboxNameEdit")
        if livebox_name is None:
            self._livebox_name_checkbox.setChecked(False)
            self._livebox_name_edit.setDisabled(True)
            self._current_livebox_name = ""
        else:
            self._livebox_name_checkbox.setChecked(True)
            self._current_livebox_name = livebox_name
            self._livebox_name_edit.setText(self._current_livebox_name)

        self._dns_name_checkbox = QtWidgets.QCheckBox(lx("DNS Name"), objectName="dnsNameCheckBox")
        self._dns_name_checkbox.clicked.connect(self.dns_name_click)
        self._dns_name_edit = QtWidgets.QLineEdit(objectName="dnsNameEdit")
        if dns_name is None:
            self._dns_name_checkbox.setChecked(False)
            self._dns_name_edit.setDisabled(True)
            self._current_dns_name = ""
        else:
            self._dns_name_checkbox.setChecked(True)
            self._current_dns_name = dns_name
            self._dns_name_edit.setText(self._current_dns_name)

        name_grid = QtWidgets.QGridLayout()
        name_grid.setSpacing(10)
        name_grid.addWidget(self._name_checkbox, 0, 0)
        name_grid.addWidget(self._name_edit, 0, 1)
        name_grid.addWidget(self._livebox_name_checkbox, 1, 0)
        name_grid.addWidget(self._livebox_name_edit, 1, 1)
        name_grid.addWidget(self._dns_name_checkbox, 2, 0)
        name_grid.addWidget(self._dns_name_edit, 2, 1)

        ok_button = QtWidgets.QPushButton(lx("OK"), objectName="ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx("Cancel"), objectName="cancel")
        cancel_button.clicked.connect(self.reject)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.setSpacing(10)
        hbox.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(20)
        vbox.addWidget(label, 0)
        vbox.addLayout(name_grid, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, "dname")

        self.setWindowTitle(lx("Assign device names"))
        self.setModal(True)
        self.show()


    def name_click(self):
        if self._name_checkbox.isChecked():
            self._name_edit.setDisabled(False)
            self._name_edit.setText(self._current_name)
        else:
            self._name_edit.setDisabled(True)
            self._name_edit.setText("")


    def livebox_name_click(self):
        if self._livebox_name_checkbox.isChecked():
            self._livebox_name_edit.setDisabled(False)
            self._livebox_name_edit.setText(self._current_livebox_name)
        else:
            self._livebox_name_edit.setDisabled(True)
            self._livebox_name_edit.setText("")


    def dns_name_click(self):
        if self._dns_name_checkbox.isChecked():
            self._dns_name_edit.setDisabled(False)
            self._dns_name_edit.setText(self._current_dns_name)
        else:
            self._dns_name_edit.setDisabled(True)
            self._dns_name_edit.setText("")


    def get_name(self):
        if self._name_checkbox.isChecked():
            return self._name_edit.text()
        return None


    def get_livebox_name(self):
        if self._livebox_name_checkbox.isChecked():
            return self._livebox_name_edit.text()
        return None


    def get_dns_name(self):
        if self._dns_name_checkbox.isChecked():
            return self._dns_name_edit.text()
        return None
