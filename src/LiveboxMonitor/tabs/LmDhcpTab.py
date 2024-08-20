### Livebox Monitor DHCP tab module ###

from enum import IntEnum
from ipaddress import IPv4Network
from ipaddress import IPv4Address

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.tabs.LmInfoTab import InfoCol
from LiveboxMonitor.lang.LmLanguages import (GetDhcpLabel as lx,
											 GetDhcpMessage as mx,
											 GetDhcpBindingDialogLabel as lbx,
											 GetDhcpSetupDialogLabel as lsx)


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'dhcpTab'

# List columns
class DhcpCol(IntEnum):
	Key = 0		# Must be the same as DevCol.Key
	Name = 1
	Domain = 2
	MAC = 3
	IP = 4
	Count = 5


# ################################ LmDhcp class ################################
class LmDhcp:

	### Create DHCP tab
	def createDhcpTab(self):
		self._dhcpTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# DHCP binding list
		self._dhcpDList = QtWidgets.QTableWidget(objectName = 'dhcpDList')
		self._dhcpDList.setColumnCount(DhcpCol.Count)
		self._dhcpDList.setHorizontalHeaderLabels(('Key', lx('Name'), lx('Domain'), lx('MAC'), lx('IP')))
		self._dhcpDList.setColumnHidden(DhcpCol.Key, True)
		aHeader = self._dhcpDList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(DhcpCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(DhcpCol.Name, QtCore.Qt.Orientation.Horizontal, 'dlist_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DhcpCol.Domain, QtCore.Qt.Orientation.Horizontal, 'dlist_Domain', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DhcpCol.MAC, QtCore.Qt.Orientation.Horizontal, 'dlist_MAC', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DhcpCol.IP, QtCore.Qt.Orientation.Horizontal, 'dlist_IP', QtCore.Qt.ItemDataRole.UserRole)
		self._dhcpDList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._dhcpDList.setColumnWidth(DhcpCol.Name, 200)
		self._dhcpDList.setColumnWidth(DhcpCol.Domain, 60)
		self._dhcpDList.setColumnWidth(DhcpCol.MAC, 120)
		self._dhcpDList.setColumnWidth(DhcpCol.IP, 105)
		self._dhcpDList.verticalHeader().hide()
		self._dhcpDList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._dhcpDList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._dhcpDList.setSortingEnabled(True)
		self._dhcpDList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._dhcpDList.setMinimumWidth(515)
		LmConfig.SetTableStyle(self._dhcpDList)

		# DHCP binding button bar
		aBindingButtonsBox = QtWidgets.QHBoxLayout()
		aBindingButtonsBox.setSpacing(30)
		aRefreshBindingButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refreshBinding')
		aRefreshBindingButton.clicked.connect(self.refreshDhcpBindingButtonClick)
		aBindingButtonsBox.addWidget(aRefreshBindingButton)
		aAddBindingButton = QtWidgets.QPushButton(lx('Add...'), objectName = 'addBinding')
		aAddBindingButton.clicked.connect(self.addDhcpBindingButtonClick)
		aBindingButtonsBox.addWidget(aAddBindingButton)
		aDelBindingButton = QtWidgets.QPushButton(lx('Delete'), objectName = 'delBinding')
		aDelBindingButton.clicked.connect(self.delDhcpBindingButtonClick)
		aBindingButtonsBox.addWidget(aDelBindingButton)

		# DHCP binding layout
		aBindingBox = QtWidgets.QVBoxLayout()
		aBindingBox.setSpacing(10)
		aBindingBox.addWidget(self._dhcpDList, 1)
		aBindingBox.addLayout(aBindingButtonsBox, 0)

		# Attribute list
		self._dhcpAList = QtWidgets.QTableWidget(objectName = 'dhcpAList')
		self._dhcpAList.setColumnCount(InfoCol.Count)
		self._dhcpAList.setHorizontalHeaderLabels((lx('Attribute'), lx('Value')))
		aHeader = self._dhcpAList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(InfoCol.Value, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(InfoCol.Attribute, QtCore.Qt.Orientation.Horizontal, 'alist_Attribute', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(InfoCol.Value, QtCore.Qt.Orientation.Horizontal, 'alist_Value', QtCore.Qt.ItemDataRole.UserRole)
		self._dhcpAList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._dhcpAList.setColumnWidth(InfoCol.Attribute, 200)
		self._dhcpAList.setColumnWidth(InfoCol.Value, 500)
		self._dhcpAList.verticalHeader().hide()
		self._dhcpAList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._dhcpAList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._dhcpAList)

		# Attribute button bar
		aAttributeButtonsBox = QtWidgets.QHBoxLayout()
		aAttributeButtonsBox.setSpacing(30)
		aRefreshDhcpAttributeButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refreshDhcpAttribute')
		aRefreshDhcpAttributeButton.clicked.connect(self.refreshDhcpAttributeButtonClick)
		aAttributeButtonsBox.addWidget(aRefreshDhcpAttributeButton)
		aDhcpSetupButton = QtWidgets.QPushButton(lx('DHCP Setup...'), objectName = 'dhcpSetup')
		aDhcpSetupButton.clicked.connect(self.dhcpSetupButtonClick)
		aAttributeButtonsBox.addWidget(aDhcpSetupButton)

		# DHCP attribute layout
		aAttributeBox = QtWidgets.QVBoxLayout()
		aAttributeBox.setSpacing(10)
		aAttributeBox.addWidget(self._dhcpAList, 1)
		aAttributeBox.addLayout(aAttributeButtonsBox, 0)

		# Layout
		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setSpacing(10)
		aHBox.addLayout(aBindingBox, 0)
		aHBox.addWidget(aSeparator)
		aHBox.addLayout(aAttributeBox, 1)
		self._dhcpTab.setLayout(aHBox)

		LmConfig.SetToolTips(self._dhcpTab, 'dhcp')
		self._tabWidget.addTab(self._dhcpTab, lx('DHCP'))

		# Set default values
		self._homeIpServer = '192.168.1.1'
		self._homeIpStart = '192.168.1.2'
		self._homeIpMask = '255.255.255.0'
		self._guestIpServer = '192.168.144.1'
		self._guestIpStart = '192.168.144.2'
		self._guestIpMask = '255.255.255.0'

		# Init context
		self.dhcpTabInit()


	### Init DHCP tab context
	def dhcpTabInit(self):
		self._dhcpDataLoaded = False


	### Click on DHCP tab
	def dhcpTabClick(self):
		if not self._dhcpDataLoaded:
			self._dhcpDataLoaded = True		# Must be first to avoid reentrency during tab drag&drop
			self.loadDhcpInfo()			# Load first as home/guest server, start & mask must be known before DHCP bindings
			self.loadDhcpBindings()


	### Click on refresh DHCP binding button
	def refreshDhcpBindingButtonClick(self):
		self._dhcpDList.clearContents()
		self._dhcpDList.setRowCount(0)
		self.loadDhcpBindings()


	### Click on add DHCP binding button
	def addDhcpBindingButtonClick(self):
		aUsedIPs = []

		# Collecting already used IPs from DHCP bindings
		i = 0
		n = self._dhcpDList.rowCount()
		while (i < n):
			aUsedIPs.append(self._dhcpDList.item(i, DhcpCol.IP).text())
			i += 1

		# Collecting already used IPs from active device list
		aDeviceList = self.getDeviceList()
		for d in aDeviceList:
			if d['Active']:
				aUsedIPs.append(d['IP'])

		# Find appropriate IP suggestions
		aHomeIpSuggest = self.findFirstAvailableIp('Home', aUsedIPs)
		aGuestIpSuggest = self.findFirstAvailableIp('Guest', aUsedIPs)

		aAddDhcpBindingDialog = AddDhcpBindingDialog(aHomeIpSuggest, aGuestIpSuggest, self)
		if (aAddDhcpBindingDialog.exec()):
			aMAC = aAddDhcpBindingDialog.getMacAddress()
			aIP = aAddDhcpBindingDialog.getIpAddress()
			if aAddDhcpBindingDialog.getDomain() == 'Home':
				d = 'default'
			else:
				d = 'guest'
			try:
				aReply = self._session.request('DHCPv4.Server.Pool.' + d, 'addStaticLease', { 'MACAddress': aMAC, 'IPAddress': aIP })
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('DHCP binding query error.')
				return

			if (aReply is not None) and ('status' in aReply):
				aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
				if len(aErrors):
					self.displayError(aErrors)
				self.refreshDhcpBindingButtonClick()
			else:
				self.displayError('DHCP binding query failed.')


	### Click on delete DHCP binding button
	def delDhcpBindingButtonClick(self):
		aCurrentSelection = self._dhcpDList.currentRow()
		if aCurrentSelection >= 0:
			aMAC = self._dhcpDList.item(aCurrentSelection, DhcpCol.MAC).text()
			aDomain = self._dhcpDList.item(aCurrentSelection, DhcpCol.Domain).text()
			if aDomain == 'Home':
				d = 'default'
			else:
				d = 'guest'
			try:
				aReply = self._session.request('DHCPv4.Server.Pool.' + d, 'deleteStaticLease', { 'MACAddress': aMAC })
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('DHCP binding delete query error.')
				return

			if (aReply is not None) and ('status' in aReply):
				aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
				if len(aErrors):
					self.displayError(aErrors)
				self.refreshDhcpBindingButtonClick()
			else:
				self.displayError('DHCP binding delete query failed.')
		else:
			self.displayError(mx('Please select a DHCP binding.', 'dhcpSelect'))


	### Click on refresh DHCP attributes button
	def refreshDhcpAttributeButtonClick(self):
		self._dhcpAList.clearContents()
		self._dhcpAList.setRowCount(0)
		self.loadDhcpInfo()


	### Click on DHCP setup button
	def dhcpSetupButtonClick(self):
		# Retrieve current values
		try:
			d = self._session.request('NMC', 'getLANIP')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is None:
			self.displayError('DHCP query failed.')
			return

		# Load current values
		aDHCPEnabled = d.get('DHCPEnable')
		aDHCPAddress = d.get('Address')
		aDHCPMask = d.get('Netmask')
		aDHCPMinAddress = d.get('DHCPMinAddress')
		aDHCPMaxAddress = d.get('DHCPMaxAddress')
		if ((aDHCPEnabled is None) or
			(aDHCPAddress is None) or
			(aDHCPMask is None) or
			(aDHCPMinAddress is None) or
			(aDHCPMaxAddress is None)):
			self.displayError(mx('Cannot retrieve DHCP information.', 'dhcpLoad'))
			return

		# Ask user
		aDhcpSetupDialog = DhcpSetupDialog(aDHCPEnabled, aDHCPAddress, aDHCPMask, aDHCPMinAddress, aDHCPMaxAddress, self)
		if (aDhcpSetupDialog.exec()):
			aNewDHCPEnabled = aDhcpSetupDialog.getEnabled()
			aNewDHCPAddress = aDhcpSetupDialog.getAddress()
			aNewDHCPMask = aDhcpSetupDialog.getMask()
			aNewDHCPMinAddress = aDhcpSetupDialog.getMinAddress()
			aNewDHCPMaxAddress = aDhcpSetupDialog.getMaxAddress()

			aChange = False

			# Warn in case of DHCP disabling
			if (not aNewDHCPEnabled) and (aDHCPEnabled):
				aChange = True
				if not self.askQuestion(mx('Deactivating the DHCP server is likely to disconnect your home devices. Continue?',
										   'deactiv')):
					return

			# Warn in case of address changes
			if ((aNewDHCPAddress != aDHCPAddress) or
				(aNewDHCPMask != aDHCPMask) or
				(aNewDHCPMinAddress != aDHCPMinAddress) or
				(aNewDHCPMaxAddress != aDHCPMaxAddress)):
				aChange = True
				if not self.askQuestion(mx('Modifying the IP address of your Livebox and the other settings of the DHCP server, ' \
										   'may interrupt all your services. You will need to redefine the static IP addresses ' \
										   'according to the new addressing plan. Continue?', 'addrChange')):
					return

			if aChange:
				# Determine network prefix length
				i = aNewDHCPAddress.split('.')
				try:
					aNetwork = IPv4Network(i[0] + '.' + i[1] + '.' + i[2] + '.0/' + aNewDHCPMask)
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError(mx('Wrong values. Error: {}', 'dhcpValErr').format(e))
					return
				aNewDHCPPrefixLen = aNetwork.prefixlen

				p = {}
				p['Address'] = aNewDHCPAddress
				p['Netmask'] = aNewDHCPMask
				p['DHCPEnable'] = aNewDHCPEnabled
				p['DHCPMinAddress'] = aNewDHCPMinAddress
				p['DHCPMaxAddress'] = aNewDHCPMaxAddress
				p['PrefixLength'] = aNewDHCPPrefixLen

				try:
					aReply = self._session.request('NetMaster.LAN.default.Bridge.lan', 'setIPv4', p)
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('DHCP setup query error.')
					return

				if (aReply is not None) and ('status' in aReply):
					aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
					if len(aErrors):
						self.displayError(aErrors)
				else:
					self.displayError('DHCP setup query failed.')


	### Load DHCP bindings
	def loadDhcpBindings(self):
		self.startTask(lx('Getting DHCP bindings...'))
		self._dhcpDList.setSortingEnabled(False)

		# Home domain
		try:
			d = self._session.request('DHCPv4.Server.Pool.default', 'getStaticLeases', 'default')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		self.loadDhcpBindingsInList(d, 'Home')

		# Guest domain
		try:
			d = self._session.request('DHCPv4.Server.Pool.guest', 'getStaticLeases', 'guest')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		self.loadDhcpBindingsInList(d, 'Guest')

		self._dhcpDList.sortItems(DhcpCol.IP, QtCore.Qt.SortOrder.AscendingOrder)
		self._dhcpDList.setSortingEnabled(True)

		self.endTask()


	### Load DHCP bindings in the list
	def loadDhcpBindingsInList(self, iBindings, iDomain):
		if iBindings is None:
			self.displayError(mx('Cannot load {} DHCP bindings.', 'bindLoad').format(iDomain))
			return

		i = self._dhcpDList.rowCount()
		for b in iBindings:
			aKey = b.get('MACAddress', '').upper()
			aIP = b.get('IPAddress', '')

			self.addDeviceLineKey(self._dhcpDList, i, aKey)
			self.formatNameWidget(self._dhcpDList, i, aKey, DhcpCol.Name)
			self._dhcpDList.setItem(i, DhcpCol.Domain, QtWidgets.QTableWidgetItem(iDomain))
			self.formatMacWidget(self._dhcpDList, i, aKey, DhcpCol.MAC)

			aIpItem = LmTools.NumericSortItem(aIP)
			aIpItem.setData(QtCore.Qt.ItemDataRole.UserRole, int(IPv4Address(aIP)))
			self._dhcpDList.setItem(i, DhcpCol.IP, aIpItem)

			i += 1


	### First first available IP in the IP range
	def findFirstAvailableIp(self, iDomain, iUsedIPs):
		# Get network
		aNetwork = self.getDomainNetwork(iDomain)
		if aNetwork is None:
			return ''

		# Setup minimum address
		if iDomain == 'Home':
			aMinIP = IPv4Address(self._homeIpStart)
		else:
			aMinIP = IPv4Address(self._guestIpStart)

		# Create iterator
		aIterator = (aIP for aIP in aNetwork.hosts() if (str(aIP) not in iUsedIPs) and (aIP >= aMinIP))

		return str(next(aIterator))


	### Find if an IP is in domain network
	def isIpInNetwork(self, iIP, iDomain):
		aNetwork = self.getDomainNetwork(iDomain)
		if aNetwork is None:
			return False
		return IPv4Address(iIP) in aNetwork


	### Get domain network
	def getDomainNetwork(self, iDomain):
		# Select parameters
		if iDomain == 'Home':
			aServer = self._homeIpServer
			aMask = self._homeIpMask
		else:
			aServer = self._guestIpServer
			aMask = self._guestIpMask

		# Set network
		if LmTools.IsIPv4(aServer):
			i = aServer.split('.')
			return IPv4Network(i[0] + '.' + i[1] + '.' + i[2] + '.0/' + aMask)
		return None


	### Load DHCP infos list
	def loadDhcpInfo(self):
		self.startTask(lx('Getting DHCP information...'))

		i = 0
		i = self.addTitleLine(self._dhcpAList, i, lx('DHCP Home Information'))

		# Home domain + DHCPv6 infos
		g = None
		try:
			d = self._session.request('DHCPv4.Server', 'getDHCPServerPool')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			g = d.get('guest')
			d = d.get('default')
		if d is None:
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4'), 'DHCPv4.Server:getDHCPServerPool query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Enabled'), LmTools.FmtBool(d.get('Enable')))
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Status'), d.get('Status'))
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Gateway'), d.get('Server'))
			self._homeIpServer = d.get('Server')
			i = self.addInfoLine(self._dhcpAList, i, lx('Subnet Mask'), d.get('SubnetMask'))
			self._homeIpMask = d.get('SubnetMask')
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Start'), d.get('MinAddress'))
			self._homeIpStart = d.get('MinAddress')
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 End'), d.get('MaxAddress'))
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Lease Time'), LmTools.FmtTime(d.get('LeaseTime')))
			i = self.addInfoLine(self._dhcpAList, i, lx('DNS Servers'), d.get('DNSServers'))

		try:
			d = self._session.request('DHCPv6.Server', 'getDHCPv6ServerStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv6'), 'DHCPv6.Server:getDHCPv6ServerStatus query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv6 Status'), d)

		try:
			d = self._session.request('DHCPv6.Server', 'getPDPrefixInformation')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv6'), 'DHCPv6.Server:getPDPrefixInformation query error', LmTools.ValQual.Error)
		else:
			if (type(d).__name__ == 'list') and len(d):
				aPrefix = d[0].get('Prefix')
				if aPrefix is not None:
					aPrefixLen = d[0].get('PrefixLen')
					if aPrefixLen is not None:
						aPrefix += '/' + str(aPrefixLen)
					i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv6 Prefix'), aPrefix)

		# Guest domain
		if g is not None:
			i = self.addTitleLine(self._dhcpAList, i, lx('DHCP Guest Information'))

			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Enabled'), LmTools.FmtBool(g.get('Enable')))
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Status'), g.get('Status'))
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Gateway'), g.get('Server'))
			self._guestIpServer = g.get('Server')
			i = self.addInfoLine(self._dhcpAList, i, lx('Subnet Mask'), g.get('SubnetMask'))
			self._guestIpMask = g.get('SubnetMask')
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Start'), g.get('MinAddress'))
			self._guestIpStart = g.get('MinAddress')
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 End'), g.get('MaxAddress'))
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4 Lease Time'), LmTools.FmtTime(g.get('LeaseTime')))
			i = self.addInfoLine(self._dhcpAList, i, lx('DNS Servers'), g.get('DNSServers'))


		# DHCPv4
		i = self.addTitleLine(self._dhcpAList, i, lx('DHCPv4'))

		try:
			d = self._session.request('NeMo.Intf.data', 'getMIBs', { 'mibs': 'dhcp dhcpv6' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._dhcpAList, i, lx('DHCPv4'), 'NeMo.Intf.data:getMIBs query error', LmTools.ValQual.Error)
		else:
			p = d.get('dhcp')

			if p is not None:
				p = p.get('dhcp_data')
			if p is not None:
				i = self.addInfoLine(self._dhcpAList, i, lx('Status'), p.get('DHCPStatus'))
				i = self.addInfoLine(self._dhcpAList, i, lx('Lease Time'), LmTools.FmtTime(p.get('LeaseTime')))
				i = self.addInfoLine(self._dhcpAList, i, lx('Lease Time Remaining'), LmTools.FmtTime(p.get('LeaseTimeRemaining')))
				i = self.addInfoLine(self._dhcpAList, i, lx('Check Authentication'), LmTools.FmtBool(p.get('CheckAuthentication')))
				i = self.addInfoLine(self._dhcpAList, i, lx('Authentication Information'), p.get('AuthenticationInformation'))
				i = self.loadDhcpInfoOptions(lx('DHCPv4 Sent Options'), i, p.get('SentOption'))
				i = self.loadDhcpInfoOptions(lx('DHCPv4 Received Options'), i, p.get('ReqOption'))

			# DHCPv6
			i = self.addTitleLine(self._dhcpAList, i, lx('DHCPv6'))

			p = d.get('dhcpv6')

			if p is not None:
				p = p.get('dhcpv6_data')
			if p is not None:
				i = self.addInfoLine(self._dhcpAList, i, lx('Status'), p.get('DHCPStatus'))
				i = self.addInfoLine(self._dhcpAList, i, lx('DUID'), p.get('DUID'))
				i = self.addInfoLine(self._dhcpAList, i, lx('Request Addresses'), LmTools.FmtBool(p.get('RequestAddresses')))
				i = self.addInfoLine(self._dhcpAList, i, lx('Request Prefixes'), LmTools.FmtBool(p.get('RequestPrefixes')))
				i = self.addInfoLine(self._dhcpAList, i, lx('Requested Options'), p.get('RequestedOptions'))
				i = self.addInfoLine(self._dhcpAList, i, lx('Check Authentication'), LmTools.FmtBool(p.get('CheckAuthentication')))
				i = self.addInfoLine(self._dhcpAList, i, lx('Authentication Information'), p.get('AuthenticationInfo'))
				i = self.loadDhcpInfoOptions(lx('DHCPv6 Sent Options'), i, p.get('SentOption'))
				i = self.loadDhcpInfoOptions(lx('DHCPv6 Received Options'), i, p.get('ReceivedOption'))

		self.endTask()


	### Update DHCP infos list
	def loadDhcpInfoOptions(self, iTitle, iIndex, iOptions):
		i = iIndex
		
		if iOptions is not None:
			i = self.addTitleLine(self._dhcpAList, i, iTitle)

			for k in iOptions:
				o = iOptions[k]
				i = self.addInfoLine(self._dhcpAList, i, str(o.get('Tag', '?')), o.get('Value'))

		return i



# ############# Add DHCP binding dialog #############
class AddDhcpBindingDialog(QtWidgets.QDialog):
	def __init__(self, iHomeIpSuggest, iGuestIpSuggest, iParent = None):
		super(AddDhcpBindingDialog, self).__init__(iParent)
		self.resize(350, 180)

		self._homeIpSuggest = iHomeIpSuggest
		self._guestIpSuggest = iGuestIpSuggest
		self._ignoreSignal = False

		aDeviceLabel = QtWidgets.QLabel(lbx('Device'), objectName = 'deviceLabel')
		self._deviceCombo = QtWidgets.QComboBox(objectName = 'deviceCombo')
		self.loadDeviceList()
		for d in self._comboDeviceList:
			self._deviceCombo.addItem(d['Name'])
		self._deviceCombo.activated.connect(self.deviceSelected)

		aMacLabel = QtWidgets.QLabel(lbx('MAC address'), objectName = 'macLabel')
		self._macEdit = QtWidgets.QLineEdit(objectName = 'macEdit')
		aMacRegExp = QtCore.QRegularExpression('^' + LmTools.MAC_RS + '$')
		aMacValidator = QtGui.QRegularExpressionValidator(aMacRegExp)
		self._macEdit.setValidator(aMacValidator)
		self._macEdit.textChanged.connect(self.macTyped)

		aDomainLabel = QtWidgets.QLabel(lbx('Domain'), objectName = 'domainLabel')
		self._domainCombo = QtWidgets.QComboBox(objectName = 'domainCombo')
		self._domainCombo.addItems(['Home', 'Guest'])
		self._domainCombo.activated.connect(self.domainSelected)

		aIPLabel = QtWidgets.QLabel(lbx('IP address'), objectName = 'ipLabel')
		self._ipEdit = QtWidgets.QLineEdit(objectName = 'ipEdit')
		aIpRegExp = QtCore.QRegularExpression('^' + LmTools.IPv4_RS + '$')
		aIpValidator = QtGui.QRegularExpressionValidator(aIpRegExp)
		self._ipEdit.setValidator(aIpValidator)
		self._ipEdit.textChanged.connect(self.ipTyped)

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(aDeviceLabel, 0, 0)
		aGrid.addWidget(self._deviceCombo, 0, 1)
		aGrid.addWidget(aMacLabel, 1, 0)
		aGrid.addWidget(self._macEdit, 1, 1)
		aGrid.addWidget(aDomainLabel, 2, 0)
		aGrid.addWidget(self._domainCombo, 2, 1)
		aGrid.addWidget(aIPLabel, 3, 0)
		aGrid.addWidget(self._ipEdit, 3, 1)

		self._okButton = QtWidgets.QPushButton(lbx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lbx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'dbinding')

		self.setWindowTitle(lbx('Add DHCP binding'))
		self.suggestIP()
		self.setOkButtonState()
		self.setModal(True)
		self.show()


	def loadDeviceList(self):
		self._deviceList = self.parent().getDeviceList()
		self._comboDeviceList = []

		# Load from MacAddrTable file
		for d in LmConf.MacAddrTable:
			aDevice = {}
			aDevice['Name'] = LmConf.MacAddrTable[d]
			aDevice['MAC'] = d
			self._comboDeviceList.append(aDevice)

		# Load from device list if not already loaded
		for d in self._deviceList:
			if (len(d['MAC'])) and (not any(e['MAC'] == d['MAC'] for e in self._comboDeviceList)):
				aDevice = {}
				aDevice['Name'] = d['LBName']
				aDevice['MAC'] = d['MAC']
				self._comboDeviceList.append(aDevice)

		# Sort by name
		self._comboDeviceList = sorted(self._comboDeviceList, key = lambda x: x['Name'])

		# Insert unknown device at the beginning
		aDevice = {}
		aDevice['Name'] = lbx('-Unknown-')
		aDevice['MAC'] = ''
		self._comboDeviceList.insert(0, aDevice)


	def deviceSelected(self, iIndex):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			self._macEdit.setText(self._comboDeviceList[iIndex]['MAC'])
			self._ignoreSignal = False
			self.suggestIP()


	def domainSelected(self, iIndex):
		self.suggestIP()


	def macTyped(self, iMac):
		if not self._ignoreSignal:
			self._ignoreSignal = True

			aIndex = 0
			i = 0
			for d in self._comboDeviceList:
				if d['MAC'] == iMac:
					aIndex = i
					break
				i += 1

			self._deviceCombo.setCurrentIndex(aIndex)
			if aIndex:
				self.suggestIP()
			self._ignoreSignal = False
		self.setOkButtonState()


	def ipTyped(self, iIp):
		self.setOkButtonState()


	def suggestIP(self):
		aDomain = self.getDomain()

		# Search if MAC corresponds to an active IP
		aIP = None
		aMAC = self.getMacAddress()
		if len(aMAC):
			aDevice = next((d for d in self._deviceList if (d['MAC'] == aMAC) and d['Active']), None)
			if aDevice is not None:
				aIP = aDevice['IP']

		# Check if IP is in the domain network
		if aIP is not None:
			if not self.parent().isIpInNetwork(aIP, aDomain):
				aIP = None

		# If no IP found, suggest the next available one
		if aIP is None:
			if aDomain == 'Home':
				aIP = self._homeIpSuggest
			else:
				aIP = self._guestIpSuggest

		self._ipEdit.setText(aIP)


	def setOkButtonState(self):
		self._okButton.setDisabled((len(self.getMacAddress()) == 0) or (len(self.getIpAddress()) == 0))


	def getMacAddress(self):
		return self._macEdit.text()


	def getDomain(self):
		return self._domainCombo.currentText()


	def getIpAddress(self):
		return self._ipEdit.text()



# ############# DHCP Setup dialog #############
class DhcpSetupDialog(QtWidgets.QDialog):
	def __init__(self, iEnabled, iAddress, iMask, iMin, iMax, iParent = None):
		super(DhcpSetupDialog, self).__init__(iParent)
		self.resize(300, 225)

		self._enableCheckBox = QtWidgets.QCheckBox(lsx('DHCP Enabled'), objectName = 'enableCheckbox')
		if iEnabled:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		aIpRegExp = QtCore.QRegularExpression('^' + LmTools.IPv4_RS + '$')
		aIpValidator = QtGui.QRegularExpressionValidator(aIpRegExp)

		aLiveboxIpLabel = QtWidgets.QLabel(lsx('Livebox IP address'), objectName = 'liveboxIpLabel')
		self._liveboxIpEdit = QtWidgets.QLineEdit(objectName = 'liveboxIpEdit')
		self._liveboxIpEdit.setValidator(aIpValidator)
		self._liveboxIpEdit.setText(iAddress)
		self._liveboxIpEdit.textChanged.connect(self.textTyped)

		aMaskLabel = QtWidgets.QLabel(lsx('Subnet mask'), objectName = 'maskLabel')
		self._maskEdit = QtWidgets.QLineEdit(objectName = 'maskEdit')
		self._maskEdit.setValidator(aIpValidator)
		self._maskEdit.setText(iMask)
		self._maskEdit.textChanged.connect(self.textTyped)

		aMinIpLabel = QtWidgets.QLabel(lsx('DHCP start IP'), objectName = 'minLabel')
		self._minEdit = QtWidgets.QLineEdit(objectName = 'minEdit')
		self._minEdit.setValidator(aIpValidator)
		self._minEdit.setText(iMin)
		self._minEdit.textChanged.connect(self.textTyped)

		aMaxIpLabel = QtWidgets.QLabel(lsx('DHCP end IP'), objectName = 'maxLabel')
		self._maxEdit = QtWidgets.QLineEdit(objectName = 'maxEdit')
		self._maxEdit.setValidator(aIpValidator)
		self._maxEdit.setText(iMax)
		self._maxEdit.textChanged.connect(self.textTyped)

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(self._enableCheckBox, 0, 0)
		aGrid.addWidget(aLiveboxIpLabel, 1, 0)
		aGrid.addWidget(self._liveboxIpEdit, 1, 1)
		aGrid.addWidget(aMaskLabel, 2, 0)
		aGrid.addWidget(self._maskEdit, 2, 1)
		aGrid.addWidget(aMinIpLabel, 3, 0)
		aGrid.addWidget(self._minEdit, 3, 1)
		aGrid.addWidget(aMaxIpLabel, 4, 0)
		aGrid.addWidget(self._maxEdit, 4, 1)

		self._okButton = QtWidgets.QPushButton(lsx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lsx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'dsetup')

		self.setWindowTitle(lsx('DHCP Setup'))
		self.setOkButtonState()
		self.setModal(True)
		self.show()


	def textTyped(self, iText):
		self.setOkButtonState()


	def setOkButtonState(self):
		self._okButton.setDisabled((len(self.getAddress()) == 0) or
								   (len(self.getMask()) == 0) or
								   (len(self.getMinAddress()) == 0) or
								   (len(self.getMaxAddress()) == 0))


	def getEnabled(self):
		return self._enableCheckBox.checkState() == QtCore.Qt.CheckState.Checked


	def getAddress(self):
		return self._liveboxIpEdit.text()


	def getMask(self):
		return self._maskEdit.text()


	def getMinAddress(self):
		return self._minEdit.text()


	def getMaxAddress(self):
		return self._maxEdit.text()