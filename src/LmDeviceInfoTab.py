### Livebox Monitor device info tab module ###

import requests
import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from src import LmTools, LmConfig
from src.LmConfig import LmConf
from src.LmDeviceListTab import DSelCol
from src.LmInfoTab import InfoCol
from src.LmLanguages import (GetDeviceInfoLabel as lx,
							 GetDeviceNameDialogLabel as lnx,
							 GetDeviceTypeDialogLabel as ltx)


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'deviceInfoTab'

# Static Config
MACADDR_URL = 'https://api.macaddress.io/v1?apiKey={0}&output=json&search={1}'



# ################################ LmDeviceInfo class ################################
class LmDeviceInfo:

	### Create device info tab
	def createDeviceInfoTab(self):
		self._deviceInfoTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# Device list
		self._infoDList = QtWidgets.QTableWidget(objectName = 'infoDList')
		self._infoDList.setColumnCount(DSelCol.Count)
		self._infoDList.setHorizontalHeaderLabels(('Key', lx('Name'), lx('MAC')))
		self._infoDList.setColumnHidden(DSelCol.Key, True)
		aHeader = self._infoDList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(DSelCol.MAC, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(DSelCol.Name, QtCore.Qt.Orientation.Horizontal, 'dlist_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DSelCol.MAC, QtCore.Qt.Orientation.Horizontal, 'dlist_MAC', QtCore.Qt.ItemDataRole.UserRole)
		self._infoDList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._infoDList.setColumnWidth(DSelCol.Name, 200)
		self._infoDList.setColumnWidth(DSelCol.MAC, 120)
		self._infoDList.verticalHeader().hide()
		self._infoDList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._infoDList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._infoDList.setSortingEnabled(True)
		self._infoDList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._infoDList.setMinimumWidth(350)
		self._infoDList.itemSelectionChanged.connect(self.infoDeviceListClick)
		LmConfig.SetTableStyle(self._infoDList)

		# Attribute list
		self._infoAList = QtWidgets.QTableWidget(objectName = 'infoAList')
		self._infoAList.setColumnCount(InfoCol.Count)
		self._infoAList.setHorizontalHeaderLabels((lx('Attribute'), lx('Value')))
		aHeader = self._infoAList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(InfoCol.Value, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(InfoCol.Attribute, QtCore.Qt.Orientation.Horizontal, 'alist_Attribute', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(InfoCol.Value, QtCore.Qt.Orientation.Horizontal, 'alist_Value', QtCore.Qt.ItemDataRole.UserRole)
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
		aRefreshDeviceInfoButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refresh')
		aRefreshDeviceInfoButton.clicked.connect(self.refreshDeviceInfoButtonClick)
		aButtonsBox.addWidget(aRefreshDeviceInfoButton)
		aAssignNameButton = QtWidgets.QPushButton(lx('Assign Name...'), objectName = 'assignName')
		aAssignNameButton.clicked.connect(self.assignNameButtonClick)
		aButtonsBox.addWidget(aAssignNameButton)
		aAssignTypeButton = QtWidgets.QPushButton(lx('Assign Type...'), objectName = 'assignType')
		aAssignTypeButton.clicked.connect(self.assignTypeButtonClick)
		aButtonsBox.addWidget(aAssignTypeButton)
		aForgetButton = QtWidgets.QPushButton(lx('Forget...'), objectName = 'forget')
		aForgetButton.clicked.connect(self.forgetButtonClick)
		aButtonsBox.addWidget(aForgetButton)
		aBlockDeviceButton = QtWidgets.QPushButton(lx('Block'), objectName = 'block')
		aBlockDeviceButton.clicked.connect(self.blockDeviceButtonClick)
		aButtonsBox.addWidget(aBlockDeviceButton)
		aUnblockDeviceButton = QtWidgets.QPushButton(lx('Unblock'), objectName = 'unblock')
		aUnblockDeviceButton.clicked.connect(self.unblockDeviceButtonClick)
		aButtonsBox.addWidget(aUnblockDeviceButton)

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addLayout(aListBox, 0)
		aVBox.addLayout(aButtonsBox, 1)
		self._deviceInfoTab.setLayout(aVBox)

		LmConfig.SetToolTips(self._deviceInfoTab, 'dinfo')
		self._tabWidget.addTab(self._deviceInfoTab, lx('Device Infos'))

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
			self.displayError('Please select a device.')


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
				return True
			else:
				self.displayError('Set Livebox name query failed.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Set Livebox name query error.')
		return False


	### Delete a device name from the Livebox
	def delDeviceLiveboxName(self, iDeviceKey):
		try:
			aReply = self._session.request('Devices.Device.' + iDeviceKey + ':removeName', { 'source': 'webui' })
			if (aReply is not None) and (aReply.get('status', False)):
				return True
			else:
				self.displayError('Remove Livebox name query failed.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Remove Livebox name query error.')
		return False


	### Click on assign device type button
	def assignTypeButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()

			self.startTask(lx('Loading device icons...'))
			LmConf.loadDeviceIcons()
			self.endTask()

			aSetDeviceTypeDialog = SetDeviceTypeDialog(aKey, self._currentDeviceType, self)
			if (aSetDeviceTypeDialog.exec()):
				aType = aSetDeviceTypeDialog.getTypeKey()
				try:
					aReply = self._session.request('Devices.Device.' + aKey + ':setType', { 'type': aType })
					if (aReply is not None) and (aReply.get('status', False)):
						self.infoDeviceListClick()
					else:
						self.displayError('Set type query failed.')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Set type query error.')
		else:
			self.displayError('Please select a device.')


	### Click on forget device button
	def forgetButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			if self.askQuestion('Are you sure you want to forget device [' + aKey + ']?'):
				try:
					aReply = self._session.request('Devices:destroyDevice', { 'key': aKey })
					if (aReply is not None) and (aReply.get('status', False)):
						self._infoDList.setCurrentCell(-1, -1)
						# Call event handler directly - in some (unknown) cases, the event is not raised
						self.processDeviceDeletedEvent(aKey)
					else:
						self.displayError('Destroy device query failed.')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Destroy device query error.')
		else:
			self.displayError('Please select a device.')


	### Click on block device button
	def blockDeviceButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()

			# First get current schedule
			try:
				aReply = self._session.request('Scheduler:getSchedule', { 'type': 'ToD', 'ID': aKey })
				if (aReply is None) or (aReply.get('status') is None):
					self.displayError('Scheduler:getSchedule query failed.')
					return
				aHasSchedule = aReply.get('status', False)
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Scheduler:getSchedule query error.')
				return

			# If has schedule override it, otherwise add it
			if aHasSchedule:
				try:
					aReply = self._session.request('Scheduler:overrideSchedule', { 'type': 'ToD', 'ID': aKey, 'override': 'Disable' })
					if (aReply is not None) and (aReply.get('status', False)):
						self.displayStatus('Device ' + aKey + ' now blocked.')
					else:
						LmTools.Error('Error: {}'.format(aReply))
						self.displayError('Block query failed.')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Block query error.')
			else:
				try:
					aInfos = {}
					aInfos['base'] = 'Weekly'
					aInfos['def'] = 'Enable'
					aInfos['ID'] = aKey
					aInfos['schedule'] = []
					aInfos['enable'] = True
					aInfos['override'] = 'Disable'
					aReply = self._session.request('Scheduler:addSchedule', { 'type': 'ToD', 'info': aInfos })
					if (aReply is not None) and (aReply.get('status', False)):
						self.displayStatus('Device ' + aKey + ' now blocked.')
					else:
						LmTools.Error('Error: {}'.format(aReply))
						self.displayError('Block query failed.')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Block query error.')
		else:
			self.displayError('Please select a device.')


	### Click on unblock device button
	def unblockDeviceButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()

			# First get current schedule
			try:
				aReply = self._session.request('Scheduler:getSchedule', { 'type': 'ToD', 'ID': aKey })
				if (aReply is None) or (aReply.get('status') is None):
					self.displayError('Scheduler:getSchedule query failed.')
					return
				aHasSchedule = aReply.get('status', False)
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Scheduler:getSchedule query error.')
				return

			# If has schedule override it, otherwise no need to unlock
			if aHasSchedule:
				try:
					aReply = self._session.request('Scheduler:overrideSchedule', { 'type': 'ToD', 'ID': aKey, 'override': 'Enable' })
					if (aReply is not None) and (aReply.get('status', False)):
						self.displayStatus('Device ' + aKey + ' now unblocked.')
					else:
						self.displayError('Unblock query failed.')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Unblock query error.')
			else:
				self.displayStatus('Device ' + aKey + ' is not blocked.')
		else:
			self.displayError('Please select a device.')


	### Update device infos list
	def updateDeviceInfo(self, iDeviceKey):
		self.startTask(lx('Getting device information...'))

		try:
			d = self._session.request('Devices.Device.' + iDeviceKey + ':get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if (d is not None):
			d = d.get('status')
		if (d is None):
			self.endTask()
			self.displayError('Error getting device information.')
			return

		i = 0
		i = self.addInfoLine(self._infoAList, i, lx('Key'), iDeviceKey)
		i = self.addInfoLine(self._infoAList, i, lx('Active'), LmTools.FmtBool(d.get('Active')))
		i = self.addInfoLine(self._infoAList, i, lx('Authenticated'), LmTools.FmtBool(d.get('AuthenticationState')))

		try:
			aData = self._session.request('Scheduler:getSchedule', { 'type': 'ToD', 'ID': iDeviceKey })
			aBlocked = False
			if (aData is not None):
				aData = aData.get('data')
			if (aData is not None):
				aData = aData.get('scheduleInfo')
			if (aData is not None):
				aBlocked = (aData.get('override', '') == 'Disable') and (aData.get('value', '') == 'Disable')
			i = self.addInfoLine(self._infoAList, i, lx('Blocked'), LmTools.FmtBool(aBlocked))
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			i = self.addInfoLine(self._infoAList, i, lx('Blocked'), 'Scheduler:getSchedule query error', LmTools.ValQual.Error)

		i = self.addInfoLine(self._infoAList, i, lx('First connection'), LmTools.FmtLiveboxTimestamp(d.get('FirstSeen')))
		i = self.addInfoLine(self._infoAList, i, lx('Last connection'), LmTools.FmtLiveboxTimestamp(d.get('LastConnection')))
		i = self.addInfoLine(self._infoAList, i, lx('Last changed'), LmTools.FmtLiveboxTimestamp(d.get('LastChanged')))
		i = self.addInfoLine(self._infoAList, i, lx('Source'), d.get('DiscoverySource'))

		self._currentDeviceLiveboxName = d.get('Name', None)
		i = self.addInfoLine(self._infoAList, i, lx('Livebox Name'), self._currentDeviceLiveboxName)

		aNameList = d.get('Names', [])
		if len(aNameList):
			for aName in aNameList:
				i = self.addInfoLine(self._infoAList, i, lx('Name'), aName.get('Name', '') + ' (' + aName.get('Source', '') + ')')
		
		aDNSList = d.get('mDNSService', [])
		if len(aDNSList):
			for aDNSName in aDNSList:
				i = self.addInfoLine(self._infoAList, i, lx('DNS Name'), aDNSName.get('Name', '') + ' (' + aDNSName.get('ServiceName', '') + ')')

		self._currentDeviceType = d.get('DeviceType', '')

		aTypeList = d.get('DeviceTypes', [])
		if len(aTypeList):
			for aType in aTypeList:
				i = self.addInfoLine(self._infoAList, i, lx('Type'), aType.get('Type', '') + ' (' + aType.get('Source', '') + ')')

		aActiveIPStruct = LmTools.DetermineIP(d)
		if aActiveIPStruct is not None:
			aActiveIP = aActiveIPStruct.get('Address', '')
		else:
			aActiveIP = ''
		aIPv4List = d.get('IPv4Address', [])
		if len(aIPv4List):
			for aIPV4 in aIPv4List:
				aIP = aIPV4.get('Address', '')
				s = aIP + ' ('
				if (len(aActiveIP) > 0) and (aActiveIP == aIP):
					s += 'active, '
				s += aIPV4.get('Status', '') + ')'

				if aIPV4.get('Reserved', False):
					s += ' - Reserved'
				i = self.addInfoLine(self._infoAList, i, lx('IPv4 Address'), s)

		aIPv6List = d.get('IPv6Address', [])
		if len(aIPv6List):
			for aIPV6 in aIPv6List:
				i = self.addInfoLine(self._infoAList, i, lx('IPv6 Address'), aIPV6.get('Address', '') +
																			 ' [' + aIPV6.get('Scope', '') + ']' +
																			 ' (' + aIPV6.get('Status', '') + ')')

		aMacAddr = d.get('PhysAddress', '')
		if len(aMacAddr) == 0:
			aMacAddr = iDeviceKey
		aManufacturer = ''
		if (len(LmConf.MacAddrApiKey)) and (len(aMacAddr)):
			try:
				aData = requests.get(MACADDR_URL.format(LmConf.MacAddrApiKey, aMacAddr), timeout = 2)
				aData = json.loads(aData.content)
				aCompDetails = aData.get('vendorDetails')
				if aCompDetails is not None:
					aManufacturer = aCompDetails.get('companyName', '') + ' - ' + aCompDetails.get('countryCode', '')
				i = self.addInfoLine(self._infoAList, i, lx('Manufacturer'), aManufacturer)
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				i = self.addInfoLine(self._infoAList, i, lx('Manufacturer'), 'Web query error', LmTools.ValQual.Error)

		i = self.addInfoLine(self._infoAList, i, lx('Vendor ID'), d.get('VendorClassID'))
		i = self.addInfoLine(self._infoAList, i, lx('Serial Number'), d.get('SerialNumber'))
		i = self.addInfoLine(self._infoAList, i, lx('Product Class'), d.get('ProductClass'))
		i = self.addInfoLine(self._infoAList, i, lx('Model Name'), d.get('ModelName'))
		i = self.addInfoLine(self._infoAList, i, lx('Software Version'), d.get('SoftwareVersion'))
		i = self.addInfoLine(self._infoAList, i, lx('Hardware Version'), d.get('HardwareVersion'))
		i = self.addInfoLine(self._infoAList, i, lx('DHCP Option 55'), d.get('DHCPOption55'))

		aSysSoftware = d.get('SSW')
		if aSysSoftware is not None:
			i = self.addInfoLine(self._infoAList, i, lx('Full Software Version'), aSysSoftware.get('SoftwareVersion'))
			i = self.addInfoLine(self._infoAList, i, lx('State'), aSysSoftware.get('State'))
			i = self.addInfoLine(self._infoAList, i, lx('Protocol'), aSysSoftware.get('Protocol'))
			i = self.addInfoLine(self._infoAList, i, lx('Current Mode'), aSysSoftware.get('CurrentMode'))
			i = self.addInfoLine(self._infoAList, i, lx('Pairing Time'), LmTools.FmtLiveboxTimestamp(aSysSoftware.get('PairingTime')))
			i = self.addInfoLine(self._infoAList, i, lx('Uplink Type'), aSysSoftware.get('UplinkType'))

		i = self.addInfoLine(self._infoAList, i, lx('Wifi Signal Strength'), LmTools.FmtInt(d.get('SignalStrength')))
		i = self.addInfoLine(self._infoAList, i, lx('Wifi Signal Noise Ratio'), LmTools.FmtInt(d.get('SignalNoiseRatio')))

		aSysSoftwareStd = d.get('SSWSta')
		if aSysSoftwareStd is not None:
			i = self.addInfoLine(self._infoAList, i, lx('Supported Standards'), aSysSoftwareStd.get('SupportedStandards'))
			i = self.addInfoLine(self._infoAList, i, lx('Supports 2.4GHz'), LmTools.FmtBool(aSysSoftwareStd.get('Supports24GHz')))
			i = self.addInfoLine(self._infoAList, i, lx('Supports 5GHz'), LmTools.FmtBool(aSysSoftwareStd.get('Supports5GHz')))
			i = self.addInfoLine(self._infoAList, i, lx('Supports 6GHz'), LmTools.FmtBool(aSysSoftwareStd.get('Supports6GHz')))

		self.endTask()



# ############# Set device name dialog #############
class SetDeviceNameDialog(QtWidgets.QDialog):
	def __init__(self, iDeviceKey, iName, iLiveboxName, iParent = None):
		super(SetDeviceNameDialog, self).__init__(iParent)
		self.resize(350, 150)

		aLabel = QtWidgets.QLabel(lnx('Names for [{}] device:').format(iDeviceKey), objectName = 'mainLabel')

		self._nameCheckBox = QtWidgets.QCheckBox(lnx('Local Name'), objectName = 'nameCheckBox')
		self._nameCheckBox.clicked.connect(self.nameClick)
		self._nameEdit = QtWidgets.QLineEdit(objectName = 'nameEdit')
		if iName is None:
			self._nameCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._nameEdit.setDisabled(True)
			self._currentName = ''
		else:
			self._nameCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
			self._currentName = iName
			self._nameEdit.setText(self._currentName)

		self._liveboxNameCheckBox = QtWidgets.QCheckBox(lnx('Livebox Name'), objectName = 'liveboxNameCheckBox')
		self._liveboxNameCheckBox.clicked.connect(self.liveboxNameClick)
		self._liveboxNameEdit = QtWidgets.QLineEdit(objectName = 'liveboxNameEdit')
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
		aNameGrid.addWidget(self._nameCheckBox, 0, 0)
		aNameGrid.addWidget(self._nameEdit, 0, 1)
		aNameGrid.addWidget(self._liveboxNameCheckBox, 1, 0)
		aNameGrid.addWidget(self._liveboxNameEdit, 1, 1)

		aOKButton = QtWidgets.QPushButton(lnx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lnx('Cancel'), objectName = 'cancel')
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

		LmConfig.SetToolTips(self, 'dname')

		self.setWindowTitle(lnx('Assign device names'))
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

		aLabel = QtWidgets.QLabel(ltx('Type for [{}] device:').format(iDeviceKey), objectName = 'mainLabel')

		self._typeNameCombo = QtWidgets.QComboBox(objectName = 'typeNameCombo')
		self._typeNameCombo.setIconSize(QtCore.QSize(45, 45))

		i = 0
		for d in LmConfig.DEVICE_TYPES:
			self._typeNameCombo.addItem(d['Name'])
			self._typeNameCombo.setItemIcon(i, QtGui.QIcon(d['PixMap']))
			i += 1
		self._typeNameCombo.activated.connect(self.typeNameSelected)

		self._typeKeyEdit = QtWidgets.QLineEdit(objectName = 'typeKeyEdit')
		self._typeKeyEdit.textChanged.connect(self.typeKeyTyped)
		self._typeKeyEdit.setText(iDeviceTypeKey)

		aOKButton = QtWidgets.QPushButton(ltx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(ltx('Cancel'), objectName = 'cancel')
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

		LmConfig.SetToolTips(self, 'dtype')

		self.setWindowTitle(ltx('Assign a device type'))
		self.setModal(True)
		self.show()


	def getTypeKey(self):
		return self._typeKeyEdit.text()


	def typeNameSelected(self, iIndex):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			self._typeKeyEdit.setText(LmConfig.DEVICE_TYPES[iIndex]['Key'])
			self._ignoreSignal = False


	def typeKeyTyped(self, iTypeKey):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			i = 0
			aFound = False
			for d in LmConfig.DEVICE_TYPES:
				if d['Key'] == iTypeKey:
					aFound = True
					break
				i += 1
			if not aFound:
				i = 0
			self._typeNameCombo.setCurrentIndex(i)
			self._ignoreSignal = False
