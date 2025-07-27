### Livebox Monitor Call API dialog ###

import json

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import call_api_label as lx


# ################################ VARS & DEFS ################################

# Preset calls
PRESET_CALLS = {
    "Device Information":
        {"Pack": "DeviceInfo",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": True},

    "Livebox Configuration":
        {"Pack": "Devices.Device.[MAC]",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Device Model":
        {"Pack": "UPnP-IGD",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Interface List":
        {"Pack": "HomeLan.Interface",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Interface Keys":
        {"Pack": "NeMo.Intf.lo",
         "Serv": "getIntfs",
         "Parm": '{"traverse": "all"}',
         "Lbox": True , "Wrep": False},

    "Device List":
        {"Pack": "Devices",
         "Serv": "get",
         "Parm": '{"expression": "physical and !self and !voice"}',
         "Lbox": True , "Wrep": False},

    "Device Topology":
        {"Pack": "TopologyDiagnostics",
         "Serv": "buildTopology",
         "Parm": '{"SendXmlFile": "false"}',
         "Lbox": True , "Wrep": False},

    "Wifi Status":
        {"Pack": "NMC.Wifi",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": True},

    "Guest Wifi Status":
        {"Pack": "NMC.Guest",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Wifi Scheduler":
        {"Pack": "Scheduler",
         "Serv": "getCompleteSchedules",
         "Parm": '{"type": "WLAN"}',
         "Lbox": True , "Wrep": True},

    "Power Management Profiles":
        {"Pack": "PowerManagement",
         "Serv": "getProfiles",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Memory Status":
        {"Pack": "DeviceInfo.MemoryStatus",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Time":
        {"Pack": "Time",
         "Serv": "getTime",
         "Parm": "{}",
         "Lbox": True , "Wrep": True},

    "WAN Status":
        {"Pack": "NMC",
         "Serv": "getWANStatus",
         "Parm": "{}",
         "Lbox": True , "Wrep": True},

    "Connection Status":
        {"Pack": "NMC",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Uplink Information":
        {"Pack": "UplinkMonitor.DefaultGateway",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": True},

    "MTU":
        {"Pack": "NeMo.Intf.data",
         "Serv": "getFirstParameter",
         "Parm": '{"name": "MTU"}',
         "Lbox": True , "Wrep": True},

    "IPv6 Status":
        {"Pack": "NMC.IPv6",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "IPv6 Mode":
        {"Pack": "NMC.Autodetect",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "CGNat Status":
        {"Pack": "NMC.ServiceEligibility.DSLITE",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "DHCP Setup":
        {"Pack": "NMC",
         "Serv": "getLANIP",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "DHCP MIBs":
        {"Pack": "NeMo.Intf.data",
         "Serv": "getMIBs",
         "Parm": '{"mibs": "dhcp dhcpv6"}',
         "Lbox": True , "Wrep": False},

    "Ethernet MIBs":
        {"Pack": "NeMo.Intf.lan",
         "Serv": "getMIBs",
         "Parm": '{"mibs": "base eth"}',
         "Lbox": True , "Wrep": True},

    "Wifi MIBs":
        {"Pack": "NeMo.Intf.lan",
         "Serv": "getMIBs",
         "Parm": '{"mibs": "base wlanradio wlanvap"}',
         "Lbox": True , "Wrep": True},

    "Guest Wifi MIBs":
        {"Pack": "NeMo.Intf.guest",
         "Serv": "getMIBs",
         "Parm": '{"mibs": "base wlanradio wlanvap"}',
         "Lbox": True , "Wrep": False},

    "Reboot Information":
        {"Pack": "NMC.Reboot",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": True},

    "Reboot History":
        {"Pack": "NMC.Reboot.Reboot",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": True},

    "Backup Status":
        {"Pack": "NMC.NetworkConfig",
         "Serv": "get",
         "Parm": "{}",
         "Lbox": True , "Wrep": False},

    "Start Backup":
        {"Pack": "NMC.NetworkConfig",
         "Serv": "launchNetworkBackup",
         "Parm": '{"delay" : True}',
         "Lbox": True , "Wrep": False}
}


# ################################ IPv6 dialog ################################
class CallApiDialog(QtWidgets.QDialog):
    def __init__(self, api_registry, parent=None):
        super().__init__(parent)
        self.resize(650, 900)
        self._app = parent
        self._api = api_registry

        # Preset combo
        preset_label = QtWidgets.QLabel(lx("Preset"), objectName="presetLabel")
        self._preset_combo = QtWidgets.QComboBox(objectName="presetCombo")
        self.load_presets()
        self._preset_combo.activated.connect(self.preset_selected)

        # Package/Service box
        package_label = QtWidgets.QLabel(lx("Package"), objectName="packageLabel")
        self._package = QtWidgets.QLineEdit(objectName="package")
        service_label = QtWidgets.QLabel(lx("Service"), objectName="serviceLabel")
        self._service = QtWidgets.QLineEdit(objectName="service")

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(preset_label, 0, 0)
        grid.addWidget(self._preset_combo, 0, 1, 1, 3)
        grid.addWidget(package_label, 1, 0)
        grid.addWidget(self._package, 1, 1)
        grid.addWidget(service_label, 1, 2)
        grid.addWidget(self._service, 1, 3)

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
        vbox.addLayout(grid, 0)
        vbox.addWidget(parameters_label, 0)
        vbox.addWidget(self._parameters, 1)
        vbox.addWidget(call_button, 1)
        vbox.addWidget(self._reply, 1)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, "callapi")

        self.setWindowTitle(lx("Call APIs"))
        self.setModal(True)
        self.show()


    def load_presets(self):
        key = "Wrep" if self._api._is_repeater else "Lbox"
        preset_items = [p for p in PRESET_CALLS if PRESET_CALLS[p][key]]
        self._preset_combo.addItems(preset_items)
        self._preset_combo.setCurrentIndex(-1)


    def preset_selected(self, index):
        preset = self._preset_combo.currentText()
        entry = PRESET_CALLS.get(preset)
        if entry:
            mac = self._api._info.get_mac()
            self._package.setText(entry["Pack"].replace('[MAC]', mac))
            self._service.setText(entry["Serv"])
            self.set_parameters(entry["Parm"].replace('[MAC]', mac))


    def call(self):
        # Get package name
        package = self._package.text().strip()
        if not package:
            self.set_reply("You must specify a package name.")
            return

        # Get service name
        service = self._service.text().strip()

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
            d = self._api._session.request(package, service or None, args or None, timeout=30)
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


    def set_parameters(self, text):
        self.set_document_field(self._parameters, text)


    def set_reply(self, text):
        self.set_document_field(self._reply, text)


    def set_document_field(self, field, text):
        text_doc = QtGui.QTextDocument(text)
        font = QtGui.QFont("Courier New", 9)
        text_doc.setDefaultFont(font)
        field.setDocument(text_doc)
