### Livebox Monitor NAT/PAT tab module ###

import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig, LmPatPtf
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, NumericSortItem, CenteredIconsDelegate
from LiveboxMonitor.dlg.LmPatRule import PatRuleDialog
from LiveboxMonitor.dlg.LmPtfRule import PtfRuleDialog
from LiveboxMonitor.dlg.LmNatPatRuleType import NatPatRuleTypeDialog
from LiveboxMonitor.lang.LmLanguages import get_nat_pat_label as lx, get_nat_pat_message as mx

from LiveboxMonitor.__init__ import __build__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'natPatTab'

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
PTF_ICON_COLUMNS = [PtfCol.Enabled]



# ################################ LmNatPat class ################################
class LmNatPat:

	### Create NAT/PAT tab
	def createNatPatTab(self):
		self._natPatTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# PAT - port forwarding list
		self._patList = LmTableWidget(objectName = 'patList')
		self._patList.set_columns({PatCol.Key: ['Key', 0, None],
								   PatCol.Enabled: [lx('A'), 10, 'plist_Enabled'],
								   PatCol.Type: [lx('Type'), 55, 'plist_Type'],
								   PatCol.ID: [lx('Name'), 120, 'plist_ID'],
								   PatCol.Description: [lx('Port Forwarding Rule Description'), 400, 'plist_Description'],
								   PatCol.Protocols: [lx('Protocols'), 70, 'plist_Protocols'],
								   PatCol.IntPort: [lx('Internal Port'), 95, 'plist_IntPort'],
								   PatCol.ExtPort: [lx('External Port'), 95, 'plist_ExtPort'],
								   PatCol.Device: [lx('Device'), 180, 'plist_Device'],
								   PatCol.DestIP: ['DestIP', 0, None],
								   PatCol.ExtIPs: [lx('External IPs'), 250, 'plist_ExtIPs']})
		self._patList.set_header_resize([PatCol.Description])
		self._patList.set_standard_setup(self)
		self._patList.setItemDelegate(CenteredIconsDelegate(self, PAT_ICON_COLUMNS))
		self._patList.itemSelectionChanged.connect(self.patListClick)
		self._patList.doubleClicked.connect(self.editPatRuleButtonClick)

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
		self._ptfList = LmTableWidget(objectName = 'ptfList')
		self._ptfList.set_columns({PtfCol.Key: ['Key', 0, None],
								   PtfCol.Enabled: [lx('A'), 10, 'tlist_Enabled'],
								   PtfCol.Type: [lx('Type'), 55, 'tlist_Type'],
								   PtfCol.ID: [lx('Name'), 120, 'tlist_ID'],
								   PtfCol.Description: [lx('Protocol Forwarding Rule Description'), 360, 'tlist_Description'],
								   PtfCol.Protocols: [lx('Protocols'), 180, 'tlist_Protocols'],
								   PtfCol.Device: [lx('Device'), 220, 'tlist_Device'],
								   PtfCol.DestIP: ['DestIP', 0, None],
								   PtfCol.ExtIPs: [lx('External IPs'), 250, 'tlist_ExtIPs']})
		self._ptfList.set_header_resize([PtfCol.Description])
		self._ptfList.set_standard_setup(self)
		self._ptfList.setItemDelegate(CenteredIconsDelegate(self, PTF_ICON_COLUMNS))
		self._ptfList.itemSelectionChanged.connect(self.ptfListClick)
		self._ptfList.doubleClicked.connect(self.editPtfRuleButtonClick)
		aListSize = LmConfig.table_height(5)
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

		LmConfig.set_tooltips(self._natPatTab, 'natpat')
		self._tab_widget.addTab(self._natPatTab, lx('NAT/PAT'))

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
			self.load_device_ip_name_map()
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
			self._task.start(lx('Saving rule...'))
			if self.savePatRule(r):
				self.commitNatPatRuleChange()
				i = self._patList.currentRow()
				self._patList.setItem(i, PatCol.Enabled, self.format_active_table_widget(r['Enable']))
				self.patListClick()
			self._task.end()


	### Click on add PAT rule button
	def addPatRuleButtonClick(self):
		dialog = PatRuleDialog(None, self)
		if dialog.exec():
			self._task.start(lx('Saving rule...'))
			r = dialog.get_rule()
			if self.savePatRule(r):
				self.commitNatPatRuleChange()
				self.refreshPatList()
			self._task.end()


	### Click on edit PAT rule button
	def editPatRuleButtonClick(self):
		r = self.getSelectedPatRule()
		if r is not None:
			dialog = PatRuleDialog(r, self)
			if dialog.exec():
				self._task.start(lx('Saving rule...'))
				# First delete current rule
				self.delPatRule(r)
				# Then save new one
				r = dialog.get_rule()
				if self.savePatRule(r):
					self.commitNatPatRuleChange()
					self.refreshPatList()
				self._task.end()


	### Click on delete PAT rule rules button
	def delPatRuleButtonClick(self):
		r = self.getSelectedPatRule()
		if r is not None:
			self._task.start(lx('Deleting rule...'))
			if self.delPatRule(r):
				self.commitNatPatRuleChange()
				self.refreshPatList()
			self._task.end()


	### Click on delete all PAT rules button
	def delAllPatRulesButtonClick(self):
		dialog = NatPatRuleTypeDialog(True, self)
		if dialog.exec():
			self._task.start(lx('Deleting rules...'))
			t = dialog.get_types()

			# Delete all IPv4 rules if selected
			if t[LmPatPtf.RULE_TYPE_IPv4]:
				self.delAllIPv4PatRule(False)

			# Delete all UPnP rules if selected
			if t[LmPatPtf.RULE_TYPE_UPnP]:
				self.delAllIPv4PatRule(True)

			# Delete one by one IPv6 rules if selected
			if t[LmPatPtf.RULE_TYPE_IPv6]:
				i = 0
				n = self._patList.rowCount()
				while (i < n):
					r = self.getPatRuleFromList(i)
					if (r is not None) and (r['Type'] == LmPatPtf.RULE_TYPE_IPv6):
						self.delPatRule(r)
					i += 1

			# Commit & refresh
			self.commitNatPatRuleChange()
			self.refreshPatList()
			self._task.end()

			self.display_status(mx('All selected rule(s) deleted.', 'delAllPat'))


	### Click on export PAT rules button
	def exportPatRulesButtonClick(self):
		dialog = NatPatRuleTypeDialog(True, self)
		if dialog.exec():
			t = dialog.get_types()

			aFileName = QtWidgets.QFileDialog.getSaveFileName(self, lx('Export File'), lx('Port Forwarding Rules') + '.txt', '*.txt')[0]
			if not aFileName:
				return

			try:
				aExportFile = open(aFileName, 'w')
			except Exception as e:
				LmTools.error(str(e))
				self.display_error(mx('Cannot create the file.', 'createFileErr'))
				return

			self._task.start(lx('Exporting port forwarding rules...'))

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

			self._task.end()

			try:
				aExportFile.close()
			except Exception as e:
				LmTools.error(str(e))
				self.display_error(mx('Cannot save the file.', 'saveFileErr'))

			self.display_status(mx('{} rule(s) exported.', 'ruleExport').format(c))


	### Click on import PAT rules button
	def importPatRulesButtonClick(self):
		aFileName = QtWidgets.QFileDialog.getOpenFileName(self, lx('Select file to import'), '', '*.txt')
		aFileName = aFileName[0]
		if aFileName == '':
			return

		try:
			aImportFile = open(aFileName, 'r')
		except Exception as e:
			LmTools.error(str(e))
			self.display_error(mx('Cannot open the file.', 'openFileErr'))
			return

		aError = False
		try:
			aFile = json.load(aImportFile)
		except Exception as e:
			LmTools.error(f'Error loading file: {e}')
			self.display_error(mx('Wrong file format.', 'fileFormatErr'))
			aError = True

		if not aError:
			aRules = aFile.get('Rules', None)

			if (aFile.get('Type', '') != 'PAT') or (aRules is None):
				self.display_error(mx('Wrong file type.', 'fileTypeErr'))
				aError = True

		if not aError:
			self._task.start(lx('Importing port forwarding rules...'))

			c = 0
			for r in aRules:
				if self.checkPatRule(r) and self.savePatRule(r):
					c += 1

			self._task.end()

		try:
			aImportFile.close()
		except Exception as e:
			LmTools.error(str(e))
			self.display_error(mx('Cannot close the file.', 'closeFileErr'))

		if not aError:
			self.commitNatPatRuleChange()
			self.refreshPatList()

			self.display_status(mx('{} rule(s) imported.', 'ruleImport').format(c))


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
			self._task.start(lx('Saving rule...'))
			if self.savePtfRule(r):
				self.commitNatPatRuleChange()
				i = self._ptfList.currentRow()
				self._ptfList.setItem(i, PtfCol.Enabled, self.format_active_table_widget(r['Enable']))
				self.ptfListClick()
			self._task.end()


	### Click on add PTF rule button
	def addPtfRuleButtonClick(self):
		dialog = PtfRuleDialog(None, self)
		if dialog.exec():
			self._task.start(lx('Saving rule...'))
			r = dialog.get_rule()
			if self.savePtfRule(r):
				self.commitNatPatRuleChange()
				self.refreshPtfList()
			self._task.end()


	### Click on edit PTF rule button
	def editPtfRuleButtonClick(self):
		r = self.getSelectedPtfRule()
		if r is not None:
			dialog = PtfRuleDialog(r, self)
			if dialog.exec():
				self._task.start(lx('Saving rule...'))
				# First delete current rule
				self.delPtfRule(r)
				# Then save new one
				r = dialog.get_rule()
				if self.savePtfRule(r):
					self.commitNatPatRuleChange()
					self.refreshPtfList()
				self._task.end()


	### Click on delete PTF rule rules button
	def delPtfRuleButtonClick(self):
		r = self.getSelectedPtfRule()
		if r is not None:
			self._task.start(lx('Deleting rule...'))
			if self.delPtfRule(r):
				self.commitNatPatRuleChange()
				self.refreshPtfList()
			self._task.end()


	### Click on delete all PTF rules button
	def delAllPtfRulesButtonClick(self):
		dialog = NatPatRuleTypeDialog(False, self)
		if dialog.exec():
			self._task.start(lx('Deleting rules...'))
			t = dialog.get_types()
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
			self._task.end()

			self.display_status(mx('{} rule(s) deleted.', 'ruleDel').format(c))


	### Click on export PTF rules button
	def exportPtfRulesButtonClick(self):
		dialog = NatPatRuleTypeDialog(False, self)
		if dialog.exec():
			t = dialog.get_types()

			aFileName = QtWidgets.QFileDialog.getSaveFileName(self, lx('Export File'), lx('Protocol Forwarding Rules') + '.txt', '*.txt')[0]
			if not aFileName:
				return

			try:
				aExportFile = open(aFileName, 'w')
			except Exception as e:
				LmTools.error(str(e))
				self.display_error(mx('Cannot create the file.', 'createFileErr'))
				return

			self._task.start(lx('Exporting protocol forwarding rules...'))

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

			self._task.end()

			try:
				aExportFile.close()
			except Exception as e:
				LmTools.error(str(e))
				self.display_error(mx('Cannot save the file.', 'saveFileErr'))

			self.display_status(mx('{} rule(s) exported.', 'ruleExport').format(c))


	### Click on import PTF rules button
	def importPtfRulesButtonClick(self):
		aFileName = QtWidgets.QFileDialog.getOpenFileName(self, lx('Select file to import'), '', '*.txt')
		aFileName = aFileName[0]
		if aFileName == '':
			return

		try:
			aImportFile = open(aFileName, 'r')
		except Exception as e:
			LmTools.error(str(e))
			self.display_error(mx('Cannot open the file.', 'openFileErr'))
			return

		aError = False
		try:
			aFile = json.load(aImportFile)
		except Exception as e:
			LmTools.error(f'Error loading file: {e}')
			self.display_error(mx('Wrong file format.', 'fileFormatErr'))
			aError = True

		if not aError:
			aRules = aFile.get('Rules', None)

			if (aFile.get('Type', '') != 'PTF') or (aRules is None):
				self.display_error(mx('Wrong file type.', 'fileTypeErr'))
				aError = True

		if not aError:
			self._task.start(lx('Importing protocol forwarding rules...'))

			c = 0
			for r in aRules:
				if self.checkPtfRule(r) and self.savePtfRule(r):
					c += 1

			self._task.end()

		try:
			aImportFile.close()
		except Exception as e:
			LmTools.error(str(e))
			self.display_error(mx('Cannot close the file.', 'closeFileErr'))

		if not aError:
			self.commitNatPatRuleChange()
			self.refreshPtfList()

			self.display_status(mx('{} rule(s) imported.', 'ruleImport').format(c))


	### Load protocol name to number reverse map from number to name
	def loadProtocolNumbers(self):
		# Init
		self._protocolNumber = {}

		# Build reverse map
		for k in LmPatPtf.PROTOCOL_NAMES:
			self._protocolNumbers[LmPatPtf.PROTOCOL_NAMES[k]] = k


	### Refresh PAT list
	def refreshPatList(self):
		self._patList.clearContents()
		self._patList.setRowCount(0)
		self.load_device_ip_name_map()
		self.loadPatRules()


	### Load PAT rules
	def loadPatRules(self):
		self._task.start(lx('Loading port forwarding rules...'))
		self._patList.setSortingEnabled(False)

		# IPv4 types (webui / upnp / others?)
		self.loadIPv4PatRules()

		# IPv6 types
		self.loadIPv6PatRules()

		self._patList.sortItems(PatCol.Type, QtCore.Qt.SortOrder.AscendingOrder)
		self._patList.setSortingEnabled(True)

		self._patList.setCurrentCell(-1, -1)
		self.patListClick()

		self._task.end()


	### Load IPv4 (webui / upnp / others?) PAT rules
	def loadIPv4PatRules(self):
		try:
			d = self._session.request('Firewall', 'getPortForwarding')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			self.display_error(mx('Cannot load IPv4 port forwarding rules.', 'patLoadErr'))
			return

		i = self._patList.rowCount()
		for k in d:
			self._patList.insertRow(i)
			r = d[k]

			aActiveStatus = r.get('Enable', False)
			self._patList.setItem(i, PatCol.Enabled, self.format_active_table_widget(aActiveStatus))

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
			self._patList.setItem(i, PatCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(aDestinationIP)))

			aExternalIPs = r.get('SourcePrefix', '')
			if len(aExternalIPs) == 0:
				aExternalIPs = lx('All')
			self._patList.setItem(i, PatCol.ExtIPs, QtWidgets.QTableWidgetItem(aExternalIPs))

			i += 1


	### Load IPv6 PAT rules
	def loadIPv6PatRules(self):
		try:
			d = self._session.request('Firewall', 'getPinhole')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.error('Cannot load IPv6 port forwarding rules.')	# Do not display a dialog as not all LB models have this API
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
			self._patList.setItem(i, PatCol.Enabled, self.format_active_table_widget(aActiveStatus))

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
			self._patList.setItem(i, PatCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(aDestinationIP)))

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
			LmTools.error('Rule as no Enable tag.')
			return False

		t = iRule.get('Type', 'UNK')
		if t not in LmPatPtf.RULE_PAT_TYPES:
			LmTools.error(f'Rule has unknown {t} type.')
			return False

		if len(iRule.get('Name', '')) == 0:
			LmTools.error('Rule has no Name.')
			return False

		aProtocols = iRule.get('ProtoNumbers', '')
		if len(aProtocols) == 0:
			LmTools.error('Rule has no protocol.')
			return False

		for p in aProtocols.split(','):
			n = LmPatPtf.PROTOCOL_NAMES.get(p)
			if n is None:
				LmTools.error(f'Rule has wrong protocol {p} set.')
				return False
			n = int(p)
			if (n != LmPatPtf.Protocols.TCP) and (n != LmPatPtf.Protocols.UDP):
				LmTools.error(f'Rule has wrong protocol {p} set.')
				return False

		n = iRule.get('IntPort', '')
		if (n is not None) and len(n):
			if not LmTools.is_tcp_udp_port(n):
				LmTools.error(f'Rule has wrong internal port {n} set.')
				return False

		n = iRule.get('ExtPort', '')
		if (n is not None) and len(n):
			if not LmTools.is_tcp_udp_port(n):
				LmTools.error(f'Rule has wrong external port {n} set.')
				return False

		aIP = iRule.get('IP', '')
		if len(aIP) == 0:
			return False
		if t == LmPatPtf.RULE_TYPE_IPv6:
			if not LmTools.is_ipv6(aIP):
				LmTools.error(f'Rule has wrong IPv6 {aIP} set.')
				return False
		else:
			if not LmTools.is_ipv4(aIP):
				LmTools.error(f'Rule has wrong IPv4 {aIP} set.')
				return False

		e = iRule.get('ExtIPs', '')
		if len(e):
			aExtIPs = e.split(',')
			for aIP in aExtIPs:
				if len(aIP) == 0:
					LmTools.error('Rule external IPs has an empty IP address.')
					return False

				if t == LmPatPtf.RULE_TYPE_IPv6:
					if not LmTools.is_ipv6(aIP):
						LmTools.error(f'Rule external IPs has a wrong IPv6 {aIP} set.')
						return False
				else:
					if not LmTools.is_ipv4(aIP):
						LmTools.error(f'Rule external IPs has a wrong IPv4 {aIP} set.')
						return False

		return True


	### Save a PAT rule in Livebox, return True if successful
	def savePatRule(self, iRule, iSilent = False):
		if iRule['Type'] == LmPatPtf.RULE_TYPE_IPv6:
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
		if iRule['Type'] == LmPatPtf.RULE_TYPE_IPv4:
			r['origin'] = 'webui'
		else:
			r['origin'] = 'upnp'
		r['destinationMACAddress'] = ''
		aExternalIPs = iRule['ExtIPs']
		if len(aExternalIPs):
			r['sourcePrefix'] = aExternalIPs

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall', 'setPortForwarding', r)
		except Exception as e:
			LmTools.error(str(e))
			if not iSilent:
				self.display_error('Firewall:setPortForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				if not iSilent:
					self.display_error(aErrors)
				return False
			return True
		else:
			if not iSilent:
				self.display_error('Firewall:setPortForwarding query failed.')
			return False


	### Save a IPv6 PAT rule in Livebox, return True if successful
	def saveIPv6PatRule(self, iRule, iSilent = False):
		# Map rule to Livebox model
		r = {}
		r['id'] = iRule['Name']
		r['origin'] = 'webui'
		r['sourceInterface'] = 'data'
		p = iRule['ExtPort']
		if LmPatPtf.IPV6_SOURCE_PORT_WORKING and (p is not None):
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
			aReply = self._session.request('Firewall', 'setPinhole', r)
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Firewall:setPinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				self.display_error(aErrors)
				return False
			return True
		else:
			self.display_error('Firewall:setPinhole query failed.')
			return False


	### Delete a PAT rule from Livebox, return True if successful
	def delPatRule(self, iRule):
		if iRule['Type'] == LmPatPtf.RULE_TYPE_IPv6:
			return self.delIPv6PatRule(iRule)
		return self.delIPv4PatRule(iRule)


	### Delete a IPv4 PAT rule from Livebox, return True if successful
	def delIPv4PatRule(self, iRule):
		# Build parameters
		r = {}
		if iRule['Type'] == LmPatPtf.RULE_TYPE_IPv4:
			o = 'webui'
		else:
			o = 'upnp'
		r['id'] = o + '_' + iRule['Name']
		r['destinationIPAddress'] = iRule['IP']
		r['origin'] = o

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall', 'deletePortForwarding', r)
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Firewall:deletePortForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				self.display_error(aErrors)
				return False
			return aReply['status']
		else:
			self.display_error('Firewall:deletePortForwarding query failed.')
			return False


	### Delete a IPv6 PAT rule from Livebox, return True if successful
	def delIPv6PatRule(self, iRule):
		# Build parameters
		r = {}
		r['id'] = 'webui_' + iRule['Name']
		r['origin'] = 'webui'

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall', 'deletePinhole', r)
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Firewall:deletePinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				self.display_error(aErrors)
				return False
			return aReply['status']
		else:
			self.display_error('Firewall:deletePinhole query failed.')
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
			aReply = self._session.request('Firewall', 'deletePortForwarding', { 'origin': o })
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Firewall:deletePortForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				self.display_error(aErrors)
				return False
			return aReply['status']
		else:
			self.display_error('Firewall:deletePortForwarding query failed.')
			return False


	### Refresh PTF list
	def refreshPtfList(self):
		self._ptfList.clearContents()
		self._ptfList.setRowCount(0)
		self.load_device_ip_name_map()
		self.loadPtfRules()


	### Load PTF rules
	def loadPtfRules(self):
		self._task.start(lx('Loading protocol forwarding rules...'))
		self._ptfList.setSortingEnabled(False)

		# IPv4 types
		self.loadIPv4PtfRules()

		# IPv6 types
		self.loadIPv6PtfRules()

		self._ptfList.sortItems(PtfCol.Type, QtCore.Qt.SortOrder.AscendingOrder)
		self._ptfList.setSortingEnabled(True)

		self._ptfList.setCurrentCell(-1, -1)
		self.ptfListClick()

		self._task.end()


	### Load IPv4 PTF rules
	def loadIPv4PtfRules(self):
		try:
			d = self._session.request('Firewall', 'getProtocolForwarding')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			self.display_error(mx('Cannot load IPv4 protocol forwarding rules.', 'ptfLoadErr'))
			return

		i = self._ptfList.rowCount()
		for k in d:
			self._ptfList.insertRow(i)
			r = d[k]

			aActiveStatus = r.get('Status', 'Disabled') == 'Enabled'
			self._ptfList.setItem(i, PtfCol.Enabled, self.format_active_table_widget(aActiveStatus))

			aOrigin = r.get('SourceInterface', '')
			if aOrigin == 'data':
				aType = LmPatPtf.RULE_TYPE_IPv4
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
			self._ptfList.setItem(i, PtfCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(aDestinationIP)))

			aExternalIPs = r.get('SourcePrefix', '')
			if len(aExternalIPs) == 0:
				aExternalIPs = lx('All')
			self._ptfList.setItem(i, PtfCol.ExtIPs, QtWidgets.QTableWidgetItem(aExternalIPs))

			i += 1


	### Load IPv6 PTF rules
	def loadIPv6PtfRules(self):
		try:
			d = self._session.request('Firewall', 'getPinhole')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.error('Cannot load IPv6 protocol forwarding rules.')	# Do not display a dialog as not all LB models have this API
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
			self._ptfList.setItem(i, PtfCol.Enabled, self.format_active_table_widget(aActiveStatus))

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
			self._ptfList.setItem(i, PtfCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(aDestinationIP)))

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
			LmTools.error('Rule as no Enable tag.')
			return False

		t = iRule.get('Type', 'UNK')
		if t not in LmPatPtf.RULE_PTF_TYPES:
			LmTools.error(f'Rule has unknown {t} type.')
			return False

		if len(iRule.get('Name', '')) == 0:
			LmTools.error('Rule has no Name.')
			return False

		aProtocols = iRule.get('ProtoNumbers', '')
		if len(aProtocols) == 0:
			LmTools.error('Rule has no protocol.')
			return False

		for p in aProtocols.split(','):
			n = LmPatPtf.PROTOCOL_NAMES.get(p)
			if n is None:
				LmTools.error(f'Rule has wrong protocol {p} set.')
				return False
			n = int(p)
			if t == LmPatPtf.RULE_TYPE_IPv6:
				aICMP = LmPatPtf.Protocols.ICMPv6
			else:
				aICMP = LmPatPtf.Protocols.ICMP
			if ((n != LmPatPtf.Protocols.TCP) and
				(n != LmPatPtf.Protocols.UDP) and
				(n != LmPatPtf.Protocols.AH) and
				(n != LmPatPtf.Protocols.GRE) and
				(n != LmPatPtf.Protocols.ESP) and
				(n != aICMP)):
				LmTools.error(f'Rule has wrong protocol {p} set.')
				return False

		aIP = iRule.get('IP', '')
		if len(aIP) == 0:
			return False
		if t == LmPatPtf.RULE_TYPE_IPv6:
			if not LmTools.is_ipv6_pfix(aIP):
				LmTools.error(f'Rule has wrong IPv6 {aIP} set.')
				return False
		else:
			if not LmTools.is_ipv4(aIP):
				LmTools.error(f'Rule has wrong IPv4 {aIP} set.')
				return False

		e = iRule.get('ExtIPs', '')
		if len(e):
			aExtIPs = e.split(',')
			for aIP in aExtIPs:
				if len(aIP) == 0:
					LmTools.error('Rule external IPs has an empty IP address.')
					return False

				if t == LmPatPtf.RULE_TYPE_IPv6:
					if not LmTools.is_ipv6(aIP):
						LmTools.error(f'Rule external IPs has a wrong IPv6 {aIP} set.')
						return False
				else:
					if not LmTools.is_ipv4(aIP):
						LmTools.error(f'Rule external IPs has a wrong IPv4 {aIP} set.')
						return False

		return True


	### Save a PTF rule in Livebox, return True if successful
	def savePtfRule(self, iRule, iSilent = False):
		if iRule['Type'] == LmPatPtf.RULE_TYPE_IPv6:
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
			aReply = self._session.request('Firewall', 'setProtocolForwarding', r)
		except Exception as e:
			LmTools.error(str(e))
			if not iSilent:
				self.display_error('Firewall:setProtocolForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				if not iSilent:
					self.display_error(aErrors)
				return False
			return True
		else:
			if not iSilent:
				self.display_error('Firewall:setProtocolForwarding query failed.')
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
			aReply = self._session.request('Firewall', 'setPinhole', r)
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Firewall:setPinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				self.display_error(aErrors)
				return False
			return True
		else:
			self.display_error('Firewall:setPinhole query failed.')
			return False


	### Delete a PTF rule from Livebox, return True if successful
	def delPtfRule(self, iRule):
		if iRule['Type'] == LmPatPtf.RULE_TYPE_IPv6:
			return self.delIPv6PtfRule(iRule)
		return self.delIPv4PtfRule(iRule)


	### Delete a IPv4 PTF rule from Livebox, return True if successful
	def delIPv4PtfRule(self, iRule):
		# Call Livebox API
		try:
			aReply = self._session.request('Firewall', 'deleteProtocolForwarding', { 'id': iRule['Name'] })
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Firewall:deleteProtocolForwarding query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				self.display_error(aErrors)
				return False
			return aReply['status']
		else:
			self.display_error('Firewall:deleteProtocolForwarding query failed.')
			return False


	### Delete a IPv6 PTF rule from Livebox, return True if successful
	def delIPv6PtfRule(self, iRule):
		# Build parameters
		r = {}
		r['id'] = 'webui_' + iRule['Name']
		r['origin'] = 'webui'

		# Call Livebox API
		try:
			aReply = self._session.request('Firewall', 'deletePinhole', r)
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Firewall:deletePinhole query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.get_errors_from_livebox_reply(aReply)
			if len(aErrors):
				self.display_error(aErrors)
				return False
			return aReply['status']
		else:
			self.display_error('Firewall:deletePinhole query failed.')
			return False


	### Commit Firewall rule changes, return True if successful
	def commitNatPatRuleChange(self):
		try:
			aReply = self._session.request('Firewall', 'commit')
		except Exception as e:
			LmTools.error(str(e))
			LmTools.error('Firewall commit query error.')
			return False

		if aReply is not None:
			return aReply.get('status', False)
		else:
			LmTools.error('Firewall commit query failed.')
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
		###WARNING### : names must match those set by NatPatRuleTypeDialog.get_types() method
		if iOrigin == 'webui':
			if iIPv6:
				return QtWidgets.QTableWidgetItem(LmPatPtf.RULE_TYPE_IPv6)
			else:
				return QtWidgets.QTableWidgetItem(LmPatPtf.RULE_TYPE_IPv4)
		elif iOrigin == 'upnp':
			return QtWidgets.QTableWidgetItem(LmPatPtf.RULE_TYPE_UPnP)
		else:
			return QtWidgets.QTableWidgetItem(iOrigin)


	### Format Protocols cell
	@staticmethod
	def formatNatPatProtocolsTableWidget(iProtocols):
		r = ''
		for p in iProtocols.split(','):
			if len(r):
				r += '/'
			r += LmPatPtf.PROTOCOL_NAMES.get(p, 'UNK')
		return QtWidgets.QTableWidgetItem(r)


	### Format Port cell
	@staticmethod
	def formatPortTableWidget(iPort):
		aPort = NumericSortItem(iPort)
		p = iPort.split('-')[0]		# If range is used, sort with the first port
		try:
			i = int(p)
		except Exception:
			i = 0
		aPort.setData(QtCore.Qt.ItemDataRole.UserRole, i)
		return aPort
