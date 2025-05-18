### Livebox Monitor device info tab module ###

import requests
import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.tabs.LmDeviceListTab import DSelCol
from LiveboxMonitor.tabs.LmInfoTab import InfoCol
from LiveboxMonitor.lang.LmLanguages import (get_device_info_label as lx,
											 get_device_info_message as mx,
											 get_device_name_label as lnx,
											 get_device_type_label as ltx)


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
		self._infoDList = LmTableWidget(objectName = 'infoDList')
		self._infoDList.set_columns({DSelCol.Key: ['Key', 0, None],
									 DSelCol.Name: [lx('Name'), 200, 'dlist_Name'],
									 DSelCol.MAC: [lx('MAC'), 120, 'dlist_MAC']})
		self._infoDList.set_header_resize([DSelCol.MAC])
		self._infoDList.set_standard_setup(self)
		self._infoDList.setMinimumWidth(350)
		self._infoDList.itemSelectionChanged.connect(self.infoDeviceListClick)

		# Attribute list
		self._infoAList = LmTableWidget(objectName = 'infoAList')
		self._infoAList.set_columns({InfoCol.Attribute: [lx('Attribute'), 200, 'alist_Attribute'],
									 InfoCol.Value: [lx('Value'), 600, 'alist_Value']})
		self._infoAList.set_header_resize([InfoCol.Value])
		self._infoAList.set_standard_setup(self, allow_sel=False, allow_sort=False)

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
		aWolButton = QtWidgets.QPushButton(lx('WakeOnLAN'), objectName = 'wol')
		aWolButton.clicked.connect(self.wolButtonClick)
		aButtonsBox.addWidget(aWolButton)
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

		LmConfig.set_tooltips(self._deviceInfoTab, 'dinfo')
		self._tabWidget.addTab(self._deviceInfoTab, lx('Device Infos'))

		# Init context
		self.initDeviceContext()


	### Init selected device context
	def initDeviceContext(self):
		self._currentDeviceLiveboxName = None
		self._currentDeviceDnsName = None
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
			aName = LmConf.MacAddrTable.get(aKey)

			aSetDeviceNameDialog = SetDeviceNameDialog(aKey, aName, self._currentDeviceLiveboxName, self._currentDeviceDnsName, self)
			if (aSetDeviceNameDialog.exec()):
				aName = aSetDeviceNameDialog.getName()
				if aName is None:
					self.delDeviceName(aKey)
				else:
					self.setDeviceName(aKey, aName)

				aName = aSetDeviceNameDialog.getLiveboxName()
				if aName is None:
					aLbSuccess = self.delDeviceLiveboxName(aKey, False)
				else:
					aLbSuccess = self.setDeviceLiveboxName(aKey, aName, False)

				aName = aSetDeviceNameDialog.getDnsName()
				if aName is None:
					if self._currentDeviceDnsName is not None:
						aDnsSuccess = self.delDeviceLiveboxName(aKey, True)
				else:
					aDnsSuccess = self.setDeviceLiveboxName(aKey, aName, True)
		else:
			self.display_error(mx('Please select a device.', 'devSelect'))


	### Refresh device info if the passed key is the selected one
	def refreshDeviceIfSelected(self, iDeviceKey):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aSelectedKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			if (aSelectedKey == iDeviceKey):
				self.infoDeviceListClick()


	### Set a device name stored in the the MacAddr table
	def setDeviceName(self, iDeviceKey, iDeviceName):
		aCurrentName = LmConf.MacAddrTable.get(iDeviceKey)
		if aCurrentName != iDeviceName:
			LmConf.MacAddrTable[iDeviceKey] = iDeviceName
			LmConf.save_mac_addr_table()
			self.updateDeviceName(iDeviceKey)


	### Delete a device name from the MacAddr table
	def delDeviceName(self, iDeviceKey):
		try:
			del LmConf.MacAddrTable[iDeviceKey]
		except:
			pass
		else:
			LmConf.save_mac_addr_table()
			self.updateDeviceName(iDeviceKey)


	### Set a device name for Livebox
	def setDeviceLiveboxName(self, iDeviceKey, iDeviceName, iDns):
		p = {}
		p['name'] = iDeviceName
		if iDns:
			p['source'] = 'dns'
			t = 'DNS'
		else:
			t = 'Livebox'
		try:
			aReply = self._session.request('Devices.Device.' + iDeviceKey, 'setName', p)
			if (aReply is not None) and (aReply.get('status', False)):
				return True
			else:
				self.display_error('Set {} name query failed.'.format(t))
		except BaseException as e:
			LmTools.error(str(e))
			self.display_error('Set {} name query error.'.format(t))
		return False


	### Delete a device name from the Livebox
	def delDeviceLiveboxName(self, iDeviceKey, iDns):
		if iDns:
			s = 'dns'
			t = 'DNS'
		else:
			s = 'webui'
			t = 'Livebox'
		try:
			aReply = self._session.request('Devices.Device.' + iDeviceKey, 'removeName', { 'source': s })
			if (aReply is not None) and (aReply.get('status', False)):
				return True
			else:
				self.display_error('Remove {} name query failed.'.format(t))
		except BaseException as e:
			LmTools.error(str(e))
			self.display_error('Remove {} name query error.'.format(t))
		return False


	### Click on assign device type button
	def assignTypeButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()

			self._task.start(lx('Loading device icons...'))
			LmConf.load_device_icons(self._liveboxSoftwareVersion)
			self._task.end()

			aSetDeviceTypeDialog = SetDeviceTypeDialog(aKey, self._currentDeviceType, self)
			if (aSetDeviceTypeDialog.exec()):
				aType = aSetDeviceTypeDialog.getTypeKey()
				try:
					aReply = self._session.request('Devices.Device.' + aKey, 'setType', { 'type': aType })
					if (aReply is not None) and (aReply.get('status', False)):
						self.infoDeviceListClick()
						self._currentDeviceType = aType		# LB device type update is async and refresh screen might be too fast
					else:
						self.display_error('Set type query failed.')
				except BaseException as e:
					LmTools.error(str(e))
					self.display_error('Set type query error.')
		else:
			self.display_error(mx('Please select a device.', 'devSelect'))


	### Click on WakeOnLAN button
	def wolButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			try:
				aReply = self._session.request('WOL', 'sendWakeOnLan', { 'hostID': aKey, 'broadcast': True })
				if (aReply is not None) and ('status' in aReply):
					self.display_status(mx('Wake on LAN signal sent to device [{}].', 'devWOL').format(aKey))
				else:
					self.display_error('WOL query failed.')
			except BaseException as e:
				LmTools.error(str(e))
				self.display_error('WOL query error.')
		else:
			self.display_error(mx('Please select a device.', 'devSelect'))


	### Click on forget device button
	def forgetButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()
			if self.ask_question(mx('Are you sure you want to forget device [{}]?', 'devForget').format(aKey)):
				try:
					aReply = self._session.request('Devices', 'destroyDevice', { 'key': aKey })
					if (aReply is not None) and (aReply.get('status', False)):
						self._infoDList.setCurrentCell(-1, -1)
						# Call event handler directly - in some (unknown) cases, the event is not raised
						self.processDeviceDeletedEvent(aKey)
					else:
						self.display_error('Destroy device query failed.')
				except BaseException as e:
					LmTools.error(str(e))
					self.display_error('Destroy device query error.')
		else:
			self.display_error(mx('Please select a device.', 'devSelect'))


	### Click on block device button
	def blockDeviceButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()

			# First get current schedule
			try:
				aReply = self._session.request('Scheduler', 'getSchedule', { 'type': 'ToD', 'ID': aKey })
				if (aReply is None) or (aReply.get('status') is None):
					self.display_error('Scheduler:getSchedule query failed.')
					return
				aHasSchedule = aReply.get('status', False)
			except BaseException as e:
				LmTools.error(str(e))
				self.display_error('Scheduler:getSchedule query error.')
				return

			# If has schedule override it, otherwise add it
			if aHasSchedule:
				try:
					aReply = self._session.request('Scheduler', 'overrideSchedule', { 'type': 'ToD', 'ID': aKey, 'override': 'Disable' })
					if (aReply is not None) and (aReply.get('status', False)):
						self.display_status(mx('Device [{}] now blocked.', 'devBlocked').format(aKey))
					else:
						LmTools.error(aReply)
						self.display_error('Block query failed.')
				except BaseException as e:
					LmTools.error(str(e))
					self.display_error('Block query error.')
			else:
				try:
					aInfos = {}
					aInfos['base'] = 'Weekly'
					aInfos['def'] = 'Enable'
					aInfos['ID'] = aKey
					aInfos['schedule'] = []
					aInfos['enable'] = True
					aInfos['override'] = 'Disable'
					aReply = self._session.request('Scheduler', 'addSchedule', { 'type': 'ToD', 'info': aInfos })
					if (aReply is not None) and (aReply.get('status', False)):
						self.display_status(mx('Device [{}] now blocked.', 'devBlocked').format(aKey))
					else:
						LmTools.error(aReply)
						self.display_error('Block query failed.')
				except BaseException as e:
					LmTools.error(str(e))
					self.display_error('Block query error.')
		else:
			self.display_error(mx('Please select a device.', 'devSelect'))


	### Click on unblock device button
	def unblockDeviceButtonClick(self):
		aCurrentSelection = self._infoDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._infoDList.item(aCurrentSelection, DSelCol.Key).text()

			# First get current schedule
			try:
				aReply = self._session.request('Scheduler', 'getSchedule', { 'type': 'ToD', 'ID': aKey })
				if (aReply is None) or (aReply.get('status') is None):
					self.display_error('Scheduler:getSchedule query failed.')
					return
				aHasSchedule = aReply.get('status', False)
			except BaseException as e:
				LmTools.error(str(e))
				self.display_error('Scheduler:getSchedule query error.')
				return

			# If has schedule override it, otherwise no need to unlock
			if aHasSchedule:
				try:
					aReply = self._session.request('Scheduler', 'overrideSchedule', { 'type': 'ToD', 'ID': aKey, 'override': 'Enable' })
					if (aReply is not None) and (aReply.get('status', False)):
						self.display_status(mx('Device [{}] now unblocked.', 'devUnblocked').format(aKey))
					else:
						self.display_error('Unblock query failed.')
				except BaseException as e:
					LmTools.error(str(e))
					self.display_error('Unblock query error.')
			else:
				self.display_status(mx('Device [{}] is not blocked.', 'devNotBlocked').format(aKey))
		else:
			self.display_error(mx('Please select a device.', 'devSelect'))


	### Update device infos list
	def updateDeviceInfo(self, iDeviceKey):
		self._task.start(lx('Getting device information...'))

		try:
			d = self._session.request('Devices.Device.' + iDeviceKey, 'get')
		except BaseException as e:
			LmTools.error(str(e))
			d = None
		if (d is not None):
			d = d.get('status')
		if (d is None):
			self._task.end()
			self.display_error(mx('Error getting device information.', 'devInfoErr'))
			return

		i = 0
		i = self.addInfoLine(self._infoAList, i, lx('Key'), iDeviceKey)
		i = self.addInfoLine(self._infoAList, i, lx('Active'), LmTools.fmt_bool(d.get('Active')))
		i = self.addInfoLine(self._infoAList, i, lx('Authenticated'), LmTools.fmt_bool(d.get('AuthenticationState')))

		try:
			aData = self._session.request('Scheduler', 'getSchedule', { 'type': 'ToD', 'ID': iDeviceKey })
			aBlocked = False
			if (aData is not None):
				aData = aData.get('data')
			if (aData is not None):
				aData = aData.get('scheduleInfo')
			if (aData is not None):
				aBlocked = (aData.get('override', '') == 'Disable') and (aData.get('value', '') == 'Disable')
			i = self.addInfoLine(self._infoAList, i, lx('Blocked'), LmTools.fmt_bool(aBlocked))
		except BaseException as e:
			LmTools.error(str(e))
			i = self.addInfoLine(self._infoAList, i, lx('Blocked'), 'Scheduler:getSchedule query error', LmTools.ValQual.Error)

		i = self.addInfoLine(self._infoAList, i, lx('First connection'), LmTools.fmt_livebox_timestamp(d.get('FirstSeen')))
		i = self.addInfoLine(self._infoAList, i, lx('Last connection'), LmTools.fmt_livebox_timestamp(d.get('LastConnection')))
		i = self.addInfoLine(self._infoAList, i, lx('Last changed'), LmTools.fmt_livebox_timestamp(d.get('LastChanged')))
		i = self.addInfoLine(self._infoAList, i, lx('Source'), d.get('DiscoverySource'))

		self._currentDeviceLiveboxName = d.get('Name')
		i = self.addInfoLine(self._infoAList, i, lx('Livebox Name'), self._currentDeviceLiveboxName)

		self._currentDeviceDnsName = None
		aNameList = d.get('Names', [])
		if len(aNameList):
			for aName in aNameList:
				aNameStr = aName.get('Name', '')
				aSource = aName.get('Source', '')
				if aSource == 'dns':
					self._currentDeviceDnsName = aNameStr
				i = self.addInfoLine(self._infoAList, i, lx('Name'), aNameStr + ' (' + aSource + ')')
		
		aDNSList = d.get('mDNSService', [])
		if len(aDNSList):
			for aDNSName in aDNSList:
				i = self.addInfoLine(self._infoAList, i, lx('DNS Name'), aDNSName.get('Name', '') + ' (' + aDNSName.get('ServiceName', '') + ')')

		self._currentDeviceType = d.get('DeviceType', '')

		aTypeList = d.get('DeviceTypes', [])
		if len(aTypeList):
			for aType in aTypeList:
				i = self.addInfoLine(self._infoAList, i, lx('Type'), aType.get('Type', '') + ' (' + aType.get('Source', '') + ')')

		aActiveIPStruct = LmTools.determine_ip(d)
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
				LmTools.error(str(e))
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
			i = self.addInfoLine(self._infoAList, i, lx('Pairing Time'), LmTools.fmt_livebox_timestamp(aSysSoftware.get('PairingTime')))
			i = self.addInfoLine(self._infoAList, i, lx('Uplink Type'), aSysSoftware.get('UplinkType'))

		aSignalStrength = LmTools.fmt_int(d.get('SignalStrength'))
		if len(aSignalStrength):
			aSignalStrength += ' dBm'
		i = self.addInfoLine(self._infoAList, i, lx('Wifi Signal Strength'), aSignalStrength)
		i = self.addInfoLine(self._infoAList, i, lx('Wifi Signal Noise Ratio'), LmTools.fmt_int(d.get('SignalNoiseRatio')))
		i = self.addInfoLine(self._infoAList, i, lx('Encryption Mode'), d.get('EncryptionMode'))
		i = self.addInfoLine(self._infoAList, i, lx('Security Mode'), d.get('SecurityModeEnabled'))
		i = self.addInfoLine(self._infoAList, i, lx('Link Bandwidth'), d.get('LinkBandwidth'))
		i = self.addInfoLine(self._infoAList, i, lx('Operating Standard'), d.get('OperatingStandard'))
		i = self.addInfoLine(self._infoAList, i, lx('Operating Band'), d.get('OperatingFrequencyBand'))


		aSysSoftwareStd = d.get('SSWSta')
		if aSysSoftwareStd is not None:
			i = self.addInfoLine(self._infoAList, i, lx('Supported Standards'), aSysSoftwareStd.get('SupportedStandards'))
			i = self.addInfoLine(self._infoAList, i, lx('Supports 2.4GHz'), LmTools.fmt_bool(aSysSoftwareStd.get('Supports24GHz')))
			i = self.addInfoLine(self._infoAList, i, lx('Supports 5GHz'), LmTools.fmt_bool(aSysSoftwareStd.get('Supports5GHz')))
			i = self.addInfoLine(self._infoAList, i, lx('Supports 6GHz'), LmTools.fmt_bool(aSysSoftwareStd.get('Supports6GHz')))

		self._task.end()



# ############# Set device name dialog #############
class SetDeviceNameDialog(QtWidgets.QDialog):
	def __init__(self, iDeviceKey, iName, iLiveboxName, iDnsName, iParent = None):
		super(SetDeviceNameDialog, self).__init__(iParent)
		self.resize(350, 200)

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

		self._dnsNameCheckBox = QtWidgets.QCheckBox(lnx('DNS Name'), objectName = 'dnsNameCheckBox')
		self._dnsNameCheckBox.clicked.connect(self.dnsNameClick)
		self._dnsNameEdit = QtWidgets.QLineEdit(objectName = 'dnsNameEdit')
		if iDnsName is None:
			self._dnsNameCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._dnsNameEdit.setDisabled(True)
			self._currentDnsName = ''
		else:
			self._dnsNameCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
			self._currentDnsName = iDnsName
			self._dnsNameEdit.setText(self._currentDnsName)

		aNameGrid = QtWidgets.QGridLayout()
		aNameGrid.setSpacing(10)
		aNameGrid.addWidget(self._nameCheckBox, 0, 0)
		aNameGrid.addWidget(self._nameEdit, 0, 1)
		aNameGrid.addWidget(self._liveboxNameCheckBox, 1, 0)
		aNameGrid.addWidget(self._liveboxNameEdit, 1, 1)
		aNameGrid.addWidget(self._dnsNameCheckBox, 2, 0)
		aNameGrid.addWidget(self._dnsNameEdit, 2, 1)

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
		aVBox.setSpacing(20)
		aVBox.addWidget(aLabel, 0)
		aVBox.addLayout(aNameGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.set_tooltips(self, 'dname')

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


	def dnsNameClick(self):
		if (self._dnsNameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			self._dnsNameEdit.setDisabled(False)
			self._dnsNameEdit.setText(self._currentDnsName)
		else:
			self._dnsNameEdit.setDisabled(True)
			self._dnsNameEdit.setText('')


	def getName(self):
		if (self._nameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			return self._nameEdit.text()
		return None


	def getLiveboxName(self):
		if (self._liveboxNameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			return self._liveboxNameEdit.text()
		return None


	def getDnsName(self):
		if (self._dnsNameCheckBox.checkState() == QtCore.Qt.CheckState.Checked):
			return self._dnsNameEdit.text()
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

		LmConfig.set_tooltips(self, 'dtype')

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
