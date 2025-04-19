### Livebox Monitor Wifi Configuration setup dialog ###

import copy

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.lang.LmLanguages import GetWifiConfigDialogLabel as lx


# ################################ VARS & DEFS ################################

# Wifi MAC Filtering modes
MAC_FILTERING_MODES = ['Off', 'WhiteList', 'BlackList']


# ################################ Wifi Configuration dialog ################################
class WifiConfigDialog(QtWidgets.QDialog):
	def __init__(self, iParent, iConfig, iGuest):
		super(WifiConfigDialog, self).__init__(iParent)

		self._guest = iGuest
		if self._guest:
			self.resize(390, 350)
		else:
			self.resize(390, 380)

		self._enableCheckBox = QtWidgets.QCheckBox(lx('Enabled'), objectName = 'enableCheckbox')
		self._enableCheckBox.clicked.connect(self.enableClick)

		if self._guest:
			aDurationLabel = QtWidgets.QLabel(lx('Duration'), objectName = 'durationLabel')
			aIntValidator = QtGui.QIntValidator()
			aIntValidator.setRange(0, 999)
			self._durationEdit = QtWidgets.QLineEdit(objectName = 'durationEdit')
			self._durationEdit.setValidator(aIntValidator)
			aDurationUnit = QtWidgets.QLabel(lx('hours (0 = unlimited).'), objectName = 'durationUnit')

		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aFreqLabel = QtWidgets.QLabel(lx('Radio Band'), objectName = 'freqLabel')
		self._freqCombo = QtWidgets.QComboBox(objectName = 'freqCombo')
		self._freqCombo.activated.connect(self.freqSelected)

		aSsidLabel = QtWidgets.QLabel(lx('SSID'), objectName = 'ssidLabel')
		self._ssidEdit = QtWidgets.QLineEdit(objectName = 'ssidEdit')

		aOptionsLabel = QtWidgets.QLabel(lx('Options'), objectName = 'optionsLabel')
		self._freqEnabledCheckBox = QtWidgets.QCheckBox(lx('Enabled'), objectName = 'freqEnabledCheckbox')
		self._broadcastCheckBox = QtWidgets.QCheckBox(lx('SSID Broadcast'), objectName = 'broadcastCheckbox')
		self._wpsCheckBox = QtWidgets.QCheckBox(lx('WPS'), objectName = 'wpsCheckbox')
		aOptionsBox = QtWidgets.QHBoxLayout()
		aOptionsBox.setSpacing(10)
		aOptionsBox.addWidget(self._freqEnabledCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aOptionsBox.addWidget(self._broadcastCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aOptionsBox.addWidget(self._wpsCheckBox, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

		aMacFilteringLabel = QtWidgets.QLabel(lx('MAC Filtering'), objectName = 'macFilteringLabel')
		self._macFilteringCombo = QtWidgets.QComboBox(objectName = 'macFilteringCombo')
		self._macFilteringCombo.addItems(MAC_FILTERING_MODES)

		aSecuLabel = QtWidgets.QLabel(lx('Security'), objectName = 'secuLabel')
		self._secuCombo = QtWidgets.QComboBox(objectName = 'secuCombo')
		self._secuCombo.activated.connect(self.secuSelected)

		aPassLabel = QtWidgets.QLabel(lx('Password'), objectName = 'passLabel')
		self._passEdit = QtWidgets.QLineEdit(objectName = 'passEdit')
		self._passEdit.textChanged.connect(self.passTyped)

		if not self._guest:
			aChanLabel = QtWidgets.QLabel(lx('Channel'), objectName = 'chanLabel')
			self._chanCombo = QtWidgets.QComboBox(objectName = 'chanCombo')

			aModeLabel = QtWidgets.QLabel(lx('Mode'), objectName = 'modeLabel')
			self._modeCombo = QtWidgets.QComboBox(objectName = 'modeCombo')

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)

		if self._guest:
			aGrid.addWidget(self._enableCheckBox, 0, 0, 1, 4)
			aGrid.addWidget(aDurationLabel, 1, 0)
			aGrid.addWidget(self._durationEdit, 1, 1)
			aGrid.addWidget(aDurationUnit, 1, 2, 1, 3)
			aGrid.addWidget(aSeparator, 2, 0, 1, 5)
			aGrid.addWidget(aFreqLabel, 3, 0)
			aGrid.addWidget(self._freqCombo, 3, 1, 1, 4)
			aGrid.addWidget(aSsidLabel, 4, 0)
			aGrid.addWidget(self._ssidEdit, 4, 1, 1, 4)
			aGrid.addWidget(aOptionsLabel, 5, 0)
			aGrid.addLayout(aOptionsBox, 5, 1, 1, 4)
			aGrid.addWidget(aMacFilteringLabel, 6, 0)
			aGrid.addWidget(self._macFilteringCombo, 6, 1, 1, 4)			
			aGrid.addWidget(aSecuLabel, 7, 0)
			aGrid.addWidget(self._secuCombo, 7, 1, 1, 4)
			aGrid.addWidget(aPassLabel, 8, 0)
			aGrid.addWidget(self._passEdit, 8, 1, 1, 4)

			# Cannot be changed on guest interfaces
			self._broadcastCheckBox.setEnabled(False)
			self._wpsCheckBox.setEnabled(False)
			self._macFilteringCombo.setEnabled(False)
		else:
			aGrid.addWidget(self._enableCheckBox, 0, 0, 1, 2)
			aGrid.addWidget(aSeparator, 1, 0, 1, 2)
			aGrid.addWidget(aFreqLabel, 2, 0)
			aGrid.addWidget(self._freqCombo, 2, 1)
			aGrid.addWidget(aSsidLabel, 3, 0)
			aGrid.addWidget(self._ssidEdit, 3, 1)
			aGrid.addWidget(aOptionsLabel, 4, 0)
			aGrid.addLayout(aOptionsBox, 4, 1)
			aGrid.addWidget(aMacFilteringLabel, 5, 0)
			aGrid.addWidget(self._macFilteringCombo, 5, 1)			
			aGrid.addWidget(aSecuLabel, 6, 0)
			aGrid.addWidget(self._secuCombo, 6, 1)
			aGrid.addWidget(aPassLabel, 7, 0)
			aGrid.addWidget(self._passEdit, 7, 1)
			aGrid.addWidget(aChanLabel, 8, 0)
			aGrid.addWidget(self._chanCombo, 8, 1)
			aGrid.addWidget(aModeLabel, 9, 0)
			aGrid.addWidget(self._modeCombo, 9, 1)

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

		LmConfig.SetToolTips(self, 'wconfig')

		if self._guest:
			self.setWindowTitle(lx('Guest Wifi Configuration'))
		else:
			self.setWindowTitle(lx('Wifi Configuration'))

		self.setConfig(iConfig)

		self._ssidEdit.setFocus()
		self.setModal(True)
		self.show()


	def setConfig(self, iConfig):
		self._config = copy.deepcopy(iConfig)
		self._currentFreq = None

		if self._config['Enable']:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if self._guest:
			self._durationEdit.setText(str(self._config['Duration'] // 3600))
			aTimer = self._config['Timer']
			if aTimer:
				self._enableCheckBox.setText(lx('Enabled for {}').format(LmTools.FmtTime(aTimer, True)))

		self.enableClick()		
		self.loadFreqCombo()
		self.freqSelected(0)


	def enableClick(self):
		if self._guest:
			if self._enableCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
				self._durationEdit.setText(str(self._config['Duration'] // 3600))
				self._durationEdit.setEnabled(True)
			else:
				self._durationEdit.setText('0')
				self._durationEdit.setEnabled(False)


	def loadFreqCombo(self):
		c = self._config['Intf']
		for f in c:
			self._freqCombo.addItem(f['Name'], userData = f['Key'])


	def freqSelected(self, iIndex):
		# First save config of previously selected freq
		self.saveFreqConfig()

		# Retrieve interface in config according to selection
		aKey, i = self.getCurrentKeyIntf()
		if i is None:
			return
		self._currentFreq = aKey

		self._ssidEdit.setText(i['SSID'])
		self._passEdit.setText(i['KeyPass'])

		if i['Enable']:
			self._freqEnabledCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._freqEnabledCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if i['Broadcast']:
			self._broadcastCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._broadcastCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if i['WPS']:
			self._wpsCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._wpsCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		try:
			aIndex = MAC_FILTERING_MODES.index(i['MACFiltering'])
		except:
			MAC_FILTERING_MODES.append(i['MACFiltering'])
			self._macFilteringCombo.addItem(i['MACFiltering'])
			aIndex = self._macFilteringCombo.count() - 1
		self._macFilteringCombo.setCurrentIndex(aIndex)

		self.loadSecuCombo()

		if not self._guest:
			self.loadChanCombo()
			self.loadModeCombo()


	def saveFreqConfig(self):
		if self._currentFreq is not None:
			i = next((i for i in self._config['Intf'] if i['Key'] == self._currentFreq), None)
			if i is None:
				LmTools.Error('Internal error, unconsistent configuration - intf not found')
				self.reject()
				return
			i['SSID'] = self._ssidEdit.text()
			i['Enable'] = self._freqEnabledCheckBox.checkState() == QtCore.Qt.CheckState.Checked
			i['Broadcast'] = self._broadcastCheckBox.checkState() == QtCore.Qt.CheckState.Checked
			i['WPS'] = self._wpsCheckBox.checkState() == QtCore.Qt.CheckState.Checked
			i['MACFiltering'] = self._macFilteringCombo.currentText()
			i['Secu'] = self._secuCombo.currentText()
			if i['Secu'] != 'None':
				i['KeyPass'] = self._passEdit.text()

			if not self._guest:
				aChan = self._chanCombo.currentText()
				if aChan == 'Auto':
					i['ChannelAuto'] = True
				else:
					i['ChannelAuto'] = False
					i['Channel'] = int(aChan)
				i['Mode'] = self._modeCombo.currentText()


	def passTyped(self, iText):
		self.setOkButtonState()


	def loadSecuCombo(self):
		aKey, i = self.getCurrentKeyIntf()
		if i is None:
			return
		aSecu = i['Secu']
		aSecuList = i['SecuAvail']
		if aSecuList is None:
			LmTools.Error('Internal error, unconsistent configuration - no security list')
			self.reject()
		aSecuList = aSecuList.split(',')
		self._secuCombo.clear()
		n = 0
		aSelection = -1
		for s in aSecuList:
			if not 'WEP' in s:
				if s == aSecu:
					aSelection = n
				self._secuCombo.addItem(s)
				n += 1

		if aSelection == -1:
			if aSecu is not None:
				self._secuCombo.addItem(aSecu)
				aSelection = n
				LmTools.LogDebug(1, 'Warning - security {} not in list'.format(aSecu))
			elif n == 0:
				LmTools.Error('Internal error, unconsistent configuration - no security')
				self.reject()
			else:
				LmTools.LogDebug(1, 'Warning - no security, defaulting to first')
				aSelection = 0

		if aSelection >= 0:
			self._secuCombo.setCurrentIndex(aSelection)
			self.secuSelected(aSelection)


	def secuSelected(self, iIndex):
		aKey, i = self.getCurrentKeyIntf()
		if i is None:
			return

		aSecu = self._secuCombo.currentText()
		if aSecu == 'None':
			# Save pass key in case secu is reselected
			i['KeyPass'] = self._passEdit.text()
			self._passEdit.setEnabled(False)
			self._passEdit.setText('')
		else:
			self._passEdit.setEnabled(True)
			if len(self._passEdit.text()) == 0:
				self._passEdit.setText(i['KeyPass'])

		self.setOkButtonState()


	def loadChanCombo(self):
		aKey, i = self.getCurrentKeyIntf()
		if i is None:
			return
		aIntf = i['LLIntf']

		aModes = self._config['Modes'].get(aIntf)
		if aModes is not None:
			aChannels = aModes.get('Channels')
			aChannelsInUse = aModes.get('ChannelsInUse')
		else:
			aChannels = None
			aChannelsInUse = None
		if aChannels is None:
			LmTools.Error('Internal error, unconsistent configuration - no channel list')
			self.reject()
			return
		aChannels = aChannels.split(',')
		if aChannelsInUse is None:
			aChannelsInUse = []
		else:
			aChannelsInUse = aChannelsInUse.split(',')

		aCurrentChannel = str(i['Channel'])

		self._chanCombo.clear()
		n = 0
		aSelection = -1
		if i['ChannelAutoSupport']:
			self._chanCombo.addItem('Auto')
			if i['ChannelAuto']:
				aSelection = n
			n += 1
		for c in aChannels:
			if (not c in aChannelsInUse) or (c == aCurrentChannel):
				self._chanCombo.addItem(c)
				if (c == aCurrentChannel) and (aSelection == -1):
					aSelection = n
				n += 1

		if aSelection == -1:
			if aCurrentChannel != 'None':
				self._chanCombo.addItem(aCurrentChannel)
				aSelection = n
				LmTools.LogDebug(1, 'Warning - channel {} not in list'.format(aSecu))
			elif n == 0:
				LmTools.Error('Internal error, unconsistent configuration - no channel')
				self.reject()
			else:
				LmTools.LogDebug(1, 'Warning - no channel, defaulting to first')
				aSelection = 0

		if aSelection >= 0:
			self._chanCombo.setCurrentIndex(aSelection)


	def loadModeCombo(self):
		aKey, i = self.getCurrentKeyIntf()
		if i is None:
			return
		aIntf = i['LLIntf']

		aModes = self._config['Modes'].get(aIntf)
		if aModes is not None:
			aModes = aModes.get('Modes')
		if aModes is None:
			LmTools.Error('Internal error, unconsistent configuration - no mode list')
			self.reject()
			return
		aModes = aModes.split(',')

		aCurrentMode = i['Mode']

		self._modeCombo.clear()
		n = 0
		aSelection = -1
		for m in aModes:
			self._modeCombo.addItem(m)
			if m == aCurrentMode:
				aSelection = n
			n += 1

		if aSelection == -1:
			if aCurrentMode is not None:
				self._modeCombo.addItem(aCurrentMode)
				aSelection = n
				LmTools.LogDebug(1, 'Warning - mode {} not in list'.format(aCurrentMode))
			elif n == 0:
				LmTools.Error('Internal error, unconsistent configuration - no mode')
				self.reject()
			else:
				LmTools.LogDebug(1, 'Warning - no mode, defaulting to first')
				aSelection = 0

		if aSelection >= 0:
			self._modeCombo.setCurrentIndex(aSelection)


	def getCurrentKeyIntf(self):
		aKey = self._freqCombo.currentData()
		i = next((i for i in self._config['Intf'] if i['Key'] == aKey), None)
		if i is None:
			LmTools.Error('Internal error, unconsistent configuration - intf {} not found'.format(aKey))
			self.reject()
		return aKey, i


	def getConfig(self):
		self._config['Enable'] = self._enableCheckBox.checkState() == QtCore.Qt.CheckState.Checked
		if self._guest:
			self._config['Duration'] = int(self._durationEdit.text()) * 3600
		self.saveFreqConfig()
		return self._config


	def setOkButtonState(self):
		# Check if another frequency is in background with no passkey
		aDisable = False
		for i in self._config['Intf']:
			if i['Key'] == self._currentFreq:
				continue
			if (i['Secu'] != 'None') and (len(i['KeyPass']) == 0):
				aDisable = True
				break

		# Check current frequency
		if not aDisable:
			if (self._secuCombo.currentText() != 'None') and (len(self._passEdit.text()) == 0):
				aDisable = True

		self._okButton.setDisabled(aDisable)
