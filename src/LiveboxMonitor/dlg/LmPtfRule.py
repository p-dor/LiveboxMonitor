### Livebox Monitor PTF rule dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig, LmPatPtf
from LiveboxMonitor.lang.LmLanguages import get_ptf_rule_label as lx, get_nat_pat_message as mx


# ################################ PTF rule dialog ################################
class PtfRuleDialog(QtWidgets.QDialog):
    def __init__(self, rule=None, parent=None):
        super(PtfRuleDialog, self).__init__(parent)
        self.resize(390, 380)

        self._ignore_signal = False

        self._enable_checkbox = QtWidgets.QCheckBox(lx('Enabled'), objectName='enableCheckbox')

        type_label = QtWidgets.QLabel(lx('Type'), objectName='typeLabel')
        self._type_combo = QtWidgets.QComboBox(objectName='typeCombo')
        self._type_combo.addItems(LmPatPtf.RULE_PTF_TYPES)
        self._type_combo.activated.connect(self.type_selected)

        name_label = QtWidgets.QLabel(lx('Name'), objectName='nameLabel')
        self._name_edit = QtWidgets.QLineEdit(objectName='nameEdit')
        self._name_edit.textChanged.connect(self.name_typed)

        desc_label = QtWidgets.QLabel(lx('Description'), objectName='descLabel')
        self._desc_edit = LmTools.MultiLinesEdit(objectName='descEdit')
        self._desc_edit.setTabChangesFocus(True)
        self._desc_edit.setLineNumber(2)

        protocols_label = QtWidgets.QLabel(lx('Protocols'), objectName='protocolsLabel')
        self._tcp_checkbox = QtWidgets.QCheckBox(lx('TCP'), objectName='tcpCheckbox')
        self._tcp_checkbox.clicked.connect(self.protocol_click)
        self._udp_checkbox = QtWidgets.QCheckBox(lx('UDP'), objectName='udpCheckbox')
        self._udp_checkbox.clicked.connect(self.protocol_click)
        self._ah_checkbox = QtWidgets.QCheckBox(lx('AH'), objectName='ahCheckbox')
        self._ah_checkbox.clicked.connect(self.protocol_click)
        self._gre_checkbox = QtWidgets.QCheckBox(lx('GRE'), objectName='greCheckbox')
        self._gre_checkbox.clicked.connect(self.protocol_click)
        self._esp_checkbox = QtWidgets.QCheckBox(lx('ESP'), objectName='espCheckbox')
        self._esp_checkbox.clicked.connect(self.protocol_click)
        self._icmp_checkbox = QtWidgets.QCheckBox(lx('ICMP'), objectName='icmpCheckbox')
        self._icmp_checkbox.clicked.connect(self.protocol_click)
        protocols_box = QtWidgets.QHBoxLayout()
        protocols_box.setSpacing(10)
        protocols_box.addWidget(self._tcp_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        protocols_box.addWidget(self._udp_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        protocols_box.addWidget(self._ah_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        protocols_box.addWidget(self._gre_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        protocols_box.addWidget(self._esp_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        protocols_box.addWidget(self._icmp_checkbox, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

        device_label = QtWidgets.QLabel(lx('Device'), objectName='deviceLabel')
        self._device_combo = QtWidgets.QComboBox(objectName='deviceCombo')
        self._device_combo.activated.connect(self.device_selected)

        ip_label = QtWidgets.QLabel(lx('IP Address'), objectName='ipLabel')
        self._ip_edit = QtWidgets.QLineEdit(objectName='ipEdit')
        self._ip_edit.textChanged.connect(self.ip_typed)

        ext_ips_label = QtWidgets.QLabel(lx('External IPs'), objectName='extIPsLabel')
        self._ext_ips_edit = LmTools.MultiLinesEdit(objectName='extIPsEdit')
        self._ext_ips_edit.setTabChangesFocus(True)
        self._ext_ips_edit.setLineNumber(2)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self._enable_checkbox, 0, 0)
        grid.addWidget(type_label, 1, 0)
        grid.addWidget(self._type_combo, 1, 1)
        grid.addWidget(name_label, 2, 0)
        grid.addWidget(self._name_edit, 2, 1)
        grid.addWidget(desc_label, 3, 0)
        grid.addWidget(self._desc_edit, 3, 1)
        grid.addWidget(protocols_label, 4, 0)
        grid.addLayout(protocols_box, 4, 1)
        grid.addWidget(device_label, 5, 0)
        grid.addWidget(self._device_combo, 5, 1)
        grid.addWidget(ip_label, 6, 0)
        grid.addWidget(self._ip_edit, 6, 1)
        grid.addWidget(ext_ips_label, 7, 0)
        grid.addWidget(self._ext_ips_edit, 7, 1)

        self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
        cancel_button.clicked.connect(self.reject)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.setSpacing(10)
        hbox.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(grid, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, 'ptfrule')

        self.setWindowTitle(lx('Protocol Forwarding Rule'))

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
        i = LmPatPtf.RULE_PTF_TYPES.index(LmPatPtf.RULE_TYPE_IPv4)
        self._type_combo.setCurrentIndex(i)
        self.type_selected(i)
        self._name_edit.setText('')
        self._desc_edit.setPlainText('')
        self._tcp_checkbox.setChecked(False)
        self._udp_checkbox.setChecked(False)
        self._ah_checkbox.setChecked(True)
        self._gre_checkbox.setChecked(False)
        self._esp_checkbox.setChecked(False)
        self._icmp_checkbox.setChecked(False)
        self._device_combo.setCurrentIndex(0)
        self._ip_edit.setText('')
        self._ext_ips_edit.setPlainText('')
        self.set_ok_button_state()


    # Set values to existing rule, for edition
    def set_rule(self, rule):
        self._enable_checkbox.setChecked(rule['Enable'])

        t = rule['Type']
        i = LmPatPtf.RULE_PTF_TYPES.index(t)
        self._type_combo.setCurrentIndex(i)
        self.type_selected(i)

        self._name_edit.setText(rule['Name'])
        self._desc_edit.setPlainText(rule['Desc'])

        p = rule['ProtoNames'].split('/')

        self._tcp_checkbox.setChecked(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.TCP.value)] in p)
        self._udp_checkbox.setChecked(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.UDP.value)] in p)
        self._ah_checkbox.setChecked(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.AH.value)] in p)
        self._gre_checkbox.setChecked(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.GRE.value)] in p)
        self._esp_checkbox.setChecked(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.ESP.value)] in p)

        if t == LmPatPtf.RULE_TYPE_IPv6:
            icmp = LmPatPtf.Protocols.ICMPv6.value
        else:
            icmp = LmPatPtf.Protocols.ICMP.value
        self._icmp_checkbox.setChecked(LmPatPtf.PROTOCOL_NAMES[str(icmp)] in p)

        ip = rule['IP']
        self._ip_edit.setText(ip)
        self.ip_typed(ip)

        self._ext_ips_edit.setPlainText(rule['ExtIPs'])

        self.set_ok_button_state()


    def get_rule(self):
        p = self.get_protocols()
        return {
            'Enable': self.get_enabled(),
            'Type': self.get_type(),
            'Name': self.get_name(),
            'Desc': self.get_description(),
            'ProtoNames': p,
            'ProtoNumbers': self.parent().translateNatPatProtocols(p),
            'IP': self.get_ip(),
            'ExtIPs': self.get_ext_ips()        
        }


    def type_selected(self, index):
        # Load corresponding devices
        self.load_device_list()

        # Adjust IP field validator
        if self.get_type() == LmPatPtf.RULE_TYPE_IPv6:
            ip_reg_exp = QtCore.QRegularExpression(f'^{LmTools.IPv6Pfix_RS}$')
        else:
            ip_reg_exp = QtCore.QRegularExpression(f'^{LmTools.IPv4_RS}$')
        self._ip_edit.setValidator(QtGui.QRegularExpressionValidator(ip_reg_exp))


    def name_typed(self, text):
        self.set_ok_button_state()


    def protocol_click(self):
        self.set_ok_button_state()


    def device_selected(self, index):
        if not self._ignore_signal:
            self._ignore_signal = True
            self._ip_edit.setText(self._device_combo.currentData())
            self._ignore_signal = False


    def ip_typed(self, text):
        if not self._ignore_signal:
            self._ignore_signal = True
            i = self._device_combo.findData(text)
            if i < 0:
                i = 0
            self._device_combo.setCurrentIndex(i)
            self._ignore_signal = False

        self.set_ok_button_state()


    def set_ok_button_state(self):
        self._ok_button.setDisabled((len(self.get_name()) == 0) or
                                    (len(self.get_ip()) == 0) or
                                    (len(self.get_protocols()) == 0))


    def load_device_list(self):
        t = self.get_type()
        device_map = self.parent()._device_ip_name_map
        self._device_combo.clear()

        # Load matching devices / IPs
        for i in device_map:
            if device_map[i]['IPVers'] == t:
                self._device_combo.addItem(self.parent().get_device_name_from_ip(i), userData=i)

        # Sort by name
        self._device_combo.model().sort(0)

        # Insert unknown device at the beginning
        self._device_combo.insertItem(0, lx('-Unknown-'), userData='')
        self._device_combo.setCurrentIndex(0)
        self.device_selected(0)


    def accept(self):
        t = self.get_type()

        # Validate IP address
        ip = self.get_ip()
        if t == LmPatPtf.RULE_TYPE_IPv6:
            if not LmTools.is_ipv6_pfix(ip):
                self.parent().display_error(mx('{} is not a valid IPv6 address or prefix.', 'ipv6AddrErr').format(ip))
                self._ip_edit.setFocus()
                return
        else:
            if not LmTools.is_ipv4(ip):
                self.parent().display_error(mx('{} is not a valid IPv4 address.', 'ipv4AddrErr').format(ip))
                self._ip_edit.setFocus()
                return

        # Validate external IP addresses
        e = self.get_ext_ips()
        if e:
            ext_ips = e.split(',')
            for ip in ext_ips:
                if len(ip) == 0:
                    self.parent().display_error(mx('Empty IP address.', 'emptyAddr'))
                    self._ext_ips_edit.setFocus()
                    return

                if t == LmPatPtf.RULE_TYPE_IPv6:
                    if not LmTools.is_ipv6(ip):
                        self.parent().display_error(mx('{} is not a valid IPv6 address.', 'ipv6AddrErr').format(ip))
                        self._ext_ips_edit.setFocus()
                        return
                else:
                    if not LmTools.is_ipv4(ip):
                        self.parent().display_error(mx('{} is not a valid IPv4 address.', 'ipv4AddrErr').format(ip))
                        self._ext_ips_edit.setFocus()
                        return

        super().accept()


    def get_enabled(self):
        return self._enable_checkbox.isChecked()


    def get_type(self):
        return self._type_combo.currentText()


    def get_name(self):
        return self._name_edit.text()


    def get_description(self):
        return self._desc_edit.toPlainText()


    def get_protocols(self):
        protocols = []

        if self._tcp_checkbox.isChecked():
            protocols.append(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.TCP.value)])

        if self._udp_checkbox.isChecked():
            protocols.append(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.UDP.value)])

        if self._ah_checkbox.isChecked():
            protocols.append(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.AH.value)])

        if self._gre_checkbox.isChecked():
            protocols.append(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.GRE.value)])

        if self._esp_checkbox.isChecked():
            protocols.append(LmPatPtf.PROTOCOL_NAMES[str(LmPatPtf.Protocols.ESP.value)])

        if self._icmp_checkbox.isChecked():
            if self.get_type() == LmPatPtf.RULE_TYPE_IPv6:
                icmp = LmPatPtf.Protocols.ICMPv6.value
            else:
                icmp = LmPatPtf.Protocols.ICMP.value
            protocols.append(LmPatPtf.PROTOCOL_NAMES[str(icmp)])

        return '/'.join(protocols)


    def get_ip(self):
        return self._ip_edit.text()


    def get_ext_ips(self):
        return self._ext_ips_edit.toPlainText()