### Livebox Monitor NAT/PAT rule type selection dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig, LmPatPtf
from LiveboxMonitor.lang.LmLanguages import get_nat_pat_rule_type_label as lx


# ################################ NAT/PAT rule type selection dialog ################################
class NatPatRuleTypeDialog(QtWidgets.QDialog):
    def __init__(self, upnp, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(230)
        self.resize(230, 150)

        self._upnp = upnp

        self._ipv4_checkbox = QtWidgets.QCheckBox(LmPatPtf.RULE_TYPE_IPv4, objectName='ipV4Checkbox')
        self._ipv4_checkbox.clicked.connect(self.set_ok_button_state)
        self._ipv6_checkbox = QtWidgets.QCheckBox(LmPatPtf.RULE_TYPE_IPv6, objectName='ipV6Checkbox')
        self._ipv6_checkbox.clicked.connect(self.set_ok_button_state)
        if upnp:
            self._upnp_checkbox = QtWidgets.QCheckBox(LmPatPtf.RULE_TYPE_UPnP, objectName='upnpCheckbox')
            self._upnp_checkbox.clicked.connect(self.set_ok_button_state)

        vcbox = QtWidgets.QVBoxLayout()
        vcbox.setSpacing(10)
        vcbox.addWidget(self._ipv4_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        vcbox.addWidget(self._ipv6_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        if upnp:
            vcbox.addWidget(self._upnp_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

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
        vbox.addLayout(vcbox, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, 'nprtype')

        self.setWindowTitle(lx('Select rule types'))

        self.set_default()

        self.setModal(True)
        self.show()


    # Set default values
    def set_default(self):
        self._ipv4_checkbox.setChecked(True)
        self._ipv6_checkbox.setChecked(True)
        if self._upnp:
            self._upnp_checkbox.setChecked(False)
        self.set_ok_button_state()


    def get_types(self):
        t = {
            LmPatPtf.RULE_TYPE_IPv4: self._ipv4_checkbox.isChecked(),
            LmPatPtf.RULE_TYPE_IPv6: self._ipv6_checkbox.isChecked()
        }
        if self._upnp:
            t[LmPatPtf.RULE_TYPE_UPnP] = self._upnp_checkbox.isChecked()
        return t


    def set_ok_button_state(self):
        if self._upnp:
            one_checked = (self._ipv4_checkbox.isChecked() or
                           self._ipv6_checkbox.isChecked() or
                           self._upnp_checkbox.isChecked())
        else:
            one_checked = (self._ipv4_checkbox.isChecked() or
                           self._ipv6_checkbox.isChecked())

        self._ok_button.setDisabled(not one_checked)
