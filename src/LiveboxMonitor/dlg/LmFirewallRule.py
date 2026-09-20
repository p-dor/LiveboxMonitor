### Livebox Monitor Firewall rule dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmQtTools, LmConfig, LmFwlTools
from LiveboxMonitor.lang.LmLanguages import get_firewall_rule_label as lx, get_firewall_message as mx
from LiveboxMonitor.tools import LmTools

from enum import IntEnum


# ################################ VARS & DEFS ################################

# Direction indexes
class Dir(IntEnum):
    Inbound = 0
    Outbound = 1

# Actions
ACTIONS = ["Accept", "Reject", "Drop"]

# Action indexes
class Action(IntEnum):
    Accept = 0
    Reject = 1
    Drop = 2


# ################################ Firewall rule dialog ################################
class FirewallRuleDialog(QtWidgets.QDialog):
    def __init__(self, rule=None, parent=None):
        super().__init__(parent)
        self.resize(390, 480)

        self._app = parent
        self._ignore_signal = False

        self._enable_checkbox = QtWidgets.QCheckBox(lx("Enabled"), objectName="enableCheckbox")

        type_label = QtWidgets.QLabel(lx("Type"), objectName="typeLabel")
        self._type_combo = QtWidgets.QComboBox(objectName="typeCombo")
        self._type_combo.addItems(LmFwlTools.RULE_FWL_TYPES)
        self._type_combo.activated.connect(self.type_selected)

        direction_label = QtWidgets.QLabel(lx("Direction"), objectName="directionLabel")
        self._direction_combo = QtWidgets.QComboBox(objectName="directionCombo")
        self._direction_combo.addItem(lx("Inbound"))
        self._direction_combo.addItem(lx("Outbound"))
        self._direction_combo.activated.connect(self.direction_selected)

        name_label = QtWidgets.QLabel(lx("Name"), objectName="nameLabel")
        self._name_edit = QtWidgets.QLineEdit(objectName="nameEdit")
        self._name_edit.textChanged.connect(self.name_typed)

        desc_label = QtWidgets.QLabel(lx("Description"), objectName="descLabel")
        self._desc_edit = LmQtTools.MultiLinesEdit(objectName="descEdit")
        self._desc_edit.setTabChangesFocus(True)
        self._desc_edit.setLineNumber(2)

        protocols_label = QtWidgets.QLabel(lx("Protocols"), objectName="protocolsLabel")
        self._protocols_combo = LmQtTools.CheckableComboBox(objectName="protocolsCombo")
        self._protocols_combo.setPlaceholderText(lx("Protocols"))
        self._protocols_combo.currentTextChanged.connect(self.protocols_click)

        device_label = QtWidgets.QLabel(lx("Device"), objectName="deviceLabel")
        self._device_combo = QtWidgets.QComboBox(objectName="deviceCombo")
        self._device_combo.activated.connect(self.device_selected)

        source_ip_label = QtWidgets.QLabel(lx("Source IP Address"), objectName="sourceIpLabel")
        self._source_ip_edit = QtWidgets.QLineEdit(objectName="sourceIpEdit")
        self._source_ip_edit.textChanged.connect(self.ip_typed)

        port_regexp = QtCore.QRegularExpression(LmTools.PORT_LIST_RS)
        port_validator = QtGui.QRegularExpressionValidator(port_regexp)

        source_port_label = QtWidgets.QLabel(lx("Source Port"), objectName="sourcePortLabel")
        self._source_port_edit = QtWidgets.QLineEdit(objectName="sourcePortEdit")
        self._source_port_edit.setValidator(port_validator)

        dest_ip_label = QtWidgets.QLabel(lx("Dest IP Address"), objectName="destIpLabel")
        self._dest_ip_edit = QtWidgets.QLineEdit(objectName="destIpEdit")
        self._dest_ip_edit.textChanged.connect(self.ip_typed)

        dest_port_label = QtWidgets.QLabel(lx("Dest Port"), objectName="destPortLabel")
        self._dest_port_edit = QtWidgets.QLineEdit(objectName="destPortEdit")
        self._dest_port_edit.setValidator(port_validator)

        ation_label = QtWidgets.QLabel(lx("Action"), objectName="actionLabel")
        self._action_combo = QtWidgets.QComboBox(objectName="actionCombo")
        for a in ACTIONS:
            self._action_combo.addItem(lx(a))

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self._enable_checkbox, 0, 0)
        grid.addWidget(type_label, 1, 0)
        grid.addWidget(self._type_combo, 1, 1)
        grid.addWidget(direction_label, 1, 2, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self._direction_combo, 1, 3)
        grid.addWidget(name_label, 2, 0)
        grid.addWidget(self._name_edit, 2, 1, 1, 3)
        grid.addWidget(desc_label, 3, 0)
        grid.addWidget(self._desc_edit, 3, 1, 1, 3)
        grid.addWidget(protocols_label, 4, 0)
        grid.addWidget(self._protocols_combo, 4, 1, 1, 3)
        grid.addWidget(device_label, 5, 0)
        grid.addWidget(self._device_combo, 5, 1, 1, 3)
        grid.addWidget(source_ip_label, 6, 0)
        grid.addWidget(self._source_ip_edit, 6, 1, 1, 3)
        grid.addWidget(source_port_label, 7, 0)
        grid.addWidget(self._source_port_edit, 7, 1, 1, 3)
        grid.addWidget(dest_ip_label, 8, 0)
        grid.addWidget(self._dest_ip_edit, 8, 1, 1, 3)
        grid.addWidget(dest_port_label, 9, 0)
        grid.addWidget(self._dest_port_edit, 9, 1, 1, 3)
        grid.addWidget(ation_label, 10, 0)
        grid.addWidget(self._action_combo, 10, 1, 1, 3)

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

        LmConfig.set_tooltips(self, "fwlrule")

        self.setWindowTitle(lx("Firewall Rule"))

        if rule:
            self.set_rule(rule)
        else:
            self.set_default()

        self._name_edit.setFocus()
        self.setModal(True)
        self.show()


    # Set default values, for rule creation
    def set_default(self):
        self._enable_checkbox.setChecked(True)
        i = LmFwlTools.RULE_FWL_TYPES.index(LmFwlTools.RULE_TYPE_IPv4)
        # Set the direction before the type as type can force direction
        self._current_direction = Dir.Outbound
        self._direction_combo.setCurrentIndex(self._current_direction)
        self.direction_selected(self._current_direction)
        self._type_combo.setCurrentIndex(i)
        self.type_selected(i)
        self._name_edit.setText("")
        self._desc_edit.setPlainText("")
        self.load_protocols_combo("TCP")
        self._device_combo.setCurrentIndex(0)
        self._source_ip_edit.setText("")
        self._source_port_edit.setText("1000")
        self._dest_ip_edit.setText("")
        self._dest_port_edit.setText("1000")
        self._action_combo.setCurrentIndex(Action.Accept)
        self.set_ok_button_state()


    # Set values to existing rule, for edition
    def set_rule(self, rule):
        self._enable_checkbox.setChecked(rule["Enable"])

        # Set the direction before the type as type can force direction
        self._current_direction = Dir.Outbound if rule["Outbound"] else Dir.Inbound
        self._direction_combo.setCurrentIndex(self._current_direction)
        self.direction_selected(self._current_direction)

        i = LmFwlTools.RULE_FWL_TYPES.index(rule["Type"])
        self._type_combo.setCurrentIndex(i)
        self.type_selected(i)

        self._name_edit.setText(rule["Name"])
        self._desc_edit.setPlainText(rule["Desc"])

        self.load_protocols_combo(rule["ProtoNames"])

        ip = rule["SourceIP"]
        self._source_ip_edit.setText(ip)
        self._source_port_edit.setText(rule["SourcePort"])
        ip = rule["DestIP"]
        self._dest_ip_edit.setText(ip)
        self._dest_port_edit.setText(rule["DestPort"])
        self.ip_typed(ip)

        self._action_combo.setCurrentIndex(ACTIONS.index(rule["Action"]))

        self.set_ok_button_state()


    def load_protocols_combo(self, protocols):
        protocol_numbers, protocol_names = zip(*LmFwlTools.PROTOCOL_NAMES.items())
        self._protocols_combo.addItems(protocol_names, protocol_numbers)
        self._protocols_combo.setSelection(protocols.split("/"))


    def get_rule(self):
        p = self.get_protocols()
        return {
            "Enable": self.get_enabled(),
            "Type": self.get_type(),
            "Outbound": self.get_outbound(),
            "Name": self.get_name(),
            "Desc": self.get_description(),
            "ProtoNames": p,
            "ProtoNumbers": self._app.translate_firewall_protocols(p),
            "SourceIP": self.get_source_ip(),
            "SourcePort": self.get_source_port(),
            "DestIP": self.get_dest_ip(),
            "DestPort": self.get_dest_port(),
            "Action": self.get_action()
        }


    def type_selected(self, index):
        # Load corresponding devices
        self.load_device_list()

        # Adjust IP field validator & direction
        if self.get_type() == LmFwlTools.RULE_TYPE_IPv6:
            ip_reg_exp = QtCore.QRegularExpression(f"^{LmTools.IPv6Pfix_RS}$")
            self._direction_combo.setEnabled(True)
        else:
            ip_reg_exp = QtCore.QRegularExpression(f"^{LmTools.IPv4Pfix_RS}$")
            self._direction_combo.setCurrentIndex(Dir.Outbound)
            self.direction_selected(Dir.Outbound)
            self._direction_combo.setEnabled(False)

        ip_validator = QtGui.QRegularExpressionValidator(ip_reg_exp)
        self._source_ip_edit.setText("")
        self._source_ip_edit.setValidator(ip_validator)
        self._dest_ip_edit.setText("")
        self._dest_ip_edit.setValidator(ip_validator)


    def direction_selected(self, index):
        if index != self._current_direction:
            # If direction changes swap sources and destinations
            self._ignore_signal = True
            source_ip = self._source_ip_edit.text()
            source_port = self._source_port_edit.text()
            dest_ip = self._dest_ip_edit.text()
            dest_port = self._dest_port_edit.text()
            self._source_ip_edit.setText(dest_ip)
            self._source_port_edit.setText(dest_port)
            self._dest_ip_edit.setText(source_ip)
            self._dest_port_edit.setText(source_port)
            self._ignore_signal = False
            self._current_direction = index


    def name_typed(self, text):
        self.set_ok_button_state()


    def protocols_click(self, current_text):
        self.set_ok_button_state()


    def device_selected(self, index):
        if not self._ignore_signal:
            self._ignore_signal = True
            if self.get_outbound():
                self._source_ip_edit.setText(self._device_combo.currentData())
            else:
                self._dest_ip_edit.setText(self._device_combo.currentData())
            self._ignore_signal = False


    def ip_typed(self, text):
        if not self._ignore_signal:
            self._ignore_signal = True
            self.select_device_from_ip()
            self._ignore_signal = False

        self.set_ok_button_state()


    def set_ok_button_state(self):
        self._ok_button.setDisabled((len(self.get_name()) == 0) or
                                    (len(self.get_protocols()) == 0))


    def load_device_list(self):
        t = self.get_type()
        device_map = self._app._device_ip_name_map
        self._device_combo.clear()

        # Load matching devices / IPs
        for i in device_map:
            if device_map[i]["IPVers"] == t:
                self._device_combo.addItem(self._app.get_device_name_from_ip(i), userData=i)

        # Sort by name
        self._device_combo.model().sort(0)

        # Insert unknown device at the beginning
        self._device_combo.insertItem(0, lx("-Unknown-"), userData="")
        self._device_combo.setCurrentIndex(0)
        self.device_selected(0)


    def select_device_from_ip(self):
        ip = self.get_source_ip() if self.get_outbound() else self.get_dest_ip()
        i = self._device_combo.findData(ip.split('/')[0])     # split() to convert potential CIDR notation into IP addr
        if i < 0:
            i = 0
        self._device_combo.setCurrentIndex(i)


    def accept(self):
        # Validate IP addresses
        if not self.validate_ip(self._source_ip_edit) or not self.validate_ip(self._dest_ip_edit):
            return

        super().accept()


    def validate_ip(self, item):
        t = self.get_type()

        ip = item.text()
        if ip:
            if t == LmFwlTools.RULE_TYPE_IPv6:
                if not LmTools.is_ipv6_pfix(ip):
                    self._app.display_error(mx("{} is not a valid IPv6 address.", "ipv6AddrErr").format(ip))
                    item.setFocus()
                    return False
            else:
                if not LmTools.is_ipv4_pfix(ip):
                    self._app.display_error(mx("{} is not a valid IPv4 address.", "ipv4AddrErr").format(ip))
                    item.setFocus()
                    return False

        return True


    def get_enabled(self):
        return self._enable_checkbox.isChecked()


    def get_type(self):
        return self._type_combo.currentText()


    def get_outbound(self):
        return self._direction_combo.currentIndex() == Dir.Outbound
 

    def get_name(self):
        return self._name_edit.text()


    def get_description(self):
        return self._desc_edit.toPlainText()


    def get_protocols(self):
        return "/".join(self._protocols_combo.currentSelection())


    def get_source_ip(self):
        return self._source_ip_edit.text()


    def get_source_port(self):
        return self._source_port_edit.text()


    def get_dest_ip(self):
        return self._dest_ip_edit.text()


    def get_dest_port(self):
        return self._dest_port_edit.text()


    def get_action(self):
        return ACTIONS[self._action_combo.currentIndex()]
