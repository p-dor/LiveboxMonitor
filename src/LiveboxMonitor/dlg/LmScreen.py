### Livebox Monitor screen & LEDs setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import GetScreenDialogLabel as lx


# ################################ Screen setup dialog ################################
class ScreenDialog(QtWidgets.QDialog):
	def __init__(self, iOrangeLedLevel, iShowWifiPassword, iParent = None):
		super(ScreenDialog, self).__init__(iParent)
		self.setMinimumWidth(300)
		self.resize(350, 150)

		aOrangeLabel = QtWidgets.QLabel(lx('LED Brightness'), objectName = 'orangeLabel')
		self._orangeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, objectName = 'orangeSlider')
		self._orangeSlider.setRange(0, 255)
		self._orangeSlider.setValue(iOrangeLedLevel)
		self._orangeSlider.setSingleStep(5)
		self._orangeSlider.setPageStep(50)
		self._orangeSlider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksAbove)
		self._orangeSlider.setTickInterval(15)
		self._orangeSlider.valueChanged.connect(self.orangeLevelChanged)
		self._orangeValue = QtWidgets.QLabel(str(iOrangeLedLevel), objectName = 'orangeValue')
		self._orangeValue.setMinimumWidth(20)

		self._showWifiPasswordCheckBox = QtWidgets.QCheckBox(lx('Show Wifi Password'), objectName = 'showWifiPasswordCheckbox')
		if iShowWifiPassword:
			self._showWifiPasswordCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._showWifiPasswordCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(aOrangeLabel, 0, 0)
		aGrid.addWidget(self._orangeSlider, 0, 1)
		aGrid.addWidget(self._orangeValue, 0, 2)
		aGrid.addWidget(self._showWifiPasswordCheckBox, 1, 0, 1, 3)

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

		LmConfig.SetToolTips(self, 'screen')

		self.setWindowTitle(lx('LEDs & Screen Setup'))

		self.setModal(True)
		self.show()


	def orangeLevelChanged(self, iValue):
		self._orangeValue.setText(str(iValue))


	def getOrangeLedLevel(self):
		return self._orangeSlider.value()


	def getShowWifiPassword(self):
		return self._showWifiPasswordCheckBox.checkState() == QtCore.Qt.CheckState.Checked
