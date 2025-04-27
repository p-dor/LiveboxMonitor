### Livebox Monitor Ping Response setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import GetPingResponseDialogLabel as lx


# ################################ Ping Response setup dialog ################################
class PingResponseDialog(QtWidgets.QDialog):
    def __init__(self, ipv4, ipv6, parent=None):
        super(PingResponseDialog, self).__init__(parent)
        self.setMinimumWidth(230)
        self.resize(230, 150)

        self._ipv4_checkbox = QtWidgets.QCheckBox(lx('Respond to IPv4 ping'), objectName='ipV4Checkbox')
        if ipv4:
                self._ipv4_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
                self._ipv4_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        self._ipv6_checkbox = QtWidgets.QCheckBox(lx('Respond to IPv6 ping'), objectName='ipV6Checkbox')
        if ipv6:
                self._ipv6_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
                self._ipv6_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        vcbox = QtWidgets.QVBoxLayout()
        vcbox.setSpacing(10)
        vcbox.addWidget(self._ipv4_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        vcbox.addWidget(self._ipv6_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

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

        LmConfig.SetToolTips(self, 'pingr')

        self.setWindowTitle(lx('Ping Responses'))

        self.setModal(True)
        self.show()


    def get_ipv4(self):
        return self._ipv4_checkbox.checkState() == QtCore.Qt.CheckState.Checked


    def get_ipv6(self):
        return self._ipv6_checkbox.checkState() == QtCore.Qt.CheckState.Checked
