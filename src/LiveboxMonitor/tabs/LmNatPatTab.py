### Livebox Monitor NAT/PAT tab module ###

import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from app import LmTools, LmConfig
from app.LmIcons import LmIcon
from app.LmConfig import LmConf
from lang.LmLanguages import (GetNatPatLabel as lx,
							  GetPatRuleDialogLabel as lrx,
							  GetPtfRuleDialogLabel as lfx,
							  GetNatPatRuleTypeDialogLabel as ltx)

from __init__ import __build__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'natPatTab'
IPV6_SOURCE_PORT_WORKING = False		# SourcePort is available in the API but not working, at least for a LB5

# List columns
class PatCol(IntEnum):
	Key = 0
	Enabled = 1
	Type = 2
	ID = 3
	Description = 4
	Protocols = 5
	IntPort = 6
	ExtPort = 7
	Device = 8
	DestIP = 9
	ExtIPs = 10
	Count = 11
PAT_ICON_COLUMNS = [PatCol.Enabled]

class PtfCol(IntEnum):
	Key = 0
	Enabled = 1
	Type = 2
	ID = 3
	Description = 4
	Protocols = 5
	Device = 6
	DestIP = 7
	ExtIPs = 8
	Count = 9
PTF_ICON_COLUMNS = [PtfCol.Enabled]

RULE_TYPE_IPv4 = 'IPv4'
RULE_TYPE_IPv6 = 'IPv6'
RULE_TYPE_UPnP = 'UPnP'
RULE_PAT_TYPES = [RULE_TYPE_IPv4, RULE_TYPE_IPv6, RULE_TYPE_UPnP]
RULE_PTF_TYPES = [RULE_TYPE_IPv4, RULE_TYPE_IPv6]

# Protocols - https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
# Numbers
class Protocols(IntEnum):
	ICMP = 1
	TCP = 6
	UDP = 17
	GRE = 47
	ESP = 50
	AH = 51
	ICMPv6 = 58

# Names
PROTOCOL_NAMES = {
	'1':	'ICMP',
	'2':	'IGMP',
	'3':	'GGP',
	'4': 	'IPv4',
	'5': 	'ST',
	'6':	'TCP',
	'7':	'CBT',
	'8':	'EGP',
	'9':	'IGP',
	'10':	'BBN',
	'11':	'NVP',
	'12':	'PUP',
	'17':	'UDP',
	'18':	'MUX',
	'20':	'HMP',
	'27':	'RDP',
	'33':	'DCCP',
	'37':	'DDP',
	'40':	'IL',
	'41':	'IPv6',
	'46':	'RSVP',
	'47':	'GRE',
	'48':	'DSR',
	'49':	'BNA',
	'50':	'ESP',
	'51':	'AH',
	'58':	'ICMPv6',
	'75':	'PVP',
	'84':	'IPTM',
	'86':	'DGP',
	'87':	'TCF',
	'88':	'EIGRP',
	'89':	'OSPF',
	'92':	'MTP'
}


# ################################ LmNatPat class ################################
class LmNatPat:

	### Create NAT/PAT tab
	def createNatPatTab(self):
		self._natPatTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# PAT - port forwarding list
		self._patList = QtWidgets.QTableWidget(objectName = 'patList')
		self._patList.setColumnCount(PatCol.Count)
		self._patList.setHorizontalHeaderLabels(('Key', lx('A'),
														lx('Type'),
														lx('Name'),
														lx('Port Forwarding Rule Description'),
														lx('Protocols'),
														lx('Internal Port'),
														lx('External Port'),
														lx('Device'),
														'DestIP',
														lx('External IPs')))
		self._patList.setColumnHidden(PatCol.Key, True)
		self._patList.setColumnHidden(PatCol.DestIP, True)
		aHeader = self._patList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(PatCol.Description, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(PatCol.Enabled, QtCore.Qt.Orientation.Horizontal, 'plist_Enabled', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.Type, QtCore.Qt.Orientation.Horizontal, 'plist_Type', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.ID, QtCore.Qt.Orientation.Horizontal, 'plist_ID', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.Description, QtCore.Qt.Orientation.Horizontal, 'plist_Description', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.Protocols, QtCore.Qt.Orientation.Horizontal, 'plist_Protocols', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.IntPort, QtCore.Qt.Orientation.Horizontal, 'plist_IntPort', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.ExtPort, QtCore.Qt.Orientation.Horizontal, 'plist_ExtPort', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.Device, QtCore.Qt.Orientation.Horizontal, 'plist_Device', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PatCol.ExtIPs, QtCore.Qt.Orientation.Horizontal, 'plist_ExtIPs', QtCore.Qt.ItemDataRole.UserRole)
		self._patList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._patList.setColumnWidth(PatCol.Enabled, 10)
		self._patList.setColumnWidth(PatCol.Type, 55)
		self._patList.setColumnWidth(PatCol.ID, 120)
		self._patList.setColumnWidth(PatCol.Description, 400)
		self._patList.setColumnWidth(PatCol.Protocols, 70)
		self._patList.setColumnWidth(PatCol.IntPort, 95)
		self._patList.setColumnWidth(PatCol.ExtPort, 95)
		self._patList.setColumnWidth(PatCol.Device, 180)
		self._patList.setColumnWidth(PatCol.ExtIPs, 250)
		self._patList.verticalHeader().hide()
		self._patList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._patList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._patList.setSortingEnabled(True)
		self._patList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._patList.setItemDelegate(LmTools.CenteredIconsDelegate(self, PAT_ICON_COLUMNS))
		self._patList.itemSelectionChanged.connect(self.patListClick)
		self._patList.doubleClicked.connect(self.editPatRuleButtonClick)
		LmConfig.SetTableStyle(self._patList)

		# PAT - port forwarding button bar
		aPatButtonsBox = QtWidgets.QHBoxLayout()
		aPatButtonsBox.setSpacing(30)
		aRefreshPatButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refreshPat')
		aRefreshPatButton.clicked.connect(self.refreshPatButtonClick)
		aPatButtonsBox.addWidget(aRefreshPatButton)
		self._patEnableButton = QtWidgets.QPushButton(lx('Enable'), objectName = 'enablePat')
		self._patEnableButton.clicked.connect(self.enablePatButtonClick)
		aPatButtonsBox.addWidget(self._patEnableButton)
		aAddRuleButton = QtWidgets.QPushButton(lx('Add...'), objectName = 'addPat')
		aAddRuleButton.clicked.connect(self.addPatRuleButtonClick)
		aPatButtonsBox.addWidget(aAddRuleButton)
		self._patEditRuleButton = QtWidgets.QPushButton(lx('Edit...'), objectName = 'editPat')
		self._patEditRuleButton.clicked.connect(self.editPatRuleButtonClick)
		aPatButtonsBox.addWidget(self._patEditRuleButton)
		self._patDelRuleButton = QtWidgets.QPushButton(lx('Delete'), objectName = 'deletePat')
		self._patDelRuleButton.clicked.connect(self.delPatRuleButtonClick)
		aPatButtonsBox.addWidget(self._patDelRuleButton)
		aDelAllRulesButton = QtWidgets.QPushButton(lx('Delete All...'), objectName = 'deleteAllPat')
		aDelAllRulesButton.clicked.connect(self.delAllPatRulesButtonClick)
		aPatButtonsBox.addWidget(aDelAllRulesButton)
		aExportPatRulesButton = QtWidgets.QPushButton(lx('Export...'), objectName = 'exportPat')
		aExportPatRulesButton.clicked.connect(self.exportPatRulesButtonClick)
		aPatButtonsBox.addWidget(aExportPatRulesButton)
		aImportPatRulesButton = QtWidgets.QPushButton(lx('Import...'), objectName = 'importPat')
		aImportPatRulesButton.clicked.connect(self.importPatRulesButtonClick)
		aPatButtonsBox.addWidget(aImportPatRulesButton)

		# PTF - Layer 3 protocol forwarding list
		self._ptfList = QtWidgets.QTableWidget(objectName = 'ptfList')
		self._ptfList.setColumnCount(PtfCol.Count)
		self._ptfList.setHorizontalHeaderLabels(('Key', lx('A'),
														lx('Type'),
														lx('Name'),
														lx('Protocol Forwarding Rule Description'),
														lx('Protocols'),
														lx('Device'),
														'DestIP',
														lx('External IPs')))
		self._ptfList.setColumnHidden(PtfCol.Key, True)
		self._ptfList.setColumnHidden(PtfCol.DestIP, True)
		aHeader = self._ptfList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(PtfCol.Description, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(PtfCol.Enabled, QtCore.Qt.Orientation.Horizontal, 'tlist_Enabled', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PtfCol.Type, QtCore.Qt.Orientation.Horizontal, 'tlist_Type', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PtfCol.ID, QtCore.Qt.Orientation.Horizontal, 'tlist_ID', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PtfCol.Description, QtCore.Qt.Orientation.Horizontal, 'tlist_Description', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PtfCol.Protocols, QtCore.Qt.Orientation.Horizontal, 'tlist_Protocols', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PtfCol.Device, QtCore.Qt.Orientation.Horizontal, 'tlist_Device', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(PtfCol.ExtIPs, QtCore.Qt.Orientation.Horizontal, 'tlist_ExtIPs', QtCore.Qt.ItemDataRole.UserRole)
		self._ptfList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._ptfList.setColumnWidth(PtfCol.Enabled, 10)
		self._ptfList.setColumnWidth(PtfCol.Type, 55)
		self._ptfList.setColumnWidth(PtfCol.ID, 120)
		self._ptfList.setColumnWidth(PtfCol.Description, 360)
		self._ptfList.setColumnWidth(PtfCol.Protocols, 180)
		self._ptfList.setColumnWidth(PtfCol.Device, 220)
		self._ptfList.setColumnWidth(PtfCol.ExtIPs, 250)
		self._ptfList.verticalHeader().hide()
		self._ptfList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._ptfList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._ptfList.setSortingEnabled(True)
		self._ptfList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._ptfList.setItemDelegate(LmTools.CenteredIconsDelegate(self, PTF_ICON_COLUMNS))
		self._ptfList.itemSelectionChanged.connect(self.ptfListClick)
		self._ptfList.doubleClicked.connect(self.editPtfRuleButtonClick)
		LmConfig.SetTableStyle(self._ptfList)
		aListSize = LmConfig.TableHeight(5)
		self._ptfList.setMinimumHeight(aListSize)
		self._ptfList.setMaximumHeight(aListSize)

		# PTF - Layer 3 protocol forwarding button bar
		aPtfButtonsBox = QtWidgets.QHBoxLayout()
		aPtfButtonsBox.setSpacing(30)
		aRefreshPtfButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refreshPtf')
		aRefreshPtfButton.clicked.connect(self.refreshPtfButtonClick)
		aPtfButtonsBox.addWidget(aRefreshPtfButton)
		self._ptfEnableButton = QtWidgets.QPushButton(lx('Enable'), objectName = 'enablePtf')
		self._ptfEnableButton.clicked.connect(self.enablePtfButtonClick)
		aPtfButtonsBox.addWidget(self._ptfEnableButton)
		aAddRuleButton = QtWidgets.QPushButton(lx('Add...'), objectName = 'addPtf')
		aAddRuleButton.clicked.connect(self.addPtfRuleButtonClick)
		aPtfButtonsBox.addWidget(aAddRuleButton)
		self._ptfEditRuleButton = QtWidgets.QPushButton(lx('Edit...'), objectName = 'editPtf')
		self._ptfEditRuleButton.clicked.connect(self.editPtfRuleButtonClick)
		aPtfButtonsBox.addWidget(self._ptfEditRuleButton)
		self._ptfDelRuleButton = QtWidgets.QPushButton(lx('Delete'), objectName = 'deletePtf')
		self._ptfDelRuleButton.clicked.connect(self.delPtfRuleButtonClick)
		aPtfButtonsBox.addWidget(self._ptfDelRuleButton)
		aDelAllRulesButton = QtWidgets.QPushButton(lx('Delete All...'), objectName = 'deleteAllPtf')
		aDelAllRulesButton.clicked.connect(self.delAllPtfRulesButtonClick)
		aPtfButtonsBox.addWidget(aDelAllRulesButton)
		aExportPtfRulesButton = QtWidgets.QPushButton(lx('Export...'), objectName = 'exportPtf')
		aExportPtfRulesButton.clicked.connect(self.exportPtfRulesButtonClick)
		aPtfButtonsBox.addWidget(aExportPtfRulesButton)
		aImportPtfRulesButton = QtWidgets.QPushButton(lx('Import...'), objectName = 'importPtf')
		aImportPtfRulesButton.clicked.connect(self.importPtfRulesButtonClick)
		aPtfButtonsBox.addWidget(aImportPtfRulesButton)

		# Layout
		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addWidget(self._patList, 1)
		aVBox.addLayout(aPatButtonsBox, 0)
		aVBox.insertSpacing(-1, 3)
		aVBox.addWidget(aSeparator)
		aVBox.insertSpacing(-1, 3)
		aVBox.addWidget(self._ptfList, 0)
		aVBox.addLayout(aPtfButtonsBox, 0)
		self._natPatTab.setLayout(aVBox)

		LmConfig.SetToolTips(self._natPatTab, 'natpat')
		self._tabWidget.addTab(self._natPatTab, lx('NAT/PAT'))

		# Init context
		self.natPatTabInit()


	### Init NAT/PAT tab context
	def natPatTabInit(self):
		self._natPatDataLoaded = False
		self._protocolNumbers = {}


	### Click on NAT/PAT tab
	def natPatTabClick(self):
		if not self._natPatDataLoaded:
			self._natPatDataLoaded = True		# Must be first to avoid reentrency during tab drag&drop
			self.loadProtocolNumbers()
			self.loadDeviceIpNameMap()
			self.loadPatRules()
			self.loadPtfRules()


	### Click on PAT list item
	def patListClick(self):
		aCurrentSelection = self._patList.currentRow()
		if aCurrentSelection >= 0:
			self._patEnableButton.setEnabled(True)
			self._patEditRuleButton.setEnabled(True)
			self._patDelRuleButton.setEnabled(True)
			aEnable = self._patList.item(aCurrentSelection, PatCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole)
			if aEnable:
				self._patEnableButton.setText(lx('Disable'))
			else:
				self._patEnableButton.setText(lx('Enable'))
		else:
			self._patEnableButton.setEnabled(False)
			self._patEditRuleButton.setEnabled(False)
			self._patDelRuleButton.setEnabled(False)


	### Click on refresh PAT rules button
	def refreshPatButtonClick(self):
		self.refreshPatList()


	### Click on enable/disable PAT rule button
	def enablePatButtonClick(self):
		r = self.getSelectedPatRule()
		if r is not None:
			r['Enable'] = not r['Enable']
			self.startTask(lx('Saving rule...'))
			if self.savePatRule(r):
				self.commitNatPatRuleChange()
				i = self._patList.currentRow()
				self._patList.setItem(i, PatCol.Enabled, self.formatActiveTableWidget(r['Enable']))
				self.patListClick()
			self.endTask()


	### Click on add PAT rule button
	def addPatRuleButtonClick(self):
		aPatRuleDialog = PatRuleDialog(None, self)
		if aPatRuleDialog.exec():
			self.startTask(lx('Saving rule...'))
			r = aPatRuleDialog.getRule()
			if self.savePatRule(r):
				self.commitNatPatRuleChange()
				self.refreshPatList()
			self.endTask()


	### Click on edit PAT rule button
	def editPatRuleButtonClick(self):
		r = self.getSelectedPatRule()
		if r is not None:
			aPatRuleDialog = PatRuleDialog(r, self)
			if aPatRuleDialog.exec():
				self.startTask(lx('Saving rule...'))
				# First delete current rule
				self.delPatRule(r)
				# Then save new one
				r = aPatRuleDialog.getRule()
				if self.savePatRule(r):
					self.commitNatPatRuleChange()
					self.refreshPatList()
				self.endTask()


	### Click on delete PAT rule rules button
	def delPatRuleButtonClick(self):
		r = self.getSelectedPatRule()
		if r is not None:
			self.startTask(lx('Deleting rule...'))
			if self.delPatRule(r):
				self.commitNatPatRuleChange()
				self.refreshPatList()
			self.endTask()


	### Click on delete all PAT rules button
	def delAllPatRulesButtonClick(self):
		aTypeDialog = NatPatRuleTypeDialog(True, self)
		if aTypeDialog.exec():
			self.startTask(lx('Deleting rules...'))
			t = aTypeDialog.getTypes()

			# Delete all IPv4 rules if selected
			if t[RULE_TYPE_IPv4]:
				self.delAllIPv4PatRule(False)

			# Delete all UPnP rules if selected
			if t[RULE_TYPE_UPnP]:
				self.delAllIPv4PatRule(True)

			# Delete one by one IPv6 rules if selected
			if t[RULE_TYPE_IPv6]:
				i = 0
				n = self._patList.rowCount()
				while (i < n):
					r = self.getPatRuleFromList(i)
					if (r is not None) and (r['Type'] == RULE_TYPE_IPv6):
						self.delPatRule(r)
					i += 1

			# Commit & refresh
			self.commitNatPatRuleChange()
			self.refreshPatList()
			self.endTask()

			self.displayStatus('All selected rule(s) deleted.')


	### Click on export PAT rules button
	def exportPatRulesButtonClick(self):
		aTypeDialog = NatPatRuleTypeDialog(True, self)
		if aTypeDialog.exec():
			t = aTypeDialog.getTypes()

			aFileName = QtWidgets.QFileDialog.getSaveFileName(self, lx('Export File'), lx('Port Forwarding Rules') + '.txt', '*.txt')
			aFileName = aFileName[0]
			if aFileName == '':
				return

			try:
				aExportFile = open(aFileName, 'w')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Cannot create the file.')
				return

			self.startTask(lx('Exporting port forwarding rules...'))

			i = 0
			c = 0
			n = self._patList.rowCount()
			aRules = []
			while (i < n):
				r = self.getPatRuleFromList(i)
				if (r is not None) and t[r['Type']]:
					aRules.append(r)
					c += 1
				i += 1

			aFile = {}
			aFile['Version'] = __build__
			aFile['Type'] = 'PAT'
			aFile['Rules'] = aRules
			json.dump(aFile, aExportFile, indent = 4)

			self.endTask()

			try:
				aExportFile.close()
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Cannot save the file.')

			self.displayStatus('{} rule(s) exported.'.format(c))


	### Click on import PAT rules button
	def importPatRulesButtonClick(self):
		aFileName = QtWidgets.QFileDialog.getOpenFileName(self, lx('Select file to import'), '', '*.txt')
		aFileName = aFileName[0]
		if aFileName == '':
			return

		try:
			aImportFile = open(aFileName, 'r')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Cannot open the file.')
			return

		aError = False
		try:
			aFile = json.load(aImportFile)
		except BaseException as e:
			LmTools.Error('Error loading file: {}'.format(e))
			self.displayError('Wrong file format.')
			aError = True

		if not aError:
			aRules = aFile.get('Rules', None)

			if (aFile.get('Type', '') != 'PAT') or (aRules is None):
				self.displayError('Wrong file type.')
				aError = True

		if not aError:
			self.startTask(lx('Importing port forwarding rules...'))

			c = 0
			for r in aRules:
				if self.checkPatRule(r) and self.savePatRule(r):
					c += 1

			self.endTask()

		try:
			aImportFile.close()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Cannot close the file.')

		if not aError:
			self.commitNatPatRuleChange()
			self.refreshPatList()

			self.displayStatus('{} rule(s) imported.'.format(c))


	### Click on PTF list item
	def ptfListClick(self):
		aCurrentSelection = self._ptfList.currentRow()
		if aCurrentSelection >= 0:
			self._ptfEnableButton.setEnabled(True)
			self._ptfEditRuleButton.setEnabled(True)
			self._ptfDelRuleButton.setEnabled(True)
			aEnable = self._ptfList.item(aCurrentSelection, PtfCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole)
			if aEnable:
				self._ptfEnableButton.setText(lx('Disable'))
			else:
				self._ptfEnableButton.setText(lx('Enable'))
		else:
			self._ptfEnableButton.setEnabled(False)
			self._ptfEditRuleButton.setEnabled(False)
			self._ptfDelRuleButton.setEnabled(False)


	### Click on refresh PTF rules button
	def refreshPtfButtonClick(self):
		self.refreshPtfList()


	### Click on enable/disable PTF rule button
	def enablePtfButtonClick(self):
		r = self.getSelectedPtfRule()
		if r is not None:
			r['Enable'] = not r['Enable']
			self.startTask(lx('Saving rule...'))
			if self.savePtfRule(r):
				self.commitNatPatRuleChange()
				i = self._ptfList.currentRow()
				self._ptfList.setItem(i, PtfCol.Enabled, self.formatActiveTableWidget(r['Enable']))
				self.ptfListClick()
			self.endTask()


	### Click on add PTF rule button
	def addPtfRuleButtonClick(self):
		aPtfRuleDialog = PtfRuleDialog(None, self)
		if aPtfRuleDialog.exec():
			self.startTask(lx('Saving rule...'))
			r = aPtfRuleDialog.getRule()
			if self.savePtfRule(r):
				self.commitNatPatRuleChange()
				self.refreshPtfList()
			self.endTask()


	### Click on edit PTF rule button
	def editPtfRuleButtonClick(self):
		r = self.getSelectedPtfRule()
		if r is not None:
			aPtfRuleDialog = PtfRuleDialog(r, self)
			if aPtfRuleDialog.exec():
				self.startTask(lx('Saving rule...'))
				# First delete current rule
				self.delPtfRule(r)
				# Then save new one
				r = aPtfRuleDialog.getRule()
				if self.savePtfRule(r):
					self.commitNatPatRuleChange()
					self.refreshPtfList()
				self.endTask()


	### Click on delete PTF rule rules button
	def delPtfRuleButtonClick(self):
		r = self.getSelectedPtfRule()
		if r is not None:
			self.startTask(lx('Deleting rule...'))
			if self.delPtfRule(r):
				self.commitNatPatRuleChange()
				self.refreshPtfList()
			self.endTask()


	### Click on delete all PTF rules button
	def delAllPtfRulesButtonClick(self):
		aTypeDialog = NatPatRuleTypeDialog(False, self)
		if aTypeDialog.exec():
			self.startTask(lx('Deleting rules...'))
			t = aTypeDialog.getTypes()
			i = 0
			c = 0
			n = self._ptfList.rowCount()
			while (i < n):
				r = self.getPtfRuleFromList(i)
				if (r is not None) and t[r['Type']]:
					self.delPtfRule(r)
					c += 1
				i += 1
			self.commitNatPatRuleChange()
			self.refreshPtfList()
			self.endTask()

			self.displayStatus('{} rule(s) deleted.'.format(c))


	### Click on export PTF rules button
	def exportPtfRulesButtonClick(self):
		aTypeDialog = NatPatRuleTypeDialog(False, self)
		if aTypeDialog.exec():
			t = aTypeDialog.getTypes()

			aFileName = QtWidgets.QFileDialog.getSaveFileName(self, lx('Export File'), lx('Protocol Forwarding Rules') + '.txt', '*.txt')
			aFileName = aFileName[0]
			if aFileName == '':
				return

			try:
				aExportFile = open(aFileName, 'w')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Cannot create the file.')
				return

			self.startTask(lx('Exporting protocol forwarding rules...'))

			i = 0
			c = 0
			n = self._ptfList.rowCount()
			aRules = []
			while (i < n):
				r = self.getPtfRuleFromList(i)
				if (r is not None) and t[r['Type']]:
					aRules.append(r)
					c += 1
				i += 1

			aFile = {}
			aFile['Version'] = __build__
			aFile['Type'] = 'PTF'
			aFile['Rules'] = aRules
			json.dump(aFile, aExportFile, indent = 4)

			self.endTask()

			try:
				aExportFile.close()
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Cannot save the file.')

			self.displayStatus('{} rule(s) exported.'.format(c))


	### Click on import PTF rules button
	def importPtfRulesButtonClick(self):
		aFileName = QtWidgets.QFileDialog.getOpenFileName(self, lx('Select file to import'), '', '*.txt')
		aFileName = aFileName[0]
		if aFileName == '':
			return

		try:
			aImportFile = open(aFileName, 'r')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Cannot open the file.')
			return

		aError = False
		try:
			aFile = json.load(aImportFile)
		except BaseException as e:
			LmTools.Error('Error loading file: {}'.format(e))
			self.displayError('Wrong file format.')
			aError = True

		if not aError:
			aRules = aFile.get('Rules', None)

			if (aFile.get('Type', '') != 'PTF') or (aRules is None):
				self.displayError('Wrong file type.')
				aError = True

		if not aError:
			self.startTask(lx('Importing protocol forwarding rules...'))

			c = 0
			for r in aRules:
				if self.checkPtfRule(r) and self.savePtfRule(r):
					c += 1

			self.endTask()

		try:
			aImportFile.close()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Cannot close the file.')

		if not aError:
			self.commitNatPatRuleChange()
			self.refreshPtfList()

			self.displayStatus('{} rule(s) imported.'.format(c))


	### Load protocol name to number reverse map from number to name
	def loadProtocolNumbers(self):
		# Init
		self._protocolNumber = {}

		# Build reverse map
		for k in PROTOCOL_NAMES:
			self._protocolNumbers[PROTOCOL_NAMES[k]] = k


	### Refresh PAT list
	def refreshPatList(self):
		self._patList.clearContents()
		self._patList.setRowCount(0)
		self.loadDeviceIpNameMap()
		self.loadPatRules()


	### Load PAT rules
	def loadPatRules(self):
		self.startTask(lx('Loading port forwarding rules...'))
		self._patList.setSortingEnabled(False)

		# IPv4 types (webui / upnp / others?)
		self.loadIPv4PatRules()

		# IPv6 types
		self.loadIPv6PatRules()

		self._patList.sortItems(PatCol.Type, QtCore.Qt.SortOrder.AscendingOrder)
		self._patList.setSortingEnabled(True)

		self._patList.setCurrentCell(-1, -1)
		self.patListClick()

		self.endTask()


	### Load IPv4 (webui / upnp / others?) PAT rules
	def loadIPv4PatRules(self):
		try:
			d = self._session.request('Firewall:getPortForwarding')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			self.displayError('Cannot load IPv4 port forwarding rules.')
			return

		i = self._patList.rowCount()
		for k in d:
			self._patList.insertRow(i)
			r = d[k]

			aActiveStatus = r.get('Enable', False)
			self._patList.setItem(i, PatCol.Enabled, self.formatActiveTableWidget(aActiveStatus))

			aOrigin = r.get('Origin', '')
			self._patList.setItem(i, PatCol.Type, self.formatNatPatOriginTableWidget(aOrigin, False))

			aID = r.get('Id', '')
			self._patList.setItem(i, PatCol.Key, QtWidgets.QTableWidgetItem('v4_' + aID))

			if len(aID) > len(aOrigin) + 1:
				aID = aID[len(aOrigin) + 1:]
			self._patList.setItem(i, PatCol.ID, QtWidgets.QTableWidgetItem(aID))

			self._patList.setItem(i, PatCol.Description, QtWidgets.QTableWidgetItem(r.get('Description', '')))

			aProtocols = r.get('Protocol', '')
			self._patList.setItem(i, PatCol.Protocols, self.formatNatPatProtocolsTableWidget(aProtocols))

			self._patList.setItem(i, PatCol.IntPort, self.formatPortTableWidget(r.get('InternalPort', '')))
			self._patList.setItem(i, PatCol.ExtPort, self.formatPortTableWidget(r.get('ExternalPort', '')))

			aDestinationIP = r.get('DestinationIPAddress', '')
			self._patList.setItem(i, PatCol.DestIP, QtWidgets.QTableWidgetItem(aDestinationIP))
			self._patList.setItem(i, PatCol.Device, QtWidgets.QTableWidgetItem(self.getDeviceNameFromIp(aDestinationIP)))

			aExternalIPs = r.get('SourcePrefix', '')
			if len(aExternalIPs) == 0:
				aExternalIPs = lx('All')
			self._patList.setItem(i, PatCol.ExtIPs, QtWidgets.QTableWidgetItem(aExternalIPs))

			i += 1


	### Load IPv6 PAT rules
	def loadIPv6PatRules(self):
		try:
			d = self._session.request('Firewall:getPinhole')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.Error('Cannot load IPv6 port forwarding rules.')	# Do not display a dialog as not all LB models have this API
			return

		i = self._patList.rowCount()
		for k in d:
			r = d[k]

			# If destination port is not set, this is a protocol forwarding rule -> skip
			aDestinationPort = r.get('DestinationPort', '')
			if len(aDestinationPort) == 0:
				continue

			self._patList.insertRow(i)

			aActiveStatus = r.get('Enable', False)
			self._patList.setItem(i, PatCol.Enabled, self.formatActiveTableWidget(aActiveStatus))

			aOrigin = r.get('Origin', '')
			self._patList.setItem(i, PatCol.Type, self.formatNatPatOriginTableWidget(aOrigin, True))

			aID = r.get('Id', '')
			self._patList.setItem(i, PatCol.Key, QtWidgets.QTableWidgetItem('v6_' + aID))

			if len(aID) > len(aOrigin) + 1:
				aID = aID[len(aOrigin) + 1:]
			self._patList.setItem(i, PatCol.ID, QtWidgets.QTableWidgetItem(aID))

			self._patList.setItem(i, PatCol.Description, QtWidgets.QTableWidgetItem(r.get('Description', '')))

			aProtocols = r.get('Protocol', '')
			self._patList.setItem(i, PatCol.Protocols, self.formatNatPatProtocolsTableWidget(aProtocols))

			self._patList.setItem(i, PatCol.IntPort, self.formatPortTableWidget(aDestinationPort))
			self._patList.setItem(i, PatCol.ExtPort, self.formatPortTableWidget(r.get('SourcePort', '')))

			aDestinationIP = r.get('DestinationIPAddress', '')
			self._patList.setItem(i, PatCol.DestIP, QtWidgets.QTableWidgetItem(aDestinationIP))
			self._patList.setItem(i, PatCol.Device, QtWidgets.QTableWidgetItem(self.getDeviceNameFromIp(aDestinationIP)))

			aExternalIPs = r.get('SourcePrefix', '')
			if len(aExternalIPs) == 0:
				aExternalIPs = lx('All')
			self._patList.setItem(i, PatCol.ExtIPs, QtWidgets.QTableWidgetItem(aExternalIPs))

			i += 1


	### Get the PAT rule object selected in the list
	def getSelectedPatRule(self):
		return self.getPatRuleFromList(self._patList.currentRow())


	### Get a PAT rule object from list row index
	def getPatRuleFromList(self, iIndex):
		if (iIndex >= 0) and (iIndex < self._patList.rowCount()):
			r = {}
			r['Enable'] = self._patList.item(iIndex, PatCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole) != 0
			r['Type'] = self._patList.item(iIndex, PatCol.Type).text()
			r['Name'] = self._patList.item(iIndex, PatCol.ID).text()
			r['Desc'] = self._patList.item(iIndex, PatCol.Description).text()
			p = self._patList.item(iIndex, PatCol.Protocols).text()
			r['ProtoNames'] = p
			r['ProtoNumbers'] = self.translateNatPatProtocols(p)
			p = self._patList.item(iIndex, PatCol.IntPort).text()
			if len(p):
				r['IntPort'] = p
			else:
				r['IntPort'] = None
			p = self._patList.item(iIndex, PatCol.ExtPort).text()
			if len(p):
				r['ExtPort'] = p
			else:
				r['ExtPort'] = None
			r['IP'] = self._patList.item(iIndex, PatCol.DestIP).text()
			e = self._patList.item(iIndex, PatCol.ExtIPs).text()
			if e == lx('All'):
				r['ExtIPs'] = ''
			else:
				r['ExtIPs'] = e
			return r
		else:
			return None


	### Check a PAT rule object consistency
	def checkPatRule(self, iRule):
		if iRule.get('Enable') is None:
			LmTools.Error('Rule as no Enable tag.')
			return False

		t = iRule.get('Type', 'UNK')
		if t not in RULE_PAT_TYPES:
			LmTools.Error('Rule has unknown {} type.'.format(t))
			return False

		if len(iRule.get('Name', '')) == 0:
			LmTools.Error('Rule has no Name.')
			return False

		aProtocols = iRule.get('ProtoNumbers', '')
		if len(aProtocols) == 0:
			LmTools.Error('Rule has no protocol.')
			return False

		for p in aProtocols.split(','):
			n = PROTOCOL_NAMES.get(p)
			if n is None:
				LmTools.Error('Rule has wrong protocol {} set.'.format(p))
				return False
			n = int(p)
			if (n != Protocols.TCP) and (n != Protocols.UDP):
				LmTools.Error('Rule has wrong protocol {} set.'.format(p))
				return False

		n = iRule.get('IntPort', '')
		if (n is not None) and len(n):
			if not LmTools.isTcpUdpPort(n):
				LmTools.Error('Rule has wrong internal port {} set.'.format(n))
				return False

		n = iRule.get('ExtPort', '')
		if (n is not None) and len(n):
			if not LmTools.isTcpUdpPort(n):
				LmTools.Error('Rule has wrong external port {} set.'.format(n))
				return False

		aIP = iRule.get('IP', '')
		if len(aIP) == 0:
			return False
		if t == RULE_TYPE_IPv6:
			if not LmTools.IsIPv6(aIP):
				LmTools.Error('Rule has wrong IPv6 {} set.'.format(aIP))
				return False
		else:
			if not LmTools.IsIPv4(aIP):
				LmTools.Error('Rule has wrong IPv4 {} set.'.format(aIP))
				return False

		e = iRule.get('ExtIPs', '')
		if len(e):
			aExtIPs = e.split(',')
			for aIP in aExtIPs:
				if len(aIP) == 0:
					LmTools.Error('Rule external IPs has an empty IP address.')
					return False

				if t == RULE_TYPE_IPv6:
					if not LmTools.IsIPv6(aIP):
						LmTools.Error('Rule external IPs has a wrong IPv6 {} set.'.format(aIP))
						return False
				else:
					if not LmTools.IsIPv4(aIP):
						LmTools.Error('Rule external IPs has a wrong IPv4 {} set.'.format(aIP))
						return False

		return True


	### Save a PAT rule in Livebox, return True if successful
	def savePatRule(self, iRule, iSilent = False):
		if iRule['Type'] == RULE_TYPE_IPv6:
			return self.saveIPv6PatRule(iRule, iSilent)
		return self.saveIPv4PatRule(iRule, iSilent)


	### Save a IPv4 PAT rule in Livebox, return True if successful
	def saveIPv4PatRule(self, iRule, iSilent = False):
		# Map rule to Livebox model
		r = {}
		r['id'] = iRule['Name']
		r['internalPort'] = iRule['IntPort']
		p = iRule['ExtPort']
		if p is not None:
			r['externalPort'] = p
		r['destinationIPAddress'] = iRule['IP']
		r['enable'] = iRule['Enable']
		r['persistent'] = True
		r['protocol'] = iRule['ProtoNumbers']
		r['description'] = iRule['Desc']
		r['sourceInterface'] = 'data'
		if iRule['Type'] == RULE_TYPE_IPv4:
			r['origin'] = 'webui'
		else:
			r['origin'] = 'upnp'
		r['destinationMACAddress'] = ''
		aExternalIPs = iRule['ExtIPs']
		if len(aExternalIPs):
			r['sourcePrefix'] = aExternalIPs

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:setPortForwarding', r)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			if not iSilent:
				self.displayError('Firewall setPortForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				if not iSilent:
					self.displayError(aErrors)
				return False
			return True
		else:
			if not iSilent:
				self.displayError('Firewall setPortForwarding query failed.')
			return False


	### Save a IPv6 PAT rule in Livebox, return True if successful
	def saveIPv6PatRule(self, iRule, iSilent = False):
		# Map rule to Livebox model
		r = {}
		r['id'] = iRule['Name']
		r['origin'] = 'webui'
		r['sourceInterface'] = 'data'
		p = iRule['ExtPort']
		if IPV6_SOURCE_PORT_WORKING and (p is not None):
			r['sourcePort'] = p
		else:
			r['sourcePort'] = ''
		r['destinationPort'] = iRule['IntPort']
		r['destinationIPAddress'] = iRule['IP']
		r['sourcePrefix'] = iRule['ExtIPs']
		r['protocol'] = iRule['ProtoNumbers']
		r['ipversion'] = 6
		r['enable'] = iRule['Enable']
		r['persistent'] = True
		r['description'] = iRule['Desc']
		r['destinationMACAddress'] = ''

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:setPinhole', r)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall setPinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return False
			return True
		else:
			self.displayError('Firewall setPinhole query failed.')
			return False


	### Delete a PAT rule from Livebox, return True if successful
	def delPatRule(self, iRule):
		if iRule['Type'] == RULE_TYPE_IPv6:
			return self.delIPv6PatRule(iRule)
		return self.delIPv4PatRule(iRule)


	### Delete a IPv4 PAT rule from Livebox, return True if successful
	def delIPv4PatRule(self, iRule):
		# Build parameters
		r = {}
		if iRule['Type'] == RULE_TYPE_IPv4:
			o = 'webui'
		else:
			o = 'upnp'
		r['id'] = o + '_' + iRule['Name']
		r['destinationIPAddress'] = iRule['IP']
		r['origin'] = o

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:deletePortForwarding', r)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall deletePortForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return False
			return aReply['status']
		else:
			self.displayError('Firewall deletePortForwarding query failed.')
			return False


	### Delete a IPv6 PAT rule from Livebox, return True if successful
	def delIPv6PatRule(self, iRule):
		# Build parameters
		r = {}
		r['id'] = 'webui_' + iRule['Name']
		r['origin'] = 'webui'

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:deletePinhole', r)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall deletePinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return False
			return aReply['status']
		else:
			self.displayError('Firewall deletePinhole query failed.')
			return False


	### Delete all IPv4 or UPnP PAT rules from Livebox, return True if successful
	def delAllIPv4PatRule(self, iUPnP):
		# Build parameters
		if iUPnP:
			o = 'upnp'
		else:
			o = 'webui'

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:deletePortForwarding', { 'origin': o })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall deletePortForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return False
			return aReply['status']
		else:
			self.displayError('Firewall deletePortForwarding query failed.')
			return False


	### Refresh PTF list
	def refreshPtfList(self):
		self._ptfList.clearContents()
		self._ptfList.setRowCount(0)
		self.loadDeviceIpNameMap()
		self.loadPtfRules()


	### Load PTF rules
	def loadPtfRules(self):
		self.startTask(lx('Loading protocol forwarding rules...'))
		self._ptfList.setSortingEnabled(False)

		# IPv4 types
		self.loadIPv4PtfRules()

		# IPv6 types
		self.loadIPv6PtfRules()

		self._ptfList.sortItems(PtfCol.Type, QtCore.Qt.SortOrder.AscendingOrder)
		self._ptfList.setSortingEnabled(True)

		self._ptfList.setCurrentCell(-1, -1)
		self.ptfListClick()

		self.endTask()


	### Load IPv4 PTF rules
	def loadIPv4PtfRules(self):
		try:
			d = self._session.request('Firewall:getProtocolForwarding')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			self.displayError('Cannot load IPv4 protocol forwarding rules.')
			return

		i = self._ptfList.rowCount()
		for k in d:
			self._ptfList.insertRow(i)
			r = d[k]

			aActiveStatus = r.get('Status', 'Disabled') == 'Enabled'
			self._ptfList.setItem(i, PtfCol.Enabled, self.formatActiveTableWidget(aActiveStatus))

			aOrigin = r.get('SourceInterface', '')
			if aOrigin == 'data':
				aType = RULE_TYPE_IPv4
			else:
				aType = aOrigin
			self._ptfList.setItem(i, PtfCol.Type, QtWidgets.QTableWidgetItem(aType))

			aID = r.get('Id', '')
			self._ptfList.setItem(i, PtfCol.Key, QtWidgets.QTableWidgetItem('v4_' + aID))
			self._ptfList.setItem(i, PtfCol.ID, QtWidgets.QTableWidgetItem(aID))

			self._ptfList.setItem(i, PtfCol.Description, QtWidgets.QTableWidgetItem(r.get('Description', '')))

			aProtocols = r.get('Protocol', '')
			self._ptfList.setItem(i, PtfCol.Protocols, self.formatNatPatProtocolsTableWidget(aProtocols))

			aDestinationIP = r.get('DestinationIPAddress', '')
			self._ptfList.setItem(i, PtfCol.DestIP, QtWidgets.QTableWidgetItem(aDestinationIP))
			self._ptfList.setItem(i, PtfCol.Device, QtWidgets.QTableWidgetItem(self.getDeviceNameFromIp(aDestinationIP)))

			aExternalIPs = r.get('SourcePrefix', '')
			if len(aExternalIPs) == 0:
				aExternalIPs = lx('All')
			self._ptfList.setItem(i, PtfCol.ExtIPs, QtWidgets.QTableWidgetItem(aExternalIPs))

			i += 1


	### Load IPv6 PTF rules
	def loadIPv6PtfRules(self):
		try:
			d = self._session.request('Firewall:getPinhole')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.Error('Cannot load IPv6 protocol forwarding rules.')	# Do not display a dialog as not all LB models have this API
			return

		i = self._ptfList.rowCount()
		for k in d:
			r = d[k]

			# If destination port is set, this is a port forwarding rule -> skip
			aDestinationPort = r.get('DestinationPort', '')
			if len(aDestinationPort):
				continue

			self._ptfList.insertRow(i)

			aActiveStatus = r.get('Status', 'Disabled') == 'Enabled'
			self._ptfList.setItem(i, PtfCol.Enabled, self.formatActiveTableWidget(aActiveStatus))

			aOrigin = r.get('Origin', '')
			self._ptfList.setItem(i, PtfCol.Type, self.formatNatPatOriginTableWidget(aOrigin, True))

			aID = r.get('Id', '')
			self._ptfList.setItem(i, PtfCol.Key, QtWidgets.QTableWidgetItem('v6_' + aID))

			if len(aID) > len(aOrigin) + 1:
				aID = aID[len(aOrigin) + 1:]
			self._ptfList.setItem(i, PtfCol.ID, QtWidgets.QTableWidgetItem(aID))

			self._ptfList.setItem(i, PtfCol.Description, QtWidgets.QTableWidgetItem(r.get('Description', '')))

			aProtocols = r.get('Protocol', '')
			self._ptfList.setItem(i, PtfCol.Protocols, self.formatNatPatProtocolsTableWidget(aProtocols))

			aDestinationIP = r.get('DestinationIPAddress', '')
			self._ptfList.setItem(i, PtfCol.DestIP, QtWidgets.QTableWidgetItem(aDestinationIP))
			self._ptfList.setItem(i, PtfCol.Device, QtWidgets.QTableWidgetItem(self.getDeviceNameFromIp(aDestinationIP)))

			aExternalIPs = r.get('SourcePrefix', '')
			if len(aExternalIPs) == 0:
				aExternalIPs = lx('All')
			self._ptfList.setItem(i, PtfCol.ExtIPs, QtWidgets.QTableWidgetItem(aExternalIPs))

			i += 1


	### Get the PTF rule object selected in the list
	def getSelectedPtfRule(self):
		return self.getPtfRuleFromList(self._ptfList.currentRow())


	### Get a PTF rule object from list row index
	def getPtfRuleFromList(self, iIndex):
		if (iIndex >= 0) and (iIndex < self._ptfList.rowCount()):
			r = {}
			r['Enable'] = self._ptfList.item(iIndex, PtfCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole) != 0
			r['Type'] = self._ptfList.item(iIndex, PtfCol.Type).text()
			r['Name'] = self._ptfList.item(iIndex, PtfCol.ID).text()
			r['Desc'] = self._ptfList.item(iIndex, PtfCol.Description).text()
			p = self._ptfList.item(iIndex, PtfCol.Protocols).text()
			r['ProtoNames'] = p
			r['ProtoNumbers'] = self.translateNatPatProtocols(p)
			r['IP'] = self._ptfList.item(iIndex, PtfCol.DestIP).text()
			e = self._ptfList.item(iIndex, PtfCol.ExtIPs).text()
			if e == lx('All'):
				r['ExtIPs'] = ''
			else:
				r['ExtIPs'] = e
			return r
		else:
			return None


	### Check a PTF rule object consistency
	def checkPtfRule(self, iRule):
		if iRule.get('Enable') is None:
			LmTools.Error('Rule as no Enable tag.')
			return False

		t = iRule.get('Type', 'UNK')
		if t not in RULE_PTF_TYPES:
			LmTools.Error('Rule has unknown {} type.'.format(t))
			return False

		if len(iRule.get('Name', '')) == 0:
			LmTools.Error('Rule has no Name.')
			return False

		aProtocols = iRule.get('ProtoNumbers', '')
		if len(aProtocols) == 0:
			LmTools.Error('Rule has no protocol.')
			return False

		for p in aProtocols.split(','):
			n = PROTOCOL_NAMES.get(p)
			if n is None:
				LmTools.Error('Rule has wrong protocol {} set.'.format(p))
				return False
			n = int(p)
			if t == RULE_TYPE_IPv6:
				aICMP = Protocols.ICMPv6
			else:
				aICMP = Protocols.ICMP
			if ((n != Protocols.TCP) and
				(n != Protocols.UDP) and
				(n != Protocols.AH) and
				(n != Protocols.GRE) and
				(n != Protocols.ESP) and
				(n != aICMP)):
				LmTools.Error('Rule has wrong protocol {} set.'.format(p))
				return False

		aIP = iRule.get('IP', '')
		if len(aIP) == 0:
			return False
		if t == RULE_TYPE_IPv6:
			if not LmTools.IsIPv6(aIP):
				LmTools.Error('Rule has wrong IPv6 {} set.'.format(aIP))
				return False
		else:
			if not LmTools.IsIPv4(aIP):
				LmTools.Error('Rule has wrong IPv4 {} set.'.format(aIP))
				return False

		e = iRule.get('ExtIPs', '')
		if len(e):
			aExtIPs = e.split(',')
			for aIP in aExtIPs:
				if len(aIP) == 0:
					LmTools.Error('Rule external IPs has an empty IP address.')
					return False

				if t == RULE_TYPE_IPv6:
					if not LmTools.IsIPv6(aIP):
						LmTools.Error('Rule external IPs has a wrong IPv6 {} set.'.format(aIP))
						return False
				else:
					if not LmTools.IsIPv4(aIP):
						LmTools.Error('Rule external IPs has a wrong IPv4 {} set.'.format(aIP))
						return False

		return True


	### Save a PTF rule in Livebox, return True if successful
	def savePtfRule(self, iRule, iSilent = False):
		if iRule['Type'] == RULE_TYPE_IPv6:
			return self.saveIPv6PtfRule(iRule, iSilent)
		return self.saveIPv4PtfRule(iRule, iSilent)


	### Save a IPv4 PTF rule in Livebox, return True if successful
	def saveIPv4PtfRule(self, iRule, iSilent = False):
		# Map rule to Livebox model
		r = {}
		r['id'] = iRule['Name']
		r['enable'] = iRule['Enable']
		r['destinationIPAddress'] = iRule['IP']
		r['protocol'] = iRule['ProtoNumbers']
		r['persistent'] = True
		r['description'] = iRule['Desc']
		aExternalIPs = iRule['ExtIPs']
		if len(aExternalIPs):
			r['sourcePrefix'] = aExternalIPs

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:setProtocolForwarding', r)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			if not iSilent:
				self.displayError('Firewall setProtocolForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				if not iSilent:
					self.displayError(aErrors)
				return False
			return True
		else:
			if not iSilent:
				self.displayError('Firewall setProtocolForwarding query failed.')
			return False


	### Save a IPv6 PTF rule in Livebox, return True if successful
	def saveIPv6PtfRule(self, iRule, iSilent = False):
		# Map rule to Livebox model
		r = {}
		r['id'] = iRule['Name']
		r['origin'] = 'webui'
		r['sourceInterface'] = 'data'
		r['sourcePort'] = ''
		r['destinationPort'] = ''
		r['destinationIPAddress'] = iRule['IP']
		r['sourcePrefix'] = iRule['ExtIPs']
		r['protocol'] = iRule['ProtoNumbers']
		r['ipversion'] = 6
		r['enable'] = iRule['Enable']
		r['persistent'] = True
		r['description'] = iRule['Desc']
		r['destinationMACAddress'] = ''

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:setPinhole', r)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall setPinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return False
			return True
		else:
			self.displayError('Firewall setPinhole query failed.')
			return False


	### Delete a PTF rule from Livebox, return True if successful
	def delPtfRule(self, iRule):
		if iRule['Type'] == RULE_TYPE_IPv6:
			return self.delIPv6PtfRule(iRule)
		return self.delIPv4PtfRule(iRule)


	### Delete a IPv4 PTF rule from Livebox, return True if successful
	def delIPv4PtfRule(self, iRule):
		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:deleteProtocolForwarding', { 'id': iRule['Name'] })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall deleteProtocolForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return False
			return aReply['status']
		else:
			self.displayError('Firewall deleteProtocolForwarding query failed.')
			return False


	### Delete a IPv6 PTF rule from Livebox, return True if successful
	def delIPv6PtfRule(self, iRule):
		# Build parameters
		r = {}
		r['id'] = 'webui_' + iRule['Name']
		r['origin'] = 'webui'

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall:deletePinhole', r)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall deletePinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return False
			return aReply['status']
		else:
			self.displayError('Firewall deletePinhole query failed.')
			return False


	### Commit Firewall rule changes, return True if successful
	def commitNatPatRuleChange(self):
		try:
			aReply = self._session.request('Firewall:commit')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.Error('Firewall commit query error.')
			return False

		if aReply is not None:
			return aReply.get('status', False)
		else:
			LmTools.Error('Firewall commit query failed.')
			return False


	### Translate Protocols for Livebox API
	def translateNatPatProtocols(self, iProtocols):
		r = ''
		for p in iProtocols.split('/'):
			n = self._protocolNumbers.get(p, None)
			if n is not None:
				if len(r):
					r += ','
				r += n
		return r


	### Format Origin cell
	@staticmethod
	def formatNatPatOriginTableWidget(iOrigin, iIPv6):
		###WARNING### : names must match those set by NatPatRuleTypeDialog.getTypes() method
		if iOrigin == 'webui':
			if iIPv6:
				return QtWidgets.QTableWidgetItem(RULE_TYPE_IPv6)
			else:
				return QtWidgets.QTableWidgetItem(RULE_TYPE_IPv4)
		elif iOrigin == 'upnp':
			return QtWidgets.QTableWidgetItem(RULE_TYPE_UPnP)
		else:
			return QtWidgets.QTableWidgetItem(iOrigin)


	### Format Protocols cell
	@staticmethod
	def formatNatPatProtocolsTableWidget(iProtocols):
		r = ''
		for p in iProtocols.split(','):
			if len(r):
				r += '/'
			r += PROTOCOL_NAMES.get(p, 'UNK')
		return QtWidgets.QTableWidgetItem(r)


	### Format Port cell
	@staticmethod
	def formatPortTableWidget(iPort):
		aPort = LmTools.NumericSortItem(iPort)
		p = iPort.split('-')[0]		# If range is used, sort with the first port
		try:
			i = int(p)
		except:
			i = 0
		aPort.setData(QtCore.Qt.ItemDataRole.UserRole, i)
		return aPort



# ############# PAT rule dialog #############
class PatRuleDialog(QtWidgets.QDialog):
	def __init__(self, iRule = None, iParent = None):
		super(PatRuleDialog, self).__init__(iParent)
		self.resize(390, 420)

		self._ignoreSignal = False

		self._enableCheckBox = QtWidgets.QCheckBox(lrx('Enabled'), objectName = 'enableCheckbox')

		aTypeLabel = QtWidgets.QLabel(lrx('Type'), objectName = 'typeLabel')
		self._typeCombo = QtWidgets.QComboBox(objectName = 'typeCombo')
		self._typeCombo.addItems(RULE_PAT_TYPES)
		self._typeCombo.activated.connect(self.typeSelected)

		aNameLabel = QtWidgets.QLabel(lrx('Name'), objectName = 'nameLabel')
		self._nameEdit = QtWidgets.QLineEdit(objectName = 'nameEdit')
		self._nameEdit.textChanged.connect(self.nameTyped)

		aDescLabel = QtWidgets.QLabel(lrx('Description'), objectName = 'descLabel')
		self._descEdit = LmTools.MultiLinesEdit(objectName = 'descEdit')
		self._descEdit.setTabChangesFocus(True)
		self._descEdit.setLineNumber(2)

		aProtocolsLabel = QtWidgets.QLabel(lrx('Protocols'), objectName = 'protocolsLabel')
		self._tcpCheckBox = QtWidgets.QCheckBox(lrx('TCP'), objectName = 'tcpCheckbox')
		self._tcpCheckBox.clicked.connect(self.protocolClick)
		self._udpCheckBox = QtWidgets.QCheckBox(lrx('UDP'), objectName = 'udpCheckbox')
		self._udpCheckBox.clicked.connect(self.protocolClick)
		aProtocolsBox = QtWidgets.QHBoxLayout()
		aProtocolsBox.setSpacing(10)
		aProtocolsBox.addWidget(self._tcpCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aProtocolsBox.addWidget(self._udpCheckBox, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

		aPortRegExp = QtCore.QRegularExpression(LmTools.PORTS_RS)
		aPortValidator = QtGui.QRegularExpressionValidator(aPortRegExp)

		aIntPortLabel = QtWidgets.QLabel(lrx('Internal Port'), objectName = 'intPortLabel')
		self._intPortEdit = QtWidgets.QLineEdit(objectName = 'intPortEdit')
		self._intPortEdit.setValidator(aPortValidator)

		aExtPortLabel = QtWidgets.QLabel(lrx('External Port'), objectName = 'extPortLabel')
		self._extPortEdit = QtWidgets.QLineEdit(objectName = 'extPortEdit')
		self._extPortEdit.setValidator(aPortValidator)

		aPortBox = QtWidgets.QHBoxLayout()
		aPortBox.addWidget(self._intPortEdit, 1, QtCore.Qt.AlignmentFlag.AlignLeft)
		aPortBox.addWidget(aExtPortLabel, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aPortBox.addWidget(self._extPortEdit, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

		aDeviceLabel = QtWidgets.QLabel(lrx('Device'), objectName = 'deviceLabel')
		self._deviceCombo = QtWidgets.QComboBox(objectName = 'deviceCombo')
		self._deviceCombo.activated.connect(self.deviceSelected)

		aIpLabel = QtWidgets.QLabel(lrx('IP Address'), objectName = 'ipLabel')
		self._ipEdit = QtWidgets.QLineEdit(objectName = 'ipEdit')
		self._ipEdit.textChanged.connect(self.ipTyped)

		aExtIPsLabel = QtWidgets.QLabel(lrx('External IPs'), objectName = 'extIPsLabel')
		self._extIPsEdit = LmTools.MultiLinesEdit(objectName = 'extIPsEdit')
		self._extIPsEdit.setTabChangesFocus(True)
		self._extIPsEdit.setLineNumber(2)

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(self._enableCheckBox, 0, 0)
		aGrid.addWidget(aTypeLabel, 1, 0)
		aGrid.addWidget(self._typeCombo, 1, 1)
		aGrid.addWidget(aNameLabel, 2, 0)
		aGrid.addWidget(self._nameEdit, 2, 1)
		aGrid.addWidget(aDescLabel, 3, 0)
		aGrid.addWidget(self._descEdit, 3, 1)
		aGrid.addWidget(aProtocolsLabel, 4, 0)
		aGrid.addLayout(aProtocolsBox, 4, 1)
		aGrid.addWidget(aIntPortLabel, 5, 0)
		aGrid.addLayout(aPortBox, 5, 1)
		aGrid.addWidget(aDeviceLabel, 6, 0)
		aGrid.addWidget(self._deviceCombo, 6, 1)
		aGrid.addWidget(aIpLabel, 7, 0)
		aGrid.addWidget(self._ipEdit, 7, 1)
		aGrid.addWidget(aExtIPsLabel, 8, 0)
		aGrid.addWidget(self._extIPsEdit, 8, 1)

		self._okButton = QtWidgets.QPushButton(lrx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lrx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'patrule')

		self.setWindowTitle(lrx('Port Forwarding Rule'))

		if iRule is None:
			self.setDefault()
		else:
			self.setRule(iRule)

		self._nameEdit.setFocus()
		self.setModal(True)
		self.show()


	# Set default values, for rule creation
	def setDefault(self):
		self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		i = RULE_PAT_TYPES.index(RULE_TYPE_IPv4)
		self._typeCombo.setCurrentIndex(i)
		self.typeSelected(i)
		self._nameEdit.setText('')
		self._descEdit.setPlainText('')
		self._tcpCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		self._udpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._intPortEdit.setText('1000')
		self._extPortEdit.setText('1000')
		self._deviceCombo.setCurrentIndex(0)
		self._ipEdit.setText('')
		self._extIPsEdit.setPlainText('')
		self.setOkButtonState()


	# Set values to existing rule, for edition
	def setRule(self, iRule):
		if iRule['Enable']:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		i = RULE_PAT_TYPES.index(iRule['Type'])
		self._typeCombo.setCurrentIndex(i)
		self.typeSelected(i)

		self._nameEdit.setText(iRule['Name'])
		self._descEdit.setPlainText(iRule['Desc'])

		p = iRule['ProtoNames'].split('/')

		if PROTOCOL_NAMES[str(Protocols.TCP.value)] in p:
			self._tcpCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._tcpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if PROTOCOL_NAMES[str(Protocols.UDP.value)] in p:
			self._udpCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._udpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		self._intPortEdit.setText(iRule['IntPort'])
		self._extPortEdit.setText(iRule['ExtPort'])

		aIP = iRule['IP']
		self._ipEdit.setText(aIP)
		self.ipTyped(aIP)

		self._extIPsEdit.setPlainText(iRule['ExtIPs'])

		self.setOkButtonState()


	def getRule(self):
		r = {}
		r['Enable'] = self.getEnabled()
		r['Type'] = self.getType()
		r['Name'] = self.getName()
		r['Desc'] = self.getDescription()
		p = self.getProtocols()
		r['ProtoNames'] = p
		r['ProtoNumbers'] = self.parent().translateNatPatProtocols(p)
		r['IntPort'] = self.getIntPort()
		r['ExtPort'] = self.getExtPort()
		r['IP'] = self.getIP()
		r['ExtIPs'] = self.getExtIPs()
		return r


	def typeSelected(self, iIndex):
		# Load corresponding devices
		self.loadDeviceList()

		# Adjust IP field validator
		if self.getType() == RULE_TYPE_IPv6:
			aIPRegExp = QtCore.QRegularExpression('^' + LmTools.IPv6_RS + '$')
			if not IPV6_SOURCE_PORT_WORKING:
				self._extPortEdit.setEnabled(False)
				self._extPortEdit.setText('')
		else:
			aIPRegExp = QtCore.QRegularExpression('^' + LmTools.IPv4_RS + '$')
			if not IPV6_SOURCE_PORT_WORKING:
				self._extPortEdit.setEnabled(True)
		aIPValidator = QtGui.QRegularExpressionValidator(aIPRegExp)
		self._ipEdit.setValidator(aIPValidator)


	def nameTyped(self, iText):
		self.setOkButtonState()


	def protocolClick(self):
		self.setOkButtonState()


	def deviceSelected(self, iIndex):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			self._ipEdit.setText(self._deviceCombo.currentData())
			self._ignoreSignal = False


	def ipTyped(self, iText):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			i = self._deviceCombo.findData(iText)
			if i < 0:
				i = 0
			self._deviceCombo.setCurrentIndex(i)
			self._ignoreSignal = False

		self.setOkButtonState()


	def setOkButtonState(self):
		self._okButton.setDisabled((len(self.getName()) == 0) or
								   (len(self.getIP()) == 0) or
								   (len(self.getProtocols()) == 0))


	def loadDeviceList(self):
		t = self.getType()
		aDeviceMap = self.parent()._deviceIpNameMap
		self._deviceCombo.clear()

		# If type is UPnP load IPv4 devices
		if t == RULE_TYPE_UPnP:
			t = RULE_TYPE_IPv4

		# Load matching devices / IPs
		for i in aDeviceMap:
			if aDeviceMap[i]['IPVers'] == t:
				self._deviceCombo.addItem(self.parent().getDeviceNameFromIp(i), userData = i)

		# Sort by name
		self._deviceCombo.model().sort(0)

		# Insert unknown device at the beginning
		self._deviceCombo.insertItem(0, lrx('-Unknown-'), userData = '')
		self._deviceCombo.setCurrentIndex(0)
		self.deviceSelected(0)


	def accept(self):
		t = self.getType()

		# Validate IP address
		aIP = self.getIP()
		if t == RULE_TYPE_IPv6:
			if not LmTools.IsIPv6(aIP):
				self.parent().displayError('{} is not a valid IPv6 address.'.format(aIP))
				self._ipEdit.setFocus()
				return
		else:
			if not LmTools.IsIPv4(aIP):
				self.parent().displayError('{} is not a valid IPv4 address.'.format(aIP))
				self._ipEdit.setFocus()
				return

		# Validate external IP addresses
		e = self.getExtIPs()
		if len(e):
			aExtIPs = e.split(',')
			for aIP in aExtIPs:
				if len(aIP) == 0:
					self.parent().displayError('Empty IP address.')
					self._extIPsEdit.setFocus()
					return

				if t == RULE_TYPE_IPv6:
					if not LmTools.IsIPv6(aIP):
						self.parent().displayError('{} is not a valid IPv6 address.'.format(aIP))
						self._extIPsEdit.setFocus()
						return
				else:
					if not LmTools.IsIPv4(aIP):
						self.parent().displayError('{} is not a valid IPv4 address.'.format(aIP))
						self._extIPsEdit.setFocus()
						return

		super().accept()


	def getEnabled(self):
		return self._enableCheckBox.checkState() == QtCore.Qt.CheckState.Checked


	def getType(self):
		return self._typeCombo.currentText()


	def getName(self):
		return self._nameEdit.text()


	def getDescription(self):
		return self._descEdit.toPlainText()


	def getProtocols(self):
		if self._tcpCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			if self._udpCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
				return PROTOCOL_NAMES[str(Protocols.TCP.value)] + '/' + PROTOCOL_NAMES[str(Protocols.UDP.value)]
			else:
				return PROTOCOL_NAMES[str(Protocols.TCP.value)]
		elif self._udpCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			return PROTOCOL_NAMES[str(Protocols.UDP.value)]
		else:
			return ''


	def getIntPort(self):
		p = self._intPortEdit.text()
		if len(p):
			return p
		return None


	def getExtPort(self):
		p = self._extPortEdit.text()
		if len(p):
			return p
		return None


	def getIP(self):
		return self._ipEdit.text()


	def getExtIPs(self):
		return self._extIPsEdit.toPlainText()



# ############# PTF rule dialog #############
class PtfRuleDialog(QtWidgets.QDialog):
	def __init__(self, iRule = None, iParent = None):
		super(PtfRuleDialog, self).__init__(iParent)
		self.resize(390, 380)

		self._ignoreSignal = False

		self._enableCheckBox = QtWidgets.QCheckBox(lfx('Enabled'), objectName = 'enableCheckbox')

		aTypeLabel = QtWidgets.QLabel(lfx('Type'), objectName = 'typeLabel')
		self._typeCombo = QtWidgets.QComboBox(objectName = 'typeCombo')
		self._typeCombo.addItems(RULE_PTF_TYPES)
		self._typeCombo.activated.connect(self.typeSelected)

		aNameLabel = QtWidgets.QLabel(lfx('Name'), objectName = 'nameLabel')
		self._nameEdit = QtWidgets.QLineEdit(objectName = 'nameEdit')
		self._nameEdit.textChanged.connect(self.nameTyped)

		aDescLabel = QtWidgets.QLabel(lfx('Description'), objectName = 'descLabel')
		self._descEdit = LmTools.MultiLinesEdit(objectName = 'descEdit')
		self._descEdit.setTabChangesFocus(True)
		self._descEdit.setLineNumber(2)

		aProtocolsLabel = QtWidgets.QLabel(lfx('Protocols'), objectName = 'protocolsLabel')
		self._tcpCheckBox = QtWidgets.QCheckBox(lfx('TCP'), objectName = 'tcpCheckbox')
		self._tcpCheckBox.clicked.connect(self.protocolClick)
		self._udpCheckBox = QtWidgets.QCheckBox(lfx('UDP'), objectName = 'udpCheckbox')
		self._udpCheckBox.clicked.connect(self.protocolClick)
		self._ahCheckBox = QtWidgets.QCheckBox(lfx('AH'), objectName = 'ahCheckbox')
		self._ahCheckBox.clicked.connect(self.protocolClick)
		self._greCheckBox = QtWidgets.QCheckBox(lfx('GRE'), objectName = 'greCheckbox')
		self._greCheckBox.clicked.connect(self.protocolClick)
		self._espCheckBox = QtWidgets.QCheckBox(lfx('ESP'), objectName = 'espCheckbox')
		self._espCheckBox.clicked.connect(self.protocolClick)
		self._icmpCheckBox = QtWidgets.QCheckBox(lfx('ICMP'), objectName = 'icmpCheckbox')
		self._icmpCheckBox.clicked.connect(self.protocolClick)
		aProtocolsBox = QtWidgets.QHBoxLayout()
		aProtocolsBox.setSpacing(10)
		aProtocolsBox.addWidget(self._tcpCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aProtocolsBox.addWidget(self._udpCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aProtocolsBox.addWidget(self._ahCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aProtocolsBox.addWidget(self._greCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aProtocolsBox.addWidget(self._espCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aProtocolsBox.addWidget(self._icmpCheckBox, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

		aPortBox = QtWidgets.QHBoxLayout()
		aPortBox.setSpacing(25)

		aDeviceLabel = QtWidgets.QLabel(lfx('Device'), objectName = 'deviceLabel')
		self._deviceCombo = QtWidgets.QComboBox(objectName = 'deviceCombo')
		self._deviceCombo.activated.connect(self.deviceSelected)

		aIpLabel = QtWidgets.QLabel(lfx('IP Address'), objectName = 'ipLabel')
		self._ipEdit = QtWidgets.QLineEdit(objectName = 'ipEdit')
		self._ipEdit.textChanged.connect(self.ipTyped)

		aExtIPsLabel = QtWidgets.QLabel(lfx('External IPs'), objectName = 'extIPsLabel')
		self._extIPsEdit = LmTools.MultiLinesEdit(objectName = 'extIPsEdit')
		self._extIPsEdit.setTabChangesFocus(True)
		self._extIPsEdit.setLineNumber(2)

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(self._enableCheckBox, 0, 0)
		aGrid.addWidget(aTypeLabel, 1, 0)
		aGrid.addWidget(self._typeCombo, 1, 1)
		aGrid.addWidget(aNameLabel, 2, 0)
		aGrid.addWidget(self._nameEdit, 2, 1)
		aGrid.addWidget(aDescLabel, 3, 0)
		aGrid.addWidget(self._descEdit, 3, 1)
		aGrid.addWidget(aProtocolsLabel, 4, 0)
		aGrid.addLayout(aProtocolsBox, 4, 1)
		aGrid.addWidget(aDeviceLabel, 5, 0)
		aGrid.addWidget(self._deviceCombo, 5, 1)
		aGrid.addWidget(aIpLabel, 6, 0)
		aGrid.addWidget(self._ipEdit, 6, 1)
		aGrid.addWidget(aExtIPsLabel, 7, 0)
		aGrid.addWidget(self._extIPsEdit, 7, 1)

		self._okButton = QtWidgets.QPushButton(lfx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lfx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'ptfrule')

		self.setWindowTitle(lfx('Protocol Forwarding Rule'))

		if iRule is None:
			self.setDefault()
		else:
			self.setRule(iRule)

		self._nameEdit.setFocus()
		self.setModal(True)
		self.show()


	# Set default values, for rule creation
	def setDefault(self):
		self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		i = RULE_PTF_TYPES.index(RULE_TYPE_IPv4)
		self._typeCombo.setCurrentIndex(i)
		self.typeSelected(i)
		self._nameEdit.setText('')
		self._descEdit.setPlainText('')
		self._tcpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._udpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._ahCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		self._greCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._espCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._icmpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._deviceCombo.setCurrentIndex(0)
		self._ipEdit.setText('')
		self._extIPsEdit.setPlainText('')
		self.setOkButtonState()


	# Set values to existing rule, for edition
	def setRule(self, iRule):
		if iRule['Enable']:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._enableCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		t = iRule['Type']
		i = RULE_PTF_TYPES.index(t)
		self._typeCombo.setCurrentIndex(i)
		self.typeSelected(i)

		self._nameEdit.setText(iRule['Name'])
		self._descEdit.setPlainText(iRule['Desc'])

		p = iRule['ProtoNames'].split('/')

		if PROTOCOL_NAMES[str(Protocols.TCP.value)] in p:
			self._tcpCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._tcpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if PROTOCOL_NAMES[str(Protocols.UDP.value)] in p:
			self._udpCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._udpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if PROTOCOL_NAMES[str(Protocols.AH.value)] in p:
			self._ahCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._ahCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if PROTOCOL_NAMES[str(Protocols.GRE.value)] in p:
			self._greCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._greCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if PROTOCOL_NAMES[str(Protocols.ESP.value)] in p:
			self._espCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._espCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		if t == RULE_TYPE_IPv6:
			aICMP = Protocols.ICMPv6.value
		else:
			aICMP = Protocols.ICMP.value
		if PROTOCOL_NAMES[str(aICMP)] in p:
			self._icmpCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._icmpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		aIP = iRule['IP']
		self._ipEdit.setText(aIP)
		self.ipTyped(aIP)

		self._extIPsEdit.setPlainText(iRule['ExtIPs'])

		self.setOkButtonState()


	def getRule(self):
		r = {}
		r['Enable'] = self.getEnabled()
		r['Type'] = self.getType()
		r['Name'] = self.getName()
		r['Desc'] = self.getDescription()
		p = self.getProtocols()
		r['ProtoNames'] = p
		r['ProtoNumbers'] = self.parent().translateNatPatProtocols(p)
		r['IP'] = self.getIP()
		r['ExtIPs'] = self.getExtIPs()
		return r


	def typeSelected(self, iIndex):
		# Load corresponding devices
		self.loadDeviceList()

		# Adjust IP field validator
		if self.getType() == RULE_TYPE_IPv6:
			aIPRegExp = QtCore.QRegularExpression('^' + LmTools.IPv6_RS + '$')
		else:
			aIPRegExp = QtCore.QRegularExpression('^' + LmTools.IPv4_RS + '$')
		aIPValidator = QtGui.QRegularExpressionValidator(aIPRegExp)
		self._ipEdit.setValidator(aIPValidator)


	def nameTyped(self, iText):
		self.setOkButtonState()


	def protocolClick(self):
		self.setOkButtonState()


	def deviceSelected(self, iIndex):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			self._ipEdit.setText(self._deviceCombo.currentData())
			self._ignoreSignal = False


	def ipTyped(self, iText):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			i = self._deviceCombo.findData(iText)
			if i < 0:
				i = 0
			self._deviceCombo.setCurrentIndex(i)
			self._ignoreSignal = False

		self.setOkButtonState()


	def setOkButtonState(self):
		self._okButton.setDisabled((len(self.getName()) == 0) or
								   (len(self.getIP()) == 0) or
								   (len(self.getProtocols()) == 0))


	def loadDeviceList(self):
		t = self.getType()
		aDeviceMap = self.parent()._deviceIpNameMap
		self._deviceCombo.clear()

		# Load matching devices / IPs
		for i in aDeviceMap:
			if aDeviceMap[i]['IPVers'] == t:
				self._deviceCombo.addItem(self.parent().getDeviceNameFromIp(i), userData = i)

		# Sort by name
		self._deviceCombo.model().sort(0)

		# Insert unknown device at the beginning
		self._deviceCombo.insertItem(0, lfx('-Unknown-'), userData = '')
		self._deviceCombo.setCurrentIndex(0)
		self.deviceSelected(0)


	def accept(self):
		t = self.getType()

		# Validate IP address
		aIP = self.getIP()
		if t == RULE_TYPE_IPv6:
			if not LmTools.IsIPv6(aIP):
				self.parent().displayError('{} is not a valid IPv6 address.'.format(aIP))
				self._ipEdit.setFocus()
				return
		else:
			if not LmTools.IsIPv4(aIP):
				self.parent().displayError('{} is not a valid IPv4 address.'.format(aIP))
				self._ipEdit.setFocus()
				return

		# Validate external IP addresses
		e = self.getExtIPs()
		if len(e):
			aExtIPs = e.split(',')
			for aIP in aExtIPs:
				if len(aIP) == 0:
					self.parent().displayError('Empty IP address.')
					self._extIPsEdit.setFocus()
					return

				if t == RULE_TYPE_IPv6:
					if not LmTools.IsIPv6(aIP):
						self.parent().displayError('{} is not a valid IPv6 address.'.format(aIP))
						self._extIPsEdit.setFocus()
						return
				else:
					if not LmTools.IsIPv4(aIP):
						self.parent().displayError('{} is not a valid IPv4 address.'.format(aIP))
						self._extIPsEdit.setFocus()
						return

		super().accept()


	def getEnabled(self):
		return self._enableCheckBox.checkState() == QtCore.Qt.CheckState.Checked


	def getType(self):
		return self._typeCombo.currentText()


	def getName(self):
		return self._nameEdit.text()


	def getDescription(self):
		return self._descEdit.toPlainText()


	def getProtocols(self):
		p = ''

		if self._tcpCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			p += PROTOCOL_NAMES[str(Protocols.TCP.value)]

		if self._udpCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			if len(p):
				p += '/'
			p += PROTOCOL_NAMES[str(Protocols.UDP.value)]

		if self._ahCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			if len(p):
				p += '/'
			p += PROTOCOL_NAMES[str(Protocols.AH.value)]

		if self._greCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			if len(p):
				p += '/'
			p += PROTOCOL_NAMES[str(Protocols.GRE.value)]

		if self._espCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			if len(p):
				p += '/'
			p += PROTOCOL_NAMES[str(Protocols.ESP.value)]

		if self._icmpCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
			if len(p):
				p += '/'
			if self.getType() == RULE_TYPE_IPv6:
				aICMP = Protocols.ICMPv6.value
			else:
				aICMP = Protocols.ICMP.value
			p += PROTOCOL_NAMES[str(aICMP)]

		return p


	def getIP(self):
		return self._ipEdit.text()


	def getExtIPs(self):
		return self._extIPsEdit.toPlainText()



# ############# NAT/PAT rule type selection dialog #############
class NatPatRuleTypeDialog(QtWidgets.QDialog):
	def __init__(self, iUPnP, iParent = None):
		super(NatPatRuleTypeDialog, self).__init__(iParent)
		self.setMinimumWidth(230)
		self.resize(230, 150)

		self._upnp = iUPnP

		self._ipV4CheckBox = QtWidgets.QCheckBox(RULE_TYPE_IPv4, objectName = 'ipV4Checkbox')
		self._ipV4CheckBox.clicked.connect(self.setOkButtonState)
		self._ipV6CheckBox = QtWidgets.QCheckBox(RULE_TYPE_IPv6, objectName = 'ipV6Checkbox')
		self._ipV6CheckBox.clicked.connect(self.setOkButtonState)
		if iUPnP:
			self._upnpCheckBox = QtWidgets.QCheckBox(RULE_TYPE_UPnP, objectName = 'upnpCheckbox')
			self._upnpCheckBox.clicked.connect(self.setOkButtonState)

		aVCBox = QtWidgets.QVBoxLayout()
		aVCBox.setSpacing(10)
		aVCBox.addWidget(self._ipV4CheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aVCBox.addWidget(self._ipV6CheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		if iUPnP:
			aVCBox.addWidget(self._upnpCheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

		self._okButton = QtWidgets.QPushButton(ltx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(ltx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aVCBox, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'nprtype')

		self.setWindowTitle(ltx('Select rule types'))

		self.setDefault()

		self.setModal(True)
		self.show()


	# Set default values
	def setDefault(self):
		self._ipV4CheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		self._ipV6CheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		if self._upnp:
			self._upnpCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self.setOkButtonState()


	def getTypes(self):
		t = {}
		t[RULE_TYPE_IPv4] = self._ipV4CheckBox.checkState() == QtCore.Qt.CheckState.Checked
		t[RULE_TYPE_IPv6] = self._ipV6CheckBox.checkState() == QtCore.Qt.CheckState.Checked
		if self._upnp:
			t[RULE_TYPE_UPnP] = self._upnpCheckBox.checkState() == QtCore.Qt.CheckState.Checked
		return t


	def setOkButtonState(self):
		if self._upnp:
			aState = ((self._ipV4CheckBox.checkState() == QtCore.Qt.CheckState.Unchecked) and
					  (self._ipV6CheckBox.checkState() == QtCore.Qt.CheckState.Unchecked) and
					  (self._upnpCheckBox.checkState() == QtCore.Qt.CheckState.Unchecked))
		else:
			aState = ((self._ipV4CheckBox.checkState() == QtCore.Qt.CheckState.Unchecked) and
					  (self._ipV6CheckBox.checkState() == QtCore.Qt.CheckState.Unchecked))

		self._okButton.setDisabled(aState)
