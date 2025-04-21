### Livebox Monitor Ping Response setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import GetPingResponseDialogLabel as lx


# ################################ Ping Response setup dialog ################################
class PingResponseDialog(QtWidgets.QDialog):
	def __init__(self, iIPv4, iIPv6, iParent = None):
		super(PingResponseDialog, self).__init__(iParent)
		self.setMinimumWidth(230)
		self.resize(230, 150)

		self._ipV4CheckBox = QtWidgets.QCheckBox(lx('Respond to IPv4 ping'), objectName = 'ipV4Checkbox')
		if iIPv4:
				self._ipV4CheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
				self._ipV4CheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		self._ipV6CheckBox = QtWidgets.QCheckBox(lx('Respond to IPv6 ping'), objectName = 'ipV6Checkbox')
		if iIPv6:
				self._ipV6CheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
				self._ipV6CheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		aVCBox = QtWidgets.QVBoxLayout()
		aVCBox.setSpacing(10)
		aVCBox.addWidget(self._ipV4CheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aVCBox.addWidget(self._ipV6CheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

		self._okButton = QtWidgets.QPushButton(lx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aVCBox, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'pingr')

		self.setWindowTitle(lx('Ping Responses'))

		self.setModal(True)
		self.show()


	def getIPv4(self):
		return self._ipV4CheckBox.checkState() == QtCore.Qt.CheckState.Checked


	def getIPv6(self):
		return self._ipV6CheckBox.checkState() == QtCore.Qt.CheckState.Checked
