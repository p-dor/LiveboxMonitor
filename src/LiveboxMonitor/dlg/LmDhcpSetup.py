### Livebox Monitor DHCP Setup dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.lang.LmLanguages import get_dhcp_setup_label as lx


# ################################ DHCP Setup dialog ################################
class DhcpSetupDialog(QtWidgets.QDialog):
    def __init__(self, enabled, address, mask, min_addr, max_addr, parent=None):
        super().__init__(parent)
        self.resize(300, 225)

        self._enable_checkbox = QtWidgets.QCheckBox(lx('DHCP Enabled'), objectName='enableCheckbox')
        self._enable_checkbox.setChecked(enabled)

        ip_reg_exp = QtCore.QRegularExpression('^' + LmTools.IPv4_RS + '$')
        ip_validator = QtGui.QRegularExpressionValidator(ip_reg_exp)

        livebox_ip_label = QtWidgets.QLabel(lx('Livebox IP address'), objectName='liveboxIpLabel')
        self._livebox_ip_edit = QtWidgets.QLineEdit(objectName='liveboxIpEdit')
        self._livebox_ip_edit.setValidator(ip_validator)
        self._livebox_ip_edit.setText(address)
        self._livebox_ip_edit.textChanged.connect(self.text_typed)

        mask_label = QtWidgets.QLabel(lx('Subnet mask'), objectName='maskLabel')
        self._mask_edit = QtWidgets.QLineEdit(objectName='maskEdit')
        self._mask_edit.setValidator(ip_validator)
        self._mask_edit.setText(mask)
        self._mask_edit.textChanged.connect(self.text_typed)

        min_ip_label = QtWidgets.QLabel(lx('DHCP start IP'), objectName='minLabel')
        self._min_edit = QtWidgets.QLineEdit(objectName='minEdit')
        self._min_edit.setValidator(ip_validator)
        self._min_edit.setText(min_addr)
        self._min_edit.textChanged.connect(self.text_typed)

        max_ip_label = QtWidgets.QLabel(lx('DHCP end IP'), objectName='maxLabel')
        self._max_edit = QtWidgets.QLineEdit(objectName='maxEdit')
        self._max_edit.setValidator(ip_validator)
        self._max_edit.setText(max_addr)
        self._max_edit.textChanged.connect(self.text_typed)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self._enable_checkbox, 0, 0)
        grid.addWidget(livebox_ip_label, 1, 0)
        grid.addWidget(self._livebox_ip_edit, 1, 1)
        grid.addWidget(mask_label, 2, 0)
        grid.addWidget(self._mask_edit, 2, 1)
        grid.addWidget(min_ip_label, 3, 0)
        grid.addWidget(self._min_edit, 3, 1)
        grid.addWidget(max_ip_label, 4, 0)
        grid.addWidget(self._max_edit, 4, 1)

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

        LmConfig.set_tooltips(self, 'dsetup')

        self.setWindowTitle(lx('DHCP Setup'))
        self.set_ok_button_state()
        self.setModal(True)
        self.show()


    def text_typed(self, text):
        self.set_ok_button_state()


    def set_ok_button_state(self):
        self._ok_button.setDisabled((len(self.get_address()) == 0) or
                                    (len(self.get_mask()) == 0) or
                                    (len(self.get_min_address()) == 0) or
                                    (len(self.get_max_address()) == 0))


    def get_enabled(self):
        return self._enable_checkbox.isChecked()


    def get_address(self):
        return self._livebox_ip_edit.text()


    def get_mask(self):
        return self._mask_edit.text()


    def get_min_address(self):
        return self._min_edit.text()


    def get_max_address(self):
        return self._max_edit.text()
