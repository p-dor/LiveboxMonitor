### Livebox Monitor device info tab module ###

import requests
import json

from enum import IntEnum

from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWidgets

from src import LmTools
from src import LmConfig
from src.LmConfig import LmConf
from src.LmDeviceListTab import DSelCol
from src.LmInfoTab import InfoCol



# ################################ VARS & DEFS ################################

# Static Config
MACADDR_URL = 'https://api.macaddress.io/v1?apiKey={0}&output=json&search={1}'



# ################################ LmDeviceInfo class ################################
class LmDeviceInfo:

	### Create device info tab
	def createDeviceInfoTab(self):
		self._deviceInfoTab = QtWidgets.QWidget()

		# Device list
		self._infoDList = QtWidgets.QTableWidget()
		self._infoDList.setColumnCount(DSelCol.Count)
		self._infoDList.setHorizontalHeaderLabels(('Key', 'Name', 'MAC'))
		self._infoDList.setColumnHidden(DSelCol.Key, True)
		aHeader = self._infoDList.horizontalHeader()
		aHeader.setSectionResizeMode(DSelCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(DSelCol.MAC, QtWidgets.QHeaderView.ResizeMode.Fixed)
		self._infoDList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._infoDList.setColumnWidth(DSelCol.Name, 200)
		self._infoDList.setColumnWidth(DSelCol.MAC, 120 + LmConfig.SCROLL_BAR_ADJUST)
		self._infoDList.verticalHeader().hide()
		self._infoDList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._infoDList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._infoDList.setSortingEnabled(True)
		self._infoDList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._infoDList.setMinimumWidth(350 + LmConfig.SCROLL_BAR_ADJUST)
		self._infoDList.itemSelectionChanged.connect(self.infoDeviceListClick)
		LmConfig.SetTableStyle(self._infoDList)

		# Attribute list
		self._infoAList = QtWidgets.QTableWidget()
		self._infoAList.setColumnCount(InfoCol.Count)
		self._infoAList.setHorizontalHeaderLabels(('Attribute', 'Value'))
		aHeader = self._infoAList.horizontalHeader()
		aHeader.setSectionResizeMode(InfoCol.Attribute, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aHeader.setSectionResizeMode(InfoCol.Value, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._infoAList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._infoAList.setColumnWidth(InfoCol.Attribute, 200)
		self._infoAList.setColumnWidth(InfoCol.Value, 600)
		self._infoAList.verticalHeader().hide()
		self._infoAList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._infoAList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._infoAList)

		# Lists layout
		aListBox = QtWidgets.QHBoxLayout()
		aListBox.setSpacing(10)
		aListBox.addWidget(self._infoDList, 0)
		aListBox.addWidget(self._infoAList, 1)

		# Button bar
		aButtonsBox = QtWidgets.QHBoxLayout()
		aButtonsBox.setSpacing(30)
		aRefreshDeviceInfoButton = QtWidgets.QPushButton('Refresh')
		aRefreshDeviceInfoButton.clicked.connect(self.refreshDeviceInfoButtonClick)
		aButtonsBox.addWidget(aRefreshDeviceInfoButton)
		aAssignNameButton = QtWidgets.QPushButton('Assign Name...')
		aAssignNameButton.clicked.connect(self.assignNameButtonClick)
		aButtonsBox.addWidget(aAssignNameButton)
		aAssignTypeButton = QtWidgets.QPushButton('Assign Type...')
		aAssignTypeButton.clicked.connect(self.assignTypeButtonClick)
		aButtonsBox.addWidget(aAssignTypeButton)
		aForgetButton = QtWidgets.QPushButton('Forget...')
		aForgetButton.clicked.connect(self.forgetButtonClick)
		aButtonsBox.addWidget(aForgetButton)
		aBlockDeviceButton = QtWidgets.QPushButton('Block')
		aBlockDeviceButton.clicked.connect(self.blockDeviceButtonClick)
		aButtonsBox.addWidget(aBlockDeviceButton)
		aUnblockDeviceButton = QtWidgets.QPushButton('Unblock')
		aUnblockDeviceButton.clicked.connect(self.unblockDeviceButtonClick)
		aButtonsBox.addWidget(aUnblockDeviceButton)

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addLayout(aListBox, 0)
		aVBox.addLayout(aButtonsBox, 1)
		self._deviceInfoTab.setLayout(aVBox)

		self._tabWidget.addTab(self._deviceInfoTab, 'Device Infos')

		# Init context
		self.initDeviceContext()


	### Init selected device context
	def initDeviceContext(self):
		self._currentDeviceLiveboxName = None
		self._currentDeviceType = ''


	### Click on info device list
	def infoDeviceListClick(self):
		self._infoAList.clearContents()
		self._infoAList.setRowCount(0)

		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			self.updateDeviceInfo(aKey)


	### Click on device infos refresh button
	def refreshDeviceInfoButtonClick(self):
		self.infoDeviceListClick()


	### Click on assign device name button
	def assignNameButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			aName = LmConf.MacAddrTable.get(aKey, None)

			aSetDeviceNameDialog = SetDeviceNameDialog(aKey, aName, self._currentDeviceLiveboxName, self)
			if (aSetDeviceNameDialog.exec()):
				aName = aSetDeviceNameDialog.getName()
				if aName is None:
					self.delDeviceName(aKey)
				else:
					self.setDeviceName(aKey, aName)

				aName = aSetDeviceNameDialog.getLiveboxName()
				if aName is None:
					aSuccess = self.delDeviceLiveboxName(aKey)
				else:
					aSuccess = self.setDeviceLiveboxName(aKey, aName)
				if aSuccess:
					self.infoDeviceListClick()
		else:
			LmTools.DisplayError('Please select a device.')


	### Set a device name stored in the the MacAddr table
	def setDeviceName(self, iDeviceKey, iDeviceName):
		aCurrentName = LmConf.MacAddrTable.get(iDeviceKey, None)
		if (aCurrentName is None) or (aCurrentName != iDeviceName):
			LmConf.MacAddrTable[iDeviceKey] = iDeviceName
			LmConf.saveMacAddrTable()
			self.updateDeviceName(iDeviceKey)


	### Delete a device name from the MacAddr table
	def delDeviceName(self, iDeviceKey):
		try:
			del LmConf.MacAddrTable[iDeviceKey]
		except:
			pass
		else:
			LmConf.saveMacAddrTable()
			self.updateDeviceName(iDeviceKey)


	### Set a device name for Livebox
	def setDeviceLiveboxName(self, iDeviceKey, iDeviceName):
		try:
			aReply = self._session.request('Devices.Device.' + iDeviceKey + ':setName', { 'name': iDeviceName })
			if (aReply is not None) and (aReply.get('status', False)):
				LmTools.DisplayStatus('Livebox name successfully assigned.')
				return True
			else:
				LmTools.DisplayError('Set Livebox name query failed.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('Set Livebox name query error.')
		return False


	### Delete a device name from the Livebox
	def delDeviceLiveboxName(self, iDeviceKey):
		try:
			aReply = self._session.request('Devices.Device.' + iDeviceKey + ':removeName', { 'source': 'webui' })
			if (aReply is not None) and (aReply.get('status', False)):
				LmTools.DisplayStatus('Livebox name successfully removed.')
				return True
			else:
				LmTools.DisplayError('Remove Livebox name query failed.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('Remove Livebox name query error.')
		return False


	### Click on assign device type button
	def assignTypeButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()

			self.startTask('Loading device icons...')
			LmConf.loadDeviceIcons()
			self.endTask()

			aSetDeviceTypeDialog = SetDeviceTypeDialog(aKey, self._currentDeviceType, self)
			if (aSetDeviceTypeDialog.exec()):
				aType = aSetDeviceTypeDialog.getTypeKey()
				try:
					aReply = self._session.request('Devices.Device.' + aKey + ':setType', { 'type': aType })
					if (aReply is not None) and (aReply.get('status', False)):
						LmTools.DisplayStatus('Type successfully assigned.')
						self.infoDeviceListClick()
					else:
						LmTools.DisplayError('Set type query failed.')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					LmTools.DisplayError('Set type query error.')
		else:
			LmTools.DisplayError('Please select a device.')


	### Click on forget device button
	def forgetButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			if LmTools.AskQuestion('Are you sure you want to forget device [' + aKey + ']?'):
				try:
					aReply = self._session.request('Devices:destroyDevice', { 'key': aKey })
					if (aReply is not None) and (aReply.get('status', False)):
						self._infoDList.setCurrentCell(-1, -1)
						# Call event handler directly - in some (unknown) cases, the event is not raised
						self.processDeviceDeletedEvent(aKey)
						LmTools.DisplayStatus('Device ' + aKey + ' successfully removed.')
					else:
						LmTools.DisplayError('Destroy device query failed.')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					LmTools.DisplayError('Destroy device query error.')
		else:
			LmTools.DisplayError('Please select a device.')


	### Click on block device button
	def blockDeviceButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			try:
				aReply = self._session.request('Scheduler:overrideSchedule', { 'type': 'ToD', 'ID': aKey, 'override': 'Disable' })
				if (aReply is not None) and (aReply.get('status', False)):
					LmTools.DisplayStatus('Device ' + aKey + ' successfully blocked.')
				else:
					LmTools.DisplayError('Block query failed.')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				LmTools.DisplayError('Block query error.')
		else:
			LmTools.DisplayError('Please select a device.')


	### Click on unblock device button
	def unblockDeviceButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			try:
				aReply = self._session.request('Scheduler:overrideSchedule', { 'type': 'ToD', 'ID': aKey, 'override': 'Enable' })
				if (aReply is not None) and (aReply.get('status', False)):
					LmTools.DisplayStatus('Device ' + aKey + ' successfully unblocked.')
				else:
					LmTools.DisplayError('Unblock query failed.')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				LmTools.DisplayError('Unblock query error.')
		else:
			LmTools.DisplayError('Please select a device.')


	### Update device infos list
	def updateDeviceInfo(self, iDeviceKey):
		self.startTask('Getting device information...')

		try:
			d = self._session.request('Devices.Device.' + iDeviceKey + ':get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if (d is not None):
			d = d.get('status')
		if (d is None):
			self.endTask()
			LmTools.DisplayError('Error getting device information.')
			return

		i = 0
		i = self.addInfoLine(self._infoAList, i, 'Key', iDeviceKey)
		i = self.addInfoLine(self._infoAList, i, 'Active', LmTools.FmtBool(d.get('Active')))
		i = self.addInfoLine(self._infoAList, i, 'Authenticated', LmTools.FmtBool(d.get('AuthenticationState')))

		try:
			aData = self._session.request('Scheduler:getSchedule', { 'type': 'ToD', 'ID': iDeviceKey })
			aBlocked = False
			if (aData is not None):
				aData = aData.get('data')
			if (aData is not None):
				aData = aData.get('scheduleInfo')
			if (aData is not None):
				aBlocked = (aData.get('override', '') == 'Disable') and (aData.get('value', '') == 'Disable')
			i = self.addInfoLine(self._infoAList, i, 'Blocked', LmTools.FmtBool(aBlocked))
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			i = self.addInfoLine(self._infoAList, i, 'Blocked', 'Scheduler:getSchedule query error', LmTools.ValQual.Error)

		i = self.addInfoLine(self._infoAList, i, 'First connection', LmTools.FmtLiveboxTimestamp(d.get('FirstSeen')))
		i = self.addInfoLine(self._infoAList, i, 'Last connection', LmTools.FmtLiveboxTimestamp(d.get('LastConnection')))
		i = self.addInfoLine(self._infoAList, i, 'Last changed', LmTools.FmtLiveboxTimestamp(d.get('LastChanged')))
		i = self.addInfoLine(self._infoAList, i, 'Source', d.get('DiscoverySource'))

		self._currentDeviceLiveboxName = d.get('Name', None)
		i = self.addInfoLine(self._infoAList, i, 'Livebox Name', self._currentDeviceLiveboxName)

		aNameList = d.get('Names', [])
		if len(aNameList):
			for aName in aNameList:
				i = self.addInfoLine(self._infoAList, i, 'Name', aName.get('Name', '') + ' (' + aName.get('Source', '') + ')')
		
		aDNSList = d.get('mDNSService', [])
		if len(aDNSList):
			for aDNSName in aDNSList:
				i = self.addInfoLine(self._infoAList, i, 'DNS Name', aDNSName.get('Name', '') + ' (' + aDNSName.get('ServiceName', '') + ')')

		self._currentDeviceType = d.get('DeviceType', '')

		aTypeList = d.get('DeviceTypes', [])
		if len(aTypeList):
			for aType in aTypeList:
				i = self.addInfoLine(self._infoAList, i, 'Type', aType.get('Type', '') + ' (' + aType.get('Source', '') + ')')

		aIPv4List = d.get('IPv4Address', [])
		if len(aIPv4List):
			for aIPV4 in aIPv4List:
				s = aIPV4.get('Address', '') + ' (' + aIPV4.get('Status', '') + ')'
				if aIPV4.get('Reserved', False):
					s += ' - Reserved'
				i = self.addInfoLine(self._infoAList, i, 'IPv4 Address', s)

		aIPv6List = d.get('IPv6Address', [])
		if len(aIPv6List):
			for aIPV6 in aIPv6List:
				i = self.addInfoLine(self._infoAList, i, 'IPv6 Address', aIPV6.get('Address', '') +
																		 ' [' + aIPV6.get('Scope', '') + ']' +
																		 ' (' + aIPV6.get('Status', '') + ')')

		aMacAddr = d.get('PhysAddress', '')
		if len(aMacAddr) == 0:
			aMacAddr = iDeviceKey
		aManufacturer = ''
		if (len(LmConf.MacAddrApiKey)) and (len(aMacAddr)):
			try:
				aData = requests.get(MACADDR_URL.format(LmConf.MacAddrApiKey, aMacAddr))
				aData = json.loads(aData.content)
				aCompDetails = aData.get('vendorDetails')
				if aCompDetails is not None:
					aManufacturer = aCompDetails.get('companyName', '') + ' - ' + aCompDetails.get('countryCode', '')
				i = self.addInfoLine(self._infoAList, i, 'Manufacturer', aManufacturer)
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				i = self.addInfoLine(self._infoAList, i, 'Manufacturer', 'Web query error', LmTools.ValQual.Error)

		i = self.addInfoLine(self._infoAList, i, 'Vendor ID', d.get('VendorClassID'))
		i = self.addInfoLine(self._infoAList, i, 'Serial Number', d.get('SerialNumber'))
		i = self.addInfoLine(self._infoAList, i, 'Product Class', d.get('ProductClass'))
		i = self.addInfoLine(self._infoAList, i, 'Model Name', d.get('ModelName'))
		i = self.addInfoLine(self._infoAList, i, 'Software Version', d.get('SoftwareVersion'))
		i = self.addInfoLine(self._infoAList, i, 'Hardware Version', d.get('HardwareVersion'))

		aSysSoftware = d.get('SSW')
		if aSysSoftware is not None:
			i = self.addInfoLine(self._infoAList, i, 'Full Software Version', aSysSoftware.get('SoftwareVersion'))
			i = self.addInfoLine(self._infoAList, i, 'State', aSysSoftware.get('State'))
			i = self.addInfoLine(self._infoAList, i, 'Protocol', aSysSoftware.get('Protocol'))
			i = self.addInfoLine(self._infoAList, i, 'Current Mode', aSysSoftware.get('CurrentMode'))
			i = self.addInfoLine(self._infoAList, i, 'Pairing Time', LmTools.FmtLiveboxTimestamp(aSysSoftware.get('PairingTime')))
			i = self.addInfoLine(self._infoAList, i, 'Uplink Type', aSysSoftware.get('UplinkType'))

		i = self.addInfoLine(self._infoAList, i, 'Wifi Signal Strength', LmTools.FmtInt(d.get('SignalStrength')))
		i = self.addInfoLine(self._infoAList, i, 'Wifi Signal Noise Ratio', LmTools.FmtInt(d.get('SignalNoiseRatio')))
		
		self.endTask()



# ############# Set device name dialog #############
class SetDeviceNameDialog(QtWidgets.QDialog):
	def __init__(self, iDeviceKey, iName, iLiveboxName, iParent = None):
		super(SetDeviceNameDialog, self).__init__(iParent)
		self.resize(350, 150)

		aLabel = QtWidgets.QLabel('Names for [' + iDeviceKey + '] device:')

		self._nameCheckBox = QtWidgets.QCheckBox('Monitor Name')
		self._nameCheckBox.clicked.connect(self.nameClick)
		self._nameEdit = QtWidgets.QLineEdit()
		if iName is None:
			self._nameCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._nameEdit.setDisabled(True)
			self._currentName = ''
		else:
			self._nameCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
			self._currentName = iName
			self._nameEdit.setText(self._currentName)

		self._liveboxNameCheckBox = QtWidgets.QCheckBox('Livebox Name')
		self._liveboxNameCheckBox.clicked.connect(self.liveboxNameClick)
		self._liveboxNameEdit = QtWidgets.QLineEdit()
		if iLiveboxName is None:
			self._liveboxNameCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._liveboxNameEdit.setDisabled(True)
			self._currentLiveboxName = ''
		else:
			self._liveboxNameCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
			self._currentLiveboxName = iLiveboxName
			self._liveboxNameEdit.setText(self._currentLiveboxName)

		aNameGrid = QtWidgets.QGridLayout()
		aNameGrid.setSpacing(10)
		aNameGrid.addWidget(self._nameCheckBox, 1, 0)
		aNameGrid.addWidget(self._nameEdit, 1, 1)
		aNameGrid.addWidget(self._liveboxNameCheckBox, 2, 0)
		aNameGrid.addWidget(self._liveboxNameEdit, 2, 1)

		aOKButton = QtWidgets.QPushButton('OK')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton('Cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(aOKButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(aLabel, 0)
		aVBox.addLayout(aNameGrid, 0)
		aVBox.addLayout(aHBox, 1)

		self.setWindowTitle('Assign device names')
		self.setModal(True)
		self.show()


	def nameClick(self):
		if (self._nameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			self._nameEdit.setDisabled(False)
			self._nameEdit.setText(self._currentName)
		else:
			self._nameEdit.setDisabled(True)
			self._nameEdit.setText('')


	def liveboxNameClick(self):
		if (self._liveboxNameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			self._liveboxNameEdit.setDisabled(False)
			self._liveboxNameEdit.setText(self._currentLiveboxName)
		else:
			self._liveboxNameEdit.setDisabled(True)
			self._liveboxNameEdit.setText('')


	def getName(self):
		if (self._nameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			return self._nameEdit.text()
		return None


	def getLiveboxName(self):
		if (self._liveboxNameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			return self._liveboxNameEdit.text()
		return None



# ############# Set device type dialog #############
class SetDeviceTypeDialog(QtWidgets.QDialog):
	def __init__(self, iDeviceKey, iDeviceTypeKey, iParent = None):
		super(SetDeviceTypeDialog, self).__init__(iParent)
		self.resize(320, 170)

		self._ignoreSignal = False

		aLabel = QtWidgets.QLabel('Type for [' + iDeviceKey + '] device:')

		self._typeNameCombo = QtWidgets.QComboBox()
		self._typeNameCombo.setIconSize(QtCore.QSize(45, 45))

		i = 0
		for d in LmConfig.DEVICE_TYPES:
			self._typeNameCombo.addItem(d['Name'])
			self._typeNameCombo.setItemIcon(i, QtGui.QIcon(d['PixMap']))
			i += 1
		self._typeNameCombo.activated.connect(self.typeNameSelected)

		self._typeKeyEdit = QtWidgets.QLineEdit()
		self._typeKeyEdit.textChanged.connect(self.typeKeyTyped)
		self._typeKeyEdit.setText(iDeviceTypeKey)

		aOKButton = QtWidgets.QPushButton('OK')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton('Cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(aOKButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(aLabel, 0)
		aVBox.addWidget(self._typeNameCombo, 0)
		aVBox.addWidget(self._typeKeyEdit, 0)
		aVBox.addLayout(aHBox, 1)

		self.setWindowTitle('Assign a device type')
		self.setModal(True)
		self.show()


	def getTypeKey(self):
		return self._typeKeyEdit.text()


	def typeNameSelected(self, aIndex):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			self._typeKeyEdit.setText(LmConfig.DEVICE_TYPES[aIndex]['Key'])
			self._ignoreSignal = False


	def typeKeyTyped(self, aTypeKey):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			i = 0
			aFound = False
			for d in LmConfig.DEVICE_TYPES:
				if d['Key'] == aTypeKey:
					aFound = True
					break
				i += 1
			if not aFound:
				i = 0
			self._typeNameCombo.setCurrentIndex(i)
			self._ignoreSignal = False
