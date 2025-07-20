### Livebox Monitor Add DHCP binding dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang.LmLanguages import get_dhcp_binding_label as lx


# ################################ Add DHCP binding setup dialog ################################
class AddDhcpBindingDialog(QtWidgets.QDialog):
    def __init__(self, home_ip_suggest, guest_ip_suggest, parent=None):
        super().__init__(parent)
        self.resize(350, 180)

        self._home_ip_suggest = home_ip_suggest
        self._guest_ip_suggest = guest_ip_suggest
        self._ignore_signal = False

        device_label = QtWidgets.QLabel(lx("Device"), objectName="deviceLabel")
        self._device_combo = QtWidgets.QComboBox(objectName="deviceCombo")
        self.load_device_list()
        for d in self._combo_device_list:
            self._device_combo.addItem(d["Name"])
        self._device_combo.activated.connect(self.device_selected)

        mac_label = QtWidgets.QLabel(lx("MAC address"), objectName="macLabel")
        self._mac_edit = QtWidgets.QLineEdit(objectName="macEdit")
        mac_reg_exp = QtCore.QRegularExpression("^" + LmTools.MAC_RS + "$")
        mac_validator = QtGui.QRegularExpressionValidator(mac_reg_exp)
        self._mac_edit.setValidator(mac_validator)
        self._mac_edit.textChanged.connect(self.mac_typed)

        domain_label = QtWidgets.QLabel(lx("Domain"), objectName="domainLabel")
        self._domain_combo = QtWidgets.QComboBox(objectName="domainCombo")
        self._domain_combo.addItems(["Home", "Guest"])
        self._domain_combo.activated.connect(self.domain_selected)

        ip_label = QtWidgets.QLabel(lx("IP address"), objectName="ipLabel")
        self._ip_edit = QtWidgets.QLineEdit(objectName="ipEdit")
        ip_reg_exp = QtCore.QRegularExpression("^" + LmTools.IPv4_RS + "$")
        ip_validator = QtGui.QRegularExpressionValidator(ip_reg_exp)
        self._ip_edit.setValidator(ip_validator)
        self._ip_edit.textChanged.connect(self.ip_typed)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(device_label, 0, 0)
        grid.addWidget(self._device_combo, 0, 1)
        grid.addWidget(mac_label, 1, 0)
        grid.addWidget(self._mac_edit, 1, 1)
        grid.addWidget(domain_label, 2, 0)
        grid.addWidget(self._domain_combo, 2, 1)
        grid.addWidget(ip_label, 3, 0)
        grid.addWidget(self._ip_edit, 3, 1)

        self._ok_button = QtWidgets.QPushButton(lx("OK"), objectName="ok")
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx("Cancel"), objectName="cancel")
        cancel_button.clicked.connect(self.reject)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.setSpacing(10)
        hbox.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(grid, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, "dbinding")

        self.setWindowTitle(lx("Add DHCP binding"))
        self.suggest_ip()
        self.set_ok_button_state()
        self.setModal(True)
        self.show()


    def load_device_list(self):
        self._deviceList = self.parent().get_device_list()
        self._combo_device_list = []

        # Load from MacAddrTable file
        for d in LmConf.MacAddrTable:
            device = {
                "Name": LmConf.MacAddrTable[d],
                "MAC": d
            }
            self._combo_device_list.append(device)

        # Load from device list if not already loaded
        for d in self._deviceList:
            if (len(d["MAC"])) and (not any(e["MAC"] == d["MAC"] for e in self._combo_device_list)):
                device = {
                    "Name": d["LBName"],
                    "MAC": d["MAC"]
                }
                self._combo_device_list.append(device)

        # Sort by name
        self._combo_device_list = sorted(self._combo_device_list, key = lambda x: x["Name"])

        # Insert unknown device at the beginning
        device = {
            "Name": lx("-Unknown-"),
            "MAC": ""
        }
        self._combo_device_list.insert(0, device)


    def device_selected(self, index):
        if not self._ignore_signal:
            self._ignore_signal = True
            self._mac_edit.setText(self._combo_device_list[index]["MAC"])
            self._ignore_signal = False
            self.suggest_ip()


    def domain_selected(self, index):
        self.suggest_ip()


    def mac_typed(self, mac):
        if not self._ignore_signal:
            self._ignore_signal = True

            # Find index of device with matching MAC, default to 0 if not found
            index = next((i for i, d in enumerate(self._combo_device_list) if d["MAC"] == mac), 0)
            self._device_combo.setCurrentIndex(index)
            if index:
                self.suggest_ip()
            self._ignore_signal = False
        self.set_ok_button_state()


    def ip_typed(self, iIp):
        self.set_ok_button_state()


    def suggest_ip(self):
        domain = self.get_domain()

        # Search if MAC corresponds to an active IP
        ip = None
        mac = self.get_mac_address()
        if mac:
            device = next((d for d in self._deviceList if (d["MAC"] == mac) and d["Active"]), None)
            if device:
                ip = device["IP"]

        # Check if IP is in the domain network
        if ip is not None:
            if not self.parent().is_ip_in_network(ip, domain):
                ip = None

        # If no IP found, suggest the next available one
        if ip is None:
            if domain == "Home":
                ip = self._home_ip_suggest
            else:
                ip = self._guest_ip_suggest

        self._ip_edit.setText(ip)


    def set_ok_button_state(self):
        self._ok_button.setDisabled((len(self.get_mac_address()) == 0) or (len(self.get_ip_address()) == 0))


    def get_mac_address(self):
        return self._mac_edit.text()


    def get_domain(self):
        return self._domain_combo.currentText()


    def get_ip_address(self):
        return self._ip_edit.text()
