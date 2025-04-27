### Livebox Monitor Firewall setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import GetFirewallLevelDialogLabel as lx


# ################################ VARS & DEFS ################################

# Firewall levels
FIREWALL_LEVELS = ['High', 'Medium', 'Low', 'Custom']


# ################################ Firewall Level dialog ################################
class FirewallLevelDialog(QtWidgets.QDialog):
    def __init__(self, ipv4_level, ipv6_level, parent=None):
        super(FirewallLevelDialog, self).__init__(parent)
        self.setMinimumWidth(230)
        self.resize(300, 150)

        ipv4_level_label = QtWidgets.QLabel(lx('IPv4 Firewall Level'), objectName='ipV4Label')
        self._ipv4_level_combo = QtWidgets.QComboBox(objectName='ipV4Combo')
        for l in FIREWALL_LEVELS:
            self._ipv4_level_combo.addItem(lx(l), userData=l)
        self._ipv4_level_combo.setCurrentIndex(FIREWALL_LEVELS.index(ipv4_level))

        ipv6_level_label = QtWidgets.QLabel(lx('IPv6 Firewall Level'), objectName='ipV6Label')
        self._ipv6_level_combo = QtWidgets.QComboBox(objectName='ipV6Combo')
        for l in FIREWALL_LEVELS:
            self._ipv6_level_combo.addItem(lx(l), userData = l)
        self._ipv6_level_combo.setCurrentIndex(FIREWALL_LEVELS.index(ipv6_level))

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ipv4_level_label, 0, 0)
        grid.addWidget(self._ipv4_level_combo, 0, 1)
        grid.addWidget(ipv6_level_label, 1, 0)
        grid.addWidget(self._ipv6_level_combo, 1, 1)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

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

        LmConfig.SetToolTips(self, 'fwlevel')

        self.setWindowTitle(lx('Firewall Levels'))

        self.setModal(True)
        self.show()


    def get_ipv4_level(self):
        return self._ipv4_level_combo.currentData()


    def get_ipv6_level(self):
        return self._ipv6_level_combo.currentData()
