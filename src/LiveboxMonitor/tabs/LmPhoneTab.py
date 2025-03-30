### Livebox Monitor phone tab module ###

import os
import webbrowser
import requests
import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang.LmLanguages import (GetPhoneLabel as lx,
											 GetPhoneMessage as mx,
											 GetPhoneContactDialogLabel as lcx)


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'phoneTab'

# List columns
class CallCol(IntEnum):
	Key = 0
	Type = 1
	Time = 2
	Number = 3
	ContactSource = 4	# N=None, L=Livebox, P=Program dynamic guess, S=Spam
	Contact = 5
	Duration = 6
	Count = 7
ICON_COLUMNS = [CallCol.Type]

class ContactCol(IntEnum):
	Key = 0
	Name = 1
	Cell = 2
	Home = 3
	Work = 4
	Ring = 5
	Count = 6

# Check spam URLs
CHECK_SPAM_URL1 = 'https://www.numeroinconnu.fr/numero/{}'
CHECK_SPAM_URL2 = 'https://callfilter.app/{}'

# CallFilter URL
CALLFILTER_URL = 'https://api.callfilter.app/apis/{0}/1/{1}'

# Spam indicator in call list
SPAM_CONTACT_NAME = '# SPAM #'



# ################################ LmPhone class ################################
class LmPhone:

	### Create phone tab
	def createPhoneTab(self):
		self._phoneTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# Call list
		self._callList = QtWidgets.QTableWidget(objectName = 'callList')
		self._callList.setColumnCount(CallCol.Count)
		self._callList.setHorizontalHeaderLabels(('Key', lx('T'), lx('Time'), lx('Number'), 'CS', lx('Contact'), lx('Duration')))
		self._callList.setColumnHidden(CallCol.Key, True)
		self._callList.setColumnHidden(CallCol.ContactSource, True)
		aHeader = self._callList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(CallCol.Contact, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(CallCol.Type, QtCore.Qt.Orientation.Horizontal, 'calist_Type', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(CallCol.Time, QtCore.Qt.Orientation.Horizontal, 'calist_Time', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(CallCol.Number, QtCore.Qt.Orientation.Horizontal, 'calist_Number', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(CallCol.Contact, QtCore.Qt.Orientation.Horizontal, 'calist_Contact', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(CallCol.Duration, QtCore.Qt.Orientation.Horizontal, 'calist_Duration', QtCore.Qt.ItemDataRole.UserRole)
		self._callList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._callList.setColumnWidth(CallCol.Type, 30)
		self._callList.setColumnWidth(CallCol.Time, 130)
		self._callList.setColumnWidth(CallCol.Number, 110)
		self._callList.setColumnWidth(CallCol.Contact, 250)
		self._callList.setColumnWidth(CallCol.Duration, 80)
		self._callList.verticalHeader().hide()
		self._callList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._callList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._callList.setSortingEnabled(True)
		self._callList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._callList.itemSelectionChanged.connect(self.callListClick)
		self._callList.doubleClicked.connect(self.editContactFromCallListClick)
		self._callList.setMinimumWidth(480)
		self._callList.setMaximumWidth(540)
		self._callList.setItemDelegate(LmTools.CenteredIconsDelegate(self, ICON_COLUMNS))
		LmConfig.SetTableStyle(self._callList)

		# Call button bar
		aCallButtonsBox = QtWidgets.QHBoxLayout()
		aCallButtonsBox.setSpacing(30)
		aRefreshCallButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refreshCall')
		aRefreshCallButton.clicked.connect(self.refreshCallButtonClick)
		aCallButtonsBox.addWidget(aRefreshCallButton)
		self._deleteCallButton = QtWidgets.QPushButton(lx('Delete'), objectName = 'deleteCall')
		self._deleteCallButton.clicked.connect(self.deleteCallButtonClick)
		aCallButtonsBox.addWidget(self._deleteCallButton)
		aDeleteAllCallsButton = QtWidgets.QPushButton(lx('Delete All...'), objectName = 'deleteAllCalls')
		aDeleteAllCallsButton.clicked.connect(self.deleteAllCallsButtonClick)
		aCallButtonsBox.addWidget(aDeleteAllCallsButton)

		# Spam tools button bar
		aSpamButtonsBox = QtWidgets.QHBoxLayout()
		aSpamButtonsBox.setSpacing(30)
		aSpamCallScanButton = QtWidgets.QPushButton(lx('Spams scan'), objectName = 'spamCallScan')
		aSpamCallScanButton.clicked.connect(self.spamCallScanButtonClick)
		aSpamButtonsBox.addWidget(aSpamCallScanButton)
		self._spamCallSitesButton = QtWidgets.QPushButton(lx('Spam sites'), objectName = 'spamCallSites')
		self._spamCallSitesButton.clicked.connect(self.spamCallSitesButtonClick)
		aSpamButtonsBox.addWidget(self._spamCallSitesButton)
		self._setSpamCallButton = QtWidgets.QPushButton(lx('Set as spam'), objectName = 'setSpamCall')
		self._setSpamCallButton.clicked.connect(self.setSpamCallButtonClick)
		aSpamButtonsBox.addWidget(self._setSpamCallButton)

		# Call layout
		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aCallBox = QtWidgets.QVBoxLayout()
		aCallBox.setSpacing(13)
		aCallBox.addWidget(self._callList, 1)
		aCallBox.addLayout(aCallButtonsBox, 0)
		aCallBox.insertSpacing(-1, 2)
		aCallBox.addWidget(aSeparator)
		aCallBox.insertSpacing(-1, 2)
		aCallBox.addLayout(aSpamButtonsBox, 0)

		# Contact list
		self._contactList = QtWidgets.QTableWidget(objectName = 'contactList')
		self._contactList.setColumnCount(ContactCol.Count)
		self._contactList.setHorizontalHeaderLabels(('Key', lx('Name'), lx('Mobile'), lx('Home'), lx('Work'), lx('Ring')))
		self._contactList.setColumnHidden(ContactCol.Key, True)
		aHeader = self._contactList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(ContactCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(ContactCol.Name, QtCore.Qt.Orientation.Horizontal, 'colist_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(ContactCol.Cell, QtCore.Qt.Orientation.Horizontal, 'colist_Cell', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(ContactCol.Home, QtCore.Qt.Orientation.Horizontal, 'colist_Home', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(ContactCol.Work, QtCore.Qt.Orientation.Horizontal, 'colist_Work', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(ContactCol.Ring, QtCore.Qt.Orientation.Horizontal, 'colist_Ring', QtCore.Qt.ItemDataRole.UserRole)
		self._contactList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._contactList.setColumnWidth(ContactCol.Name, 250)
		self._contactList.setColumnWidth(ContactCol.Cell, 110)
		self._contactList.setColumnWidth(ContactCol.Home, 110)
		self._contactList.setColumnWidth(ContactCol.Work, 110)
		self._contactList.setColumnWidth(ContactCol.Ring, 60)
		self._contactList.verticalHeader().hide()
		self._contactList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._contactList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._contactList.setSortingEnabled(True)
		self._contactList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._contactList.itemSelectionChanged.connect(self.contactListClick)
		self._contactList.doubleClicked.connect(self.editContactButtonClick)
		LmConfig.SetTableStyle(self._contactList)

		# Contact button bar
		aContactButtonsBox = QtWidgets.QHBoxLayout()
		aContactButtonsBox.setSpacing(10)
		aRefreshContactButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refreshContact')
		aRefreshContactButton.clicked.connect(self.refreshContactButtonClick)
		aContactButtonsBox.addWidget(aRefreshContactButton)
		aAddContactButton = QtWidgets.QPushButton(lx('Add...'), objectName = 'addContact')
		aAddContactButton.clicked.connect(self.addContactButtonClick)
		aContactButtonsBox.addWidget(aAddContactButton)
		self._editContactButton = QtWidgets.QPushButton(lx('Edit...'), objectName = 'editContact')
		self._editContactButton.clicked.connect(self.editContactButtonClick)
		aContactButtonsBox.addWidget(self._editContactButton)
		self._deleteContactButton = QtWidgets.QPushButton(lx('Delete'), objectName = 'deleteContact')
		self._deleteContactButton.clicked.connect(self.deleteContactButtonClick)
		aContactButtonsBox.addWidget(self._deleteContactButton)
		aDeleteAllContactsButton = QtWidgets.QPushButton(lx('Delete All...'), objectName = 'deleteAllContacts')
		aDeleteAllContactsButton.clicked.connect(self.deleteAllContactsButtonClick)
		aContactButtonsBox.addWidget(aDeleteAllContactsButton)

		# Tool button bar
		aToolButtonsBox = QtWidgets.QHBoxLayout()
		aToolButtonsBox.setSpacing(30)

		aPhoneRingSet = QtWidgets.QHBoxLayout()
		aPhoneRingSet.setSpacing(2)
		self._ringToneCombo = QtWidgets.QComboBox(objectName = 'ringToneCombo')
		self._ringToneCombo.addItem('-')
		i = 1
		while i <= 7:
			self._ringToneCombo.addItem(str(i))
			i += 1
		self._ringToneCombo.setMaximumWidth(55)
		aPhoneRingSet.addWidget(self._ringToneCombo)
		aPhoneRingButton = QtWidgets.QPushButton(lx('Phone Ring'), objectName = 'phoneRing')
		aPhoneRingButton.clicked.connect(self.phoneRingButtonClick)
		aPhoneRingSet.addWidget(aPhoneRingButton)
		aToolButtonsBox.addLayout(aPhoneRingSet, 0)

		aExportContactsButton = QtWidgets.QPushButton(lx('Export...'), objectName = 'exportContacts')
		aExportContactsButton.clicked.connect(self.exportContactsButtonClick)
		aToolButtonsBox.addWidget(aExportContactsButton)
		aImportContactsButton = QtWidgets.QPushButton(lx('Import...'), objectName = 'importContacts')
		aImportContactsButton.clicked.connect(self.importContactsButtonClick)
		aToolButtonsBox.addWidget(aImportContactsButton)

		# Contact layout
		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aContactBox = QtWidgets.QVBoxLayout()
		aContactBox.setSpacing(13)
		aContactBox.addWidget(self._contactList, 1)
		aContactBox.addLayout(aContactButtonsBox, 0)
		aContactBox.insertSpacing(-1, 2)
		aContactBox.addWidget(aSeparator)
		aContactBox.insertSpacing(-1, 2)
		aContactBox.addLayout(aToolButtonsBox, 0)

		# Layout
		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setSpacing(10)
		aHBox.addLayout(aCallBox, 1)
		aHBox.addWidget(aSeparator)
		aHBox.addLayout(aContactBox, 1)
		self._phoneTab.setLayout(aHBox)

		LmConfig.SetToolTips(self._phoneTab, 'phone')
		self._tabWidget.addTab(self._phoneTab, lx('Phone'))

		# Init context
		self.phoneTabInit()


	### Init phone tab context
	def phoneTabInit(self):
		self._phoneDataLoaded = False
		self._contactMatching = {}


	### Reset phone tab
	def phoneTabReset(self):
		self._callList.clearContents()
		self._callList.setRowCount(0)
		self._contactList.clearContents()
		self._contactList.setRowCount(0)
		self.phoneTabInit()


	### Click on phone tab
	def phoneTabClick(self):
		if not self._phoneDataLoaded:
			self._phoneDataLoaded = True	# Must be first to avoid reentrency during tab drag&drop
			self.loadContactList()	# Load it first for dynamic contact matching in call list
			self.loadCallList()


	### Click on call list item
	def callListClick(self):
		i = self._callList.currentRow()
		if i >= 0:
			self._deleteCallButton.setEnabled(True)
			self._spamCallSitesButton.setEnabled(True)

			# Activate & set Set Spam button title according to call type
			aCallType = self._callList.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
			if (aCallType == 1) or (aCallType == 3):	# Call received or missed
				aContactSource = self._callList.item(i, CallCol.ContactSource).text()
				if (aContactSource == 'N') or (aContactSource == 'S'):		# None or Spam
					self._setSpamCallButton.setEnabled(True)
					if aContactSource == 'S':
						self._setSpamCallButton.setText(lx('Unset as spam'))
					else:
						self._setSpamCallButton.setText(lx('Set as spam'))
				else:
					self._setSpamCallButton.setEnabled(False)
			else:
				self._setSpamCallButton.setEnabled(False)
		else:
			self._deleteCallButton.setEnabled(False)
			self._spamCallSitesButton.setEnabled(False)
			self._setSpamCallButton.setEnabled(False)


	### Click on contact list item
	def contactListClick(self):
		i = self._contactList.currentRow()
		if i >= 0:
			self._editContactButton.setEnabled(True)
			self._deleteContactButton.setEnabled(True)
		else:
			self._editContactButton.setEnabled(False)
			self._deleteContactButton.setEnabled(False)


	### Click on call list refresh button
	def refreshCallButtonClick(self):
		self._callList.clearContents()
		self._callList.setRowCount(0)
		self.loadCallList()


	### Click on spam calls scan button
	def spamCallScanButtonClick(self):
		if len(LmConf.CallFilterApiKey):
			self.scanSpams()
		else:
			self.displayError(mx('You must configure a CallFilter API Key in the preferences first.', 'callFilterAPIKeyErr'))


	### Click on spam call sites button
	def spamCallSitesButtonClick(self):
		i = self._callList.currentRow()
		if i >= 0:
			aPhoneNb = LmPhone.intlPhoneNumber(self._callList.item(i, CallCol.Number).text(), False)
			webbrowser.open_new_tab(CHECK_SPAM_URL1.format(aPhoneNb))
			webbrowser.open_new_tab(CHECK_SPAM_URL2.format(aPhoneNb))
		else:
			self.displayError(mx('Please select a phone call.', 'callSelect'))


	### Click on set/unset spam call button
	def setSpamCallButtonClick(self):
		i = self._callList.currentRow()
		if i >= 0:
			aCallType = self._callList.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
			if (aCallType == 1) or (aCallType == 3):	# Call received or missed
				aPhoneNb = LmPhone.intlPhoneNumber(self._callList.item(i, CallCol.Number).text())
				aSource = self._callList.item(i, CallCol.ContactSource).text()
				if (aSource == 'S'):		# Flagged as spam
					LmConf.unsetSpamCall(aPhoneNb)
					aSet = False
				else:
					LmConf.setSpamCall(aPhoneNb)
					aSet = True
		else:
			self.displayError(mx('Please select a phone call.', 'callSelect'))
			return

		# Update all lines with same number
		self._callList.setSortingEnabled(False)
		n = self._callList.rowCount()
		i = 0
		while (i < n):
			aCallType = self._callList.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
			if (aCallType == 1) or (aCallType == 3):	# Call received or missed
				aLinePhoneNb = LmPhone.intlPhoneNumber(self._callList.item(i, CallCol.Number).text())
				if aLinePhoneNb == aPhoneNb:
					self.displaySpamCall(i, aSet)
			i += 1
		self._callList.setSortingEnabled(True)

		self.callListClick()


	### Click on delete call button
	def deleteCallButtonClick(self):
		aCurrentSelection = self._callList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._callList.item(aCurrentSelection, CallCol.Key).text()
			try:
				aReply = self._session.request('VoiceService.VoiceApplication', 'clearCallList', { 'callId': aKey })
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Phone call delete query error.')
				return

			if (aReply is not None) and ('status' in aReply):
				self._callList.removeRow(aCurrentSelection)
			else:
				self.displayError('Phone call delete query failed.')
		else:
			self.displayError(mx('Please select a phone call.', 'callSelect'))


	### Click on delete all calls button
	def deleteAllCallsButtonClick(self):
		if self.askQuestion(mx('Are you sure you want to delete all phone calls?', 'delAllCalls')):
			self.startTask(lx('Deleting phone call list...'))
			try:
				aReply = self._session.request('VoiceService.VoiceApplication', 'clearCallList')
			except BaseException as e:
				self.endTask()
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Delete all calls query error.')
				return
			self.endTask()

			if (aReply is not None) and ('status' in aReply):
				self.refreshCallButtonClick()
			else:
				self.displayError('Delete all calls query failed.')


	### Double click on a call to add/edit corresponding contact
	def editContactFromCallListClick(self):
		aCurrentSelection = self._callList.currentRow()
		if aCurrentSelection >= 0:
			aName = self._callList.item(aCurrentSelection, CallCol.Contact).text()
			n = self._contactList.rowCount()

			# Try first to find the contact by phone number
			aRawPhoneNb = self._callList.item(aCurrentSelection, CallCol.Number).text()
			aPhoneNb  = LmPhone.intlPhoneNumber(aRawPhoneNb)
			if len(aPhoneNb):
				i = 0
				while (i < n):
					if ((LmPhone.intlPhoneNumber(self._contactList.item(i, ContactCol.Cell).text()) == aPhoneNb) or
						(LmPhone.intlPhoneNumber(self._contactList.item(i, ContactCol.Home).text()) == aPhoneNb) or
						(LmPhone.intlPhoneNumber(self._contactList.item(i, ContactCol.Work).text()) == aPhoneNb)):
						self.editContactDialog(i)
						return
					i += 1

			# Then try to find the contact by name
			if len(aName):
				i = 0
				while (i < n):
					if self._contactList.item(i, ContactCol.Name).text() == aName:
						self.editContactDialog(i)
						return
					i += 1

			# If not found then propose to create a contact from phone call data
			aContact = {}
			aSep = aName.find(' ')
			if aSep > 0:
				aContact['name'] = aName[0:aSep]
				aContact['firstname'] = aName[aSep + 1:]
			else:
				aContact['name'] = aName
				aContact['firstname'] = ''
			aContact['cell'] = aRawPhoneNb
			aContact['home'] = ''
			aContact['work'] = ''
			aContact['ringtone'] = '1'
			self.addContactDialog(aContact)


	### Load phone call list
	def loadCallList(self):
		self.startTask(lx('Loading phone call list...'))

		self._callList.setSortingEnabled(False)

		aCallList = self._session.request('VoiceService.VoiceApplication', 'getCallList', [{ 'line': '1' }], iTimeout = 8)
		if aCallList is not None:
			aCallList = aCallList.get('status')
		if aCallList is None:
			self.displayError(mx('Error getting phone call list.', 'callLoad'))
		else:
			i = 0
			for c in aCallList:
				self._callList.insertRow(i)

				aKey = QtWidgets.QTableWidgetItem(c.get('callId', ''))

				aCallTypeIcon = LmTools.NumericSortItem()
				aStatus = c.get('callType', '')
				aOrigin = c.get('callOrigin', '')
				if aStatus == 'succeeded':
					if aOrigin == 'local':
						aCallTypeIcon.setIcon(QtGui.QIcon(LmIcon.CallOutPixmap))
						aCallTypeIcon.setData(QtCore.Qt.ItemDataRole.UserRole, 2)
						aMissedCall = False
					else:
						aCallTypeIcon.setIcon(QtGui.QIcon(LmIcon.CallInPixmap))
						aCallTypeIcon.setData(QtCore.Qt.ItemDataRole.UserRole, 3)
						aMissedCall = False
				else:
					if aOrigin == 'local':
						aCallTypeIcon.setIcon(QtGui.QIcon(LmIcon.CallFailedPixmap))
						aCallTypeIcon.setData(QtCore.Qt.ItemDataRole.UserRole, 4)
						aMissedCall = False
					else:
						aCallTypeIcon.setIcon(QtGui.QIcon(LmIcon.CallMissedPixmap))
						aCallTypeIcon.setData(QtCore.Qt.ItemDataRole.UserRole, 1)
						aMissedCall = True

				aTime = QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(c.get('startTime')))
				aTime.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				aNumber = QtWidgets.QTableWidgetItem(c.get('remoteNumber'))
				aNumber.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				aContactStr = c.get('remoteName')
				if len(aContactStr):
					aContactSource = QtWidgets.QTableWidgetItem('L')	# Livebox source
				else:
					aContactSource = QtWidgets.QTableWidgetItem('N')	# None
				aContact = QtWidgets.QTableWidgetItem(aContactStr)

				aSeconds = c.get('duration')
				aDuration = LmTools.NumericSortItem(LmTools.FmtTime(aSeconds, True))
				aDuration.setData(QtCore.Qt.ItemDataRole.UserRole, aSeconds)
				aDuration.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)

				if aMissedCall:
					aTime.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
					aNumber.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
					aContact.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
					aDuration.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))

				self._callList.setItem(i, CallCol.Key, aKey)
				self._callList.setItem(i, CallCol.Type, aCallTypeIcon)
				self._callList.setItem(i, CallCol.Time, aTime)
				self._callList.setItem(i, CallCol.Number, aNumber)
				self._callList.setItem(i, CallCol.ContactSource, aContactSource)
				self._callList.setItem(i, CallCol.Contact, aContact)
				self._callList.setItem(i, CallCol.Duration, aDuration)

				i += 1
			self.assignContactToCalls()
			self.indicateSpamCalls()

		self._callList.sortItems(CallCol.Time, QtCore.Qt.SortOrder.DescendingOrder)

		self._callList.setSortingEnabled(True)
		self.callListClick()

		self.endTask()


	### Assign contacts to calls via matching context
	def assignContactToCalls(self):
		self._callList.setSortingEnabled(False)

		n = self._callList.rowCount()
		i = 0
		while (i < n):
			if self._callList.item(i, CallCol.ContactSource).text() != 'L':
				aPhoneNb = LmPhone.intlPhoneNumber(self._callList.item(i, CallCol.Number).text())
				aContactName = self.findMatchingContact(aPhoneNb)
				if aContactName is not None:
					aContactSource = QtWidgets.QTableWidgetItem('P')	# Program source
					aForeground = self._callList.item(i, CallCol.Contact).foreground()
					aContact = QtWidgets.QTableWidgetItem(aContactName)
					aContact.setForeground(aForeground)
					self._callList.setItem(i, CallCol.ContactSource, aContactSource)
					self._callList.setItem(i, CallCol.Contact, aContact)
			i += 1

		self._callList.setSortingEnabled(True)


	### Assign spam contact name to all calls in the spam table
	def indicateSpamCalls(self):
		self._callList.setSortingEnabled(False)

		n = self._callList.rowCount()
		i = 0
		while (i < n):
			aCallType = self._callList.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
			if (((aCallType == 1) or (aCallType == 3)) and	# Call received or missed
				self._callList.item(i, CallCol.ContactSource).text() == 'N'):
				aPhoneNb = LmPhone.intlPhoneNumber(self._callList.item(i, CallCol.Number).text())
				if aPhoneNb in LmConf.SpamCallsTable:
					self.displaySpamCall(i)
			i += 1

		self._callList.setSortingEnabled(True)


	### Scan call list to detect spams via CallFilter API
	def scanSpams(self):
		self._callList.setSortingEnabled(False)

		n = self._callList.rowCount()
		i = 0
		aSpamCount = 0
		aAlreadyChecked = []
		while (i < n):
			aCallType = self._callList.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
			if (((aCallType == 1) or (aCallType == 3)) and	# Call received or missed
				self._callList.item(i, CallCol.ContactSource).text() == 'N'):
				aRawPhoneNb = self._callList.item(i, CallCol.Number).text()
				aFullPhoneNb = LmPhone.intlPhoneNumber(aRawPhoneNb)
				if aFullPhoneNb not in aAlreadyChecked:
					aAlreadyChecked.append(aFullPhoneNb)
					aPhoneNb = LmPhone.intlPhoneNumber(aRawPhoneNb, False)
					if LmPhone.isSpam(aPhoneNb):
						LmConf.setSpamCall(aFullPhoneNb)
						aSpamCount += 1
			i += 1

		self._callList.setSortingEnabled(True)

		if aSpamCount:
			self.indicateSpamCalls()
		self.displayStatus(mx('Number of detected spam numbers: {}.', 'spamCount').format(aSpamCount))


	### Assign spam contact name to calls in the spam table
	def displaySpamCall(self, iIndex, iSpam = True):
		if iSpam:
			aSource = 'S'	# Spam
			aName = SPAM_CONTACT_NAME
		else:
			aSource = 'N'	# None
			aName = ''
		aContactSource = QtWidgets.QTableWidgetItem(aSource)
		aForeground = self._callList.item(iIndex, CallCol.Contact).foreground()
		aContact = QtWidgets.QTableWidgetItem(aName)
		aContact.setForeground(aForeground)
		self._callList.setItem(iIndex, CallCol.ContactSource, aContactSource)
		self._callList.setItem(iIndex, CallCol.Contact, aContact)


	### Check if number is spam via CallFilter API
	@staticmethod
	def isSpam(iPhoneNumber):
		if len(LmConf.CallFilterApiKey) and len(iPhoneNumber):
			try:
				aData = requests.get(CALLFILTER_URL.format(LmConf.CallFilterApiKey, iPhoneNumber), timeout = 2)
				aData = json.loads(aData.content)
				aSpam = aData.get('blocked')
				if aSpam is not None:
					return aSpam != 0
				else:
					LmTools.Error('CallFilter response error: no blocked field')
			except BaseException as e:
				LmTools.Error('CallFilter error: {}'.format(e))
		return False


	### Click on contact list refresh button
	def refreshContactButtonClick(self):
		self._contactList.clearContents()
		self._contactList.setRowCount(0)
		self.loadContactList()


	### Click on add contact button
	def addContactButtonClick(self):
		self.addContactDialog(None)


	### Click on edit contact button
	def editContactButtonClick(self):
		aCurrentSelection = self._contactList.currentRow()
		if aCurrentSelection >= 0:
			self.editContactDialog(aCurrentSelection)
		else:
			self.displayError(mx('Please select a contact.', 'contactSelect'))


	### Click on delete contact button
	def deleteContactButtonClick(self):
		aCurrentSelection = self._contactList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._contactList.item(aCurrentSelection, ContactCol.Key).text()
			try:
				aReply = self._session.request('Phonebook', 'removeContactByUniqueID', { 'uniqueID': aKey })
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Contact delete query error.')
				return

			if (aReply is not None) and (aReply.get('status', False)):
				aContact = self.getContactRow(aCurrentSelection)
				self.rmvContactFromMatchingIndex(aContact)
				self._contactList.removeRow(aCurrentSelection)
				self.assignContactToCalls()
			else:
				self.displayError('Contact delete query failed.')
		else:
			self.displayError(mx('Please select a contact.', 'contactSelect'))


	### Click on delete all contacts button
	def deleteAllContactsButtonClick(self):
		if self.askQuestion(mx('Are you sure you want to delete all contacts?', 'delAllContacts')):
			self.startTask(lx('Deleting contact list...'))
			try:
				aReply = self._session.request('Phonebook', 'removeAllContacts')
			except BaseException as e:
				self.endTask()
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Delete all contacts query error.')
				return
			self.endTask()

			if (aReply is not None) and (aReply.get('status', False)):
				self.refreshContactButtonClick()
			else:
				self.displayError('Delete all contacts query failed.')


	### Click on Phone Ring button
	def phoneRingButtonClick(self):
		aRingTone = self._ringToneCombo.currentText()
		if (aRingTone == '-'):
			aParams = {}
		else:
			aParams = { "ringtone": aRingTone }

		LmTools.MouseCursor_Busy()
		try:
			d = self._session.request('VoiceService.VoiceApplication', 'ring', aParams)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		LmTools.MouseCursor_Normal()

		if d is None:
			self.displayError('Ring service error.')
		else:
			self.displayStatus(mx('Phone should be ringing.', 'ring'))


	### Click on export contacts button
	def exportContactsButtonClick(self):
		aFileName = QtWidgets.QFileDialog.getSaveFileName(self, lx('Export File'), lx('Livebox Contacts') + '.vcf', '*.vcf')
		aFileName = aFileName[0]
		if aFileName == '':
			return

		try:
			aExportFile = open(aFileName, 'w', encoding = 'utf-8')	# VCF standard charset is UTF-8
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError(mx('Cannot create the file.', 'createFileErr'))
			return

		self.startTask(lx('Exporting all contacts...'))

		aContactList = self._session.request('Phonebook', 'getAllContacts', iTimeout = 20)
		if aContactList is not None:
			aContactList = aContactList.get('status')
		if aContactList is None:
			self.displayError(mx('Error getting contact list.', 'contactLoad'))
		else:
			for c in aContactList:
				aContact = self.decodeLiveboxContact(c)
				aExportFile.write('BEGIN:VCARD\n')
				aExportFile.write('VERSION:3.0\n')
				aExportFile.write('PRODID:' + self._applicationName + '\n')
				aExportFile.write('FN:' + aContact['formattedName'] + '\n')
				aExportFile.write('N:' + aContact['name'] + ';' + aContact['firstname'] + ';;;\n')
				aExportFile.write('TEL;TYPE=CELL:' + aContact['cell'] + '\n')
				aExportFile.write('TEL;TYPE=HOME:' + aContact['home'] + '\n')
				aExportFile.write('TEL;TYPE=WORK:' + aContact['work'] + '\n')
				aExportFile.write('RINGTONE:' + aContact['ringtone'] + '\n')
				aExportFile.write('END:VCARD\n')

		self.endTask()

		try:
			aExportFile.close()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError(mx('Cannot save the file.', 'saveFileErr'))


	### Click on import contacts button
	def importContactsButtonClick(self):
		aFiles = QtWidgets.QFileDialog.getOpenFileNames(self, lx('Select files to import'), '', '*.vcf')
		aFiles = aFiles[0]

		self.startTask(lx('Importing contacts...'))
		self._contactList.setSortingEnabled(False)

		aFileError = []
		for f in aFiles:
			aResult = self.importVcfFile(f)
			if aResult == 0:
				aFileError.append(os.path.basename(f))
			elif aResult < 0:
				break

		self._contactList.setSortingEnabled(True)

		self.assignContactToCalls()
		self.endTask()

		if len(aFileError):
			aErrorStr = lx('Cannot import file(s): ')
			for f in aFileError:
				aErrorStr += f + ', '
			n = len(aErrorStr)
			aErrorStr = aErrorStr[:n - 2] + '.'
			self.displayError(aErrorStr)


	### VCF file import, returns: 1=Success, 0=File error, -1=Stop all error
	def importVcfFile(self, iFile):
		try:
			f = open(iFile, 'r', encoding = 'utf-8')	# VCF standard charset is UTF-8
		except:
			return 0

		c = None
		try:
			for l in f:
				# Get tag structure
				i = l.find(':')
				if i < 1:
					continue
				aTagStruct = l[:i].upper()
				l = l[i + 1:].rstrip('\n')

				# Some tags are build like "item1.TEL;...", remove to ease parsing
				if aTagStruct.startswith('ITEM'):
					i = aTagStruct.find('.')
					if i >= 0:
						aTagStruct = aTagStruct[i + 1:]

				# Decode tag structure to get tag name and its parameters
				aTagElems = aTagStruct.split(';')
				aTag = None
				aTagParams = {}
				for e in aTagElems:
					if aTag is None:
						aTag = e
					else:
						i = e.find('=')
						if i >= 0:
							aTagParams[e[:i]] = e[i + 1:]
						else:
							aTagParams[e] = ''

				if aTag == 'BEGIN':
					# Create a blank contact
					if l.upper() == 'VCARD':
						c = {}
						c['firstname'] = ''
						c['name'] = ''
						c['formattedName'] = ''
						c['cell'] = ''
						c['home'] = ''
						c['work'] = ''
						c['ringtone'] = '1'

				elif aTag == 'END':
					# Import the decoded contact
					if (l.upper() == 'VCARD') and (c is not None):
						if self.addLiveboxContact(c):
							self._contactList.insertRow(0)
							self.setContactRow(0, c)
							self.addContactToMatchingIndex(c)
							QtCore.QCoreApplication.processEvents()
						else:
							f.close()
							return -1
						c = None
				else:
					LmPhone.importVcfTag(c, aTag, aTagParams, l)
		except BaseException as aExcept:
			LmTools.Error('Error: {}'.format(aExcept))
			f.close()
			return 0

		f.close()
		return 1


	### VCF tag import
	@staticmethod
	def importVcfTag(iContact, iTag, iParams, iVal):
		if iContact is None:
			return

		# Name tag
		if iTag == 'N':
			# Replace semicolon escape sequences by spaces
			iVal = iVal.replace(r'\;', ' ')

			# Get name & firstname
			s = iVal.split(';')
			if len(s) > 1:
				iContact['name']  = s[0].strip()
				iContact['firstname'] = s[1].strip()
			else:
				iContact['name']  = s[0].strip()
				iContact['firstname'] = ''
			iContact['formattedName'] = LmPhone.computeFormattedName(iContact['name'], iContact['firstname'])

		# Phone number tag
		elif iTag == 'TEL':
			# Get type, use cell if none specified
			aType = iParams.get('TYPE', 'CELL')

			# Assign the phone number according to its type
			if aType == 'HOME':
				iContact['home'] = LmPhone.vcfPhoneNumberCleanup(iVal)
			elif aType == 'WORK':
				iContact['work'] = LmPhone.vcfPhoneNumberCleanup(iVal)
			else:
				iContact['cell'] = LmPhone.vcfPhoneNumberCleanup(iVal)

		# Ring tone tag (not standard)
		elif iTag == 'RINGTONE':
			if (len(iVal) == 1) and (iVal in '1234567'):
				iContact['ringtone'] = iVal


	### VCF phone number cleanup
	@staticmethod
	def vcfPhoneNumberCleanup(iPhoneNumber):
		if (len(iPhoneNumber)) and (iPhoneNumber[0] == '+'):
			n = '00'
			iPhoneNumber = iPhoneNumber[1:]
		else:
			n = ''

		for c in iPhoneNumber:
			if c in r'0123456789*#':
				n += c

		return n


	### Convert phone numbers to intl format if local
	@staticmethod
	def intlPhoneNumber(iPhoneNumber, iFull = True):
		if ((len(iPhoneNumber) < 2) or
			iPhoneNumber.startswith('00') or
			(iPhoneNumber[0] != '0')):
			return iPhoneNumber

		if iFull:
			return '00' + LmConf.PhoneCode + iPhoneNumber[1:]
		return LmConf.PhoneCode + iPhoneNumber[1:]


	### Compute formatted name from name and firstname
	@staticmethod
	def computeFormattedName(iName, iFirstname):
		if len(iName):
			if len(iFirstname):
				return iName + ' ' + iFirstname
			return iName
		return iFirstname


	### Load contact list
	def loadContactList(self):
		self.startTask(lx('Loading contact list...'))

		self._contactList.setSortingEnabled(False)

		self._contactMatching = {}
		aContactList = self._session.request('Phonebook', 'getAllContacts', iTimeout = 20)
		if aContactList is not None:
			aContactList = aContactList.get('status')
		if aContactList is None:
			self.displayError(mx('Error getting contact list.', 'contactLoad'))
		else:
			i = 0
			for c in aContactList:
				self._contactList.insertRow(i)
				aContact = self.decodeLiveboxContact(c)
				self.setContactRow(i, aContact)
				self.addContactToMatchingIndex(aContact)
				i += 1

		self._contactList.sortItems(ContactCol.Name, QtCore.Qt.SortOrder.AscendingOrder)
		self._contactList.setSortingEnabled(True)
		self.assignContactToCalls()
		self.contactListClick()

		self.endTask()


	### Get contact from Livebox contact structure
	def decodeLiveboxContact(self, iLiveboxContact):
		aContact = {}
		aContact['key'] = iLiveboxContact.get('uniqueID', '')

		aName = iLiveboxContact.get('name', '')
		s = aName.split(';')
		if len(s) > 1:
			aContact['name'] = s[0][2:]
			aContact['firstname'] = s[1]
		else:
			aContact['name']  = ''
			aContact['firstname'] = ''

		aContact['formattedName'] = iLiveboxContact.get('formattedName', '')

		aContact['cell'] = ''
		aContact['home'] = ''
		aContact['work'] = ''
		aNumbers = iLiveboxContact.get('telephoneNumbers')
		if type(aNumbers).__name__ == 'list':
			for n in aNumbers:
				aType = n.get('type', '')
				if aType == 'CELL':
					aContact['cell'] = n.get('name', '')
				elif aType == 'HOME':
					aContact['home'] = n.get('name', '')
				elif aType == 'WORK':
					aContact['work'] = n.get('name', '')

		aContact['ringtone'] = iLiveboxContact.get('ringtone', '1')

		return aContact


	### Set contact row
	def setContactRow(self, iLine, iContact):
		aKey = QtWidgets.QTableWidgetItem(iContact['key'])

		aContactName = QtWidgets.QTableWidgetItem(iContact['formattedName'])

		aCellNb = QtWidgets.QTableWidgetItem(iContact['cell'])
		aCellNb.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		aHomeNb = QtWidgets.QTableWidgetItem(iContact['home'])
		aHomeNb.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		aWorkNb = QtWidgets.QTableWidgetItem(iContact['work'])
		aWorkNb.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

		aRingTone = QtWidgets.QTableWidgetItem(iContact['ringtone'])
		aRingTone.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

		self._contactList.setItem(iLine, ContactCol.Key, aKey)
		self._contactList.setItem(iLine, ContactCol.Name, aContactName)
		self._contactList.setItem(iLine, ContactCol.Cell, aCellNb)
		self._contactList.setItem(iLine, ContactCol.Home, aHomeNb)
		self._contactList.setItem(iLine, ContactCol.Work, aWorkNb)
		self._contactList.setItem(iLine, ContactCol.Ring, aRingTone)


	### Get contact from row
	def getContactRow(self, iLine):
		aContact = {}
		aContact['key'] = self._contactList.item(iLine, ContactCol.Key).text()
		aContact['formattedName'] = self._contactList.item(iLine, ContactCol.Name).text()
		aContact['cell'] = self._contactList.item(iLine, ContactCol.Cell).text()
		aContact['home'] = self._contactList.item(iLine, ContactCol.Home).text()
		aContact['work'] = self._contactList.item(iLine, ContactCol.Work).text()
		aContact['ringtone'] = self._contactList.item(iLine, ContactCol.Ring).text()
		return aContact


	### Add contact dialog
	def addContactDialog(self, iDefaultContactData):
		aAddContactDialog = EditContactDialog(False, iDefaultContactData, self)
		if aAddContactDialog.exec():
			aContact = aAddContactDialog.getContact()
			if self.addLiveboxContact(aContact):
				self._contactList.setSortingEnabled(False)
				self._contactList.insertRow(0)
				self.setContactRow(0, aContact)
				self._contactList.setSortingEnabled(True)
				self.addContactToMatchingIndex(aContact)
				self.assignContactToCalls()


	### Add a contact in Livebox
	def addLiveboxContact(self, iContact):
		aData = {}
		aData['name'] = 'N:' + iContact['name'] + ';' + iContact['firstname'] + ';'
		aData['formattedName'] = iContact['formattedName']
		aData['ringtone'] = iContact['ringtone']
		aPhoneNumbers = []
		aNumber = {}
		aNumber['name'] = iContact['cell']
		aNumber['type'] = 'CELL'
		aNumber['preferred'] = False
		aPhoneNumbers.append(aNumber)
		aNumber = {}
		aNumber['name'] = iContact['work']
		aNumber['type'] = 'WORK'
		aNumber['preferred'] = False
		aPhoneNumbers.append(aNumber)
		aNumber = {}
		aNumber['name'] = iContact['home']
		aNumber['type'] = 'HOME'
		aNumber['preferred'] = False
		aPhoneNumbers.append(aNumber)
		aData['telephoneNumbers'] = aPhoneNumbers

		try:
			aReply = self._session.request('Phonebook', 'addContactAndGenUUID', { 'contact': aData })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Contact creation query error.')
			return False

		if (aReply is not None) and ('status' in aReply):
			aKey = aReply['status']
			if aKey is None:
				self.displayError(mx('Max number of contacts reached.', 'contactMax'))
				return False
			iContact['key'] = aReply['status']
			return True

		self.displayError('Contact creation query failed.')
		return False


	### Edit contact dialog
	def editContactDialog(self, iLine):
		aKey = self._contactList.item(iLine, ContactCol.Key).text()

		# First retrieve a fresh copy of the contact
		try:
			aReply = self._session.request('Phonebook', 'getContactByUniqueID', { 'uniqueID': aKey })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Contact query error.')
			return
		if (aReply is None) or ('status' not in aReply):
			self.displayError(mx('Cannot retrieve contact.', 'contactGet'))
			return
		aLBContact = aReply['status']
		aContact = self.decodeLiveboxContact(aLBContact)

		# Edit dialog
		aEditContactDialog = EditContactDialog(True, aContact, self)
		if aEditContactDialog.exec():
			aContact = aEditContactDialog.getContact()
			aLBContact['name'] = 'N:' + aContact['name'] + ';' + aContact['firstname'] + ';'
			aLBContact['n'] = 'N:' + aContact['name'] + ';' + aContact['firstname'] + ';;;;;;;'
			aLBContact['formattedName'] = aContact['formattedName']
			aLBContact['ringtone'] = aContact['ringtone']
			aPhoneNumbers = []
			aNumber = {}
			aNumber['name'] = aContact['cell']
			aNumber['type'] = 'CELL'
			aNumber['preferred'] = False
			aPhoneNumbers.append(aNumber)
			aNumber = {}
			aNumber['name'] = aContact['work']
			aNumber['type'] = 'WORK'
			aNumber['preferred'] = False
			aPhoneNumbers.append(aNumber)
			aNumber = {}
			aNumber['name'] = aContact['home']
			aNumber['type'] = 'HOME'
			aNumber['preferred'] = False
			aPhoneNumbers.append(aNumber)
			aLBContact['telephoneNumbers'] = aPhoneNumbers

			# Perform updates
			try:
				aReply = self._session.request('Phonebook', 'modifyContactByUniqueID', { 'uniqueID': aKey, 'contact': aLBContact })
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('Contact update query error.')
				return

			if (aReply is not None) and (aReply.get('status', False)):
				aCurrentContact = self.getContactRow(iLine)
				self.rmvContactFromMatchingIndex(aCurrentContact)
				self._contactList.setSortingEnabled(False)
				self.setContactRow(iLine, aContact)
				self._contactList.setSortingEnabled(True)
				self.addContactToMatchingIndex(aContact)
				self.assignContactToCalls()
			else:
				self.displayError('Contact update query failed.')


	### Add contact to matching index
	def addContactToMatchingIndex(self, iContact):
		aContactEntry = { 'key': iContact['key'], 'name': iContact['formattedName'] }
		self.addNumberToMatchingIndex(LmPhone.intlPhoneNumber(iContact['cell']), aContactEntry)
		self.addNumberToMatchingIndex(LmPhone.intlPhoneNumber(iContact['work']), aContactEntry)
		self.addNumberToMatchingIndex(LmPhone.intlPhoneNumber(iContact['home']), aContactEntry)


	### Remove contact from matching index
	def rmvContactFromMatchingIndex(self, iContact):
		aContactEntry = { 'key': iContact['key'], 'name': iContact['formattedName'] }
		self.rmvNumberFromMatchingIndex(LmPhone.intlPhoneNumber(iContact['cell']), aContactEntry)
		self.rmvNumberFromMatchingIndex(LmPhone.intlPhoneNumber(iContact['work']), aContactEntry)
		self.rmvNumberFromMatchingIndex(LmPhone.intlPhoneNumber(iContact['home']), aContactEntry)


	### Add a phone number to matching index
	def addNumberToMatchingIndex(self, iPhoneNumber, iContactEntry):
		if len(iPhoneNumber):
			aPhoneEntry = self._contactMatching.get(iPhoneNumber)
			if aPhoneEntry is None:
				self._contactMatching[iPhoneNumber] = [ iContactEntry ]
			else:
				self._contactMatching[iPhoneNumber].append(iContactEntry)


	### Remove a phone number from matching index
	def rmvNumberFromMatchingIndex(self, iPhoneNumber, iContactEntry):
		if len(iPhoneNumber):
			aPhoneEntry = self._contactMatching.get(iPhoneNumber)
			if aPhoneEntry is not None:
				try:
					self._contactMatching[iPhoneNumber].remove(iContactEntry)
				except:
					pass


	### Find a contact name matching a phone number
	def findMatchingContact(self, iPhoneNumber):
		if len(iPhoneNumber):
			aPhoneEntry = self._contactMatching.get(iPhoneNumber)
			if aPhoneEntry is not None:
				n = len(aPhoneEntry)
				if n:
					return aPhoneEntry[n - 1]['name']
		return None



# ############# Edit contact dialog #############
class EditContactDialog(QtWidgets.QDialog):
	def __init__(self, iEditMode, iContact = None, iParent = None):
		super(EditContactDialog, self).__init__(iParent)
		self.resize(320, 170)

		self._ready = False

		aFirstNameEditLabel = QtWidgets.QLabel(lcx('First name'), objectName = 'firstNameLabel')
		self._firstNameEdit = QtWidgets.QLineEdit(objectName = 'firstNameEdit')
		self._firstNameEdit.textChanged.connect(self.textChanged)

		aNameEditLabel = QtWidgets.QLabel(lcx('Name'), objectName = 'nameLabel')
		self._nameEdit = QtWidgets.QLineEdit(objectName = 'nameEdit')
		self._nameEdit.textChanged.connect(self.textChanged)

		aPhoneNbRegExp = QtCore.QRegularExpression(r'^[0-9+*#]{1}[0-9*#]{19}$')
		aPhoneNbValidator = QtGui.QRegularExpressionValidator(aPhoneNbRegExp)

		aCellEditLabel = QtWidgets.QLabel(lcx('Mobile'), objectName = 'cellLabel')
		self._cellEdit = QtWidgets.QLineEdit(objectName = 'cellEdit')
		self._cellEdit.setValidator(aPhoneNbValidator)
		self._cellEdit.textChanged.connect(self.textChanged)

		aHomeEditLabel = QtWidgets.QLabel(lcx('Home'), objectName = 'homeLabel')
		self._homeEdit = QtWidgets.QLineEdit(objectName = 'homeEdit')
		self._homeEdit.setValidator(aPhoneNbValidator)
		self._homeEdit.textChanged.connect(self.textChanged)

		aWorkEditLabel = QtWidgets.QLabel(lcx('Work'), objectName = 'workLabel')
		self._workEdit = QtWidgets.QLineEdit(objectName = 'workEdit')
		self._workEdit.setValidator(aPhoneNbValidator)
		self._workEdit.textChanged.connect(self.textChanged)

		aRingToneEditLabel = QtWidgets.QLabel(lcx('Ring tone'), objectName = 'ringToneLabel')
		self._ringToneCombo = QtWidgets.QComboBox(objectName = 'ringToneCombo')
		i = 1
		while i <= 7:
			self._ringToneCombo.addItem(str(i))
			i += 1

		aEditGrid = QtWidgets.QGridLayout()
		aEditGrid.setSpacing(10)
		aEditGrid.addWidget(aFirstNameEditLabel, 0, 0)
		aEditGrid.addWidget(self._firstNameEdit, 0, 1)
		aEditGrid.addWidget(aNameEditLabel, 1, 0)
		aEditGrid.addWidget(self._nameEdit, 1, 1)
		aEditGrid.addWidget(aCellEditLabel, 2, 0)
		aEditGrid.addWidget(self._cellEdit, 2, 1)
		aEditGrid.addWidget(aHomeEditLabel, 3, 0)
		aEditGrid.addWidget(self._homeEdit, 3, 1)
		aEditGrid.addWidget(aWorkEditLabel, 4, 0)
		aEditGrid.addWidget(self._workEdit, 4, 1)
		aEditGrid.addWidget(aRingToneEditLabel, 5, 0)
		aEditGrid.addWidget(self._ringToneCombo, 5, 1)

		self._okButton = QtWidgets.QPushButton(lcx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lcx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aButtonBar = QtWidgets.QHBoxLayout()
		aButtonBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setSpacing(10)
		aButtonBar.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aEditGrid, 0)
		aVBox.addLayout(aButtonBar, 1)

		self._firstNameEdit.setFocus()

		LmConfig.SetToolTips(self, 'pcontact')

		if iEditMode:
			self.setWindowTitle(lcx('Contact edition'))
		else:
			self.setWindowTitle(lcx('Contact creation'))

		if iContact is None:
			self._contact = {}
		else:
			self._contact = iContact
			self._firstNameEdit.setText(iContact['firstname'])
			self._nameEdit.setText(iContact['name'])
			self._cellEdit.setText(iContact['cell'])
			self._homeEdit.setText(iContact['home'])
			self._workEdit.setText(iContact['work'])
			self._ringToneCombo.setCurrentIndex(int(iContact['ringtone']) - 1)

		self.setOkButtonState()
		self.setModal(True)
		self._ready = True
		self.show()


	def textChanged(self, iText):
		if self._ready:
			self.setOkButtonState()


	def setOkButtonState(self):
		c = self.getContact()
		if ((len(c['name']) == 0) and (len(c['firstname']) == 0)):
			self._okButton.setDisabled(True)
			return

		if ((len(c['cell']) == 0) and (len(c['home']) == 0) and (len(c['work']) == 0)):
			self._okButton.setDisabled(True)
			return

		self._okButton.setDisabled(False)


	def getContact(self):
		self._contact['firstname'] = EditContactDialog.cleanupName(self._firstNameEdit.text())
		self._contact['name'] = EditContactDialog.cleanupName(self._nameEdit.text())
		self._contact['formattedName'] = LmPhone.computeFormattedName(self._contact['name'], self._contact['firstname'])
		self._contact['cell'] = EditContactDialog.cleanupPhoneNumber(self._cellEdit.text())
		self._contact['home'] = EditContactDialog.cleanupPhoneNumber(self._homeEdit.text())
		self._contact['work'] = EditContactDialog.cleanupPhoneNumber(self._workEdit.text())
		self._contact['ringtone'] = self._ringToneCombo.currentText()
		return self._contact


	@staticmethod
	def cleanupName(iName):
		return iName.replace(';', ' ')


	@staticmethod
	def cleanupPhoneNumber(iPhoneNb):
		if len(iPhoneNb) and (iPhoneNb[0] == '+'):
			return '00' + iPhoneNb[1:]
		return iPhoneNb
