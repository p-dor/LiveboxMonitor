### Livebox Monitor Firewall setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import GetFirewallLevelDialogLabel as lx


# ################################ VARS & DEFS ################################

# Firewall levels
FIREWALL_LEVELS = ['High', 'Medium', 'Low', 'Custom']


# ################################ Firewall Level dialog ################################
class FirewallLevelDialog(QtWidgets.QDialog):
	def __init__(self, iIPv4Level, iIPv6Level, iParent = None):
		super(FirewallLevelDialog, self).__init__(iParent)
		self.setMinimumWidth(230)
		self.resize(300, 150)

		aIpV4LevelLabel = QtWidgets.QLabel(lx('IPv4 Firewall Level'), objectName = 'ipV4Label')
		self._ipV4LevelCombo = QtWidgets.QComboBox(objectName = 'ipV4Combo')
		for l in FIREWALL_LEVELS:
			self._ipV4LevelCombo.addItem(lx(l), userData = l)
		self._ipV4LevelCombo.setCurrentIndex(FIREWALL_LEVELS.index(iIPv4Level))

		aIpV6LevelLabel = QtWidgets.QLabel(lx('IPv6 Firewall Level'), objectName = 'ipV6Label')
		self._ipV6LevelCombo = QtWidgets.QComboBox(objectName = 'ipV6Combo')
		for l in FIREWALL_LEVELS:
			self._ipV6LevelCombo.addItem(lx(l), userData = l)
		self._ipV6LevelCombo.setCurrentIndex(FIREWALL_LEVELS.index(iIPv6Level))

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(aIpV4LevelLabel, 0, 0)
		aGrid.addWidget(self._ipV4LevelCombo, 0, 1)
		aGrid.addWidget(aIpV6LevelLabel, 1, 0)
		aGrid.addWidget(self._ipV6LevelCombo, 1, 1)
		aGrid.setColumnStretch(0, 0)
		aGrid.setColumnStretch(1, 1)

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
		aVBox.addLayout(aGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'fwlevel')

		self.setWindowTitle(lx('Firewall Levels'))

		self.setModal(True)
		self.show()


	def getIPv4Level(self):
		return self._ipV4LevelCombo.currentData()


	def getIPv6Level(self):
		return self._ipV6LevelCombo.currentData()
