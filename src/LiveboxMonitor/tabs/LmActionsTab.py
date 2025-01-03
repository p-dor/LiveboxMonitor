### Livebox Monitor actions tab module ###

import json
import webbrowser

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmGenApiDocumentation
from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmConfig import LmConf, PrefsDialog, SetApplicationStyle, EmailSetupDialog
from LiveboxMonitor.lang.LmLanguages import (GetActionsLabel as lx,
											 GetActionsMessage as mx,
											 GetActionsRHistoryDialogLabel as lrx,
											 GetActionsWGlobalDialogLabel as lwx,
											 GetActionsBackupRestoreDialogLabel as lbx,
											 GetActionsFirewallLevelDialogLabel as lfx,
											 GetActionsPingResponseDialogLabel as lpx,
											 GetActionsDynDnsDialogLabel as ldx,
											 GetActionsDmzDialogLabel as lzx)

from LiveboxMonitor.__init__ import __url__, __copyright__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'actionTab'

# Static Config
BUTTON_WIDTH = 150

# Wifi status keys
class WifiKey:
	AccessPoint = 'Name'
	Enable = 'WE'
	Status = 'WS'
	Scheduler = 'SCH'
	Wifi2Enable = 'W2E'
	Wifi2Status = 'W2S'
	Wifi2VAP = 'W2V'
	Wifi5Enable = 'W5E'
	Wifi5Status = 'W5S'
	Wifi5VAP = 'W5V'
	Wifi6Enable = 'W6E'
	Wifi6Status = 'W6S'
	Wifi6VAP = 'W6V'
	Guest2VAP = 'G2V'
	Guest5VAP = 'G5V'

# Wifi status values
class WifiStatus:
	Enable = 'Y'
	Disable = 'N'
	Error = 'E'
	Inactive = 'I'
	Unsigned = 'S'

# Firewall levels
FIREWALL_LEVELS = ['High', 'Medium', 'Low', 'Custom']

# DynDNS host list columns
class HostCol(IntEnum):
	Service = 0
	HostName = 1
	UserName = 2
	Password = 3
	LastUpdate = 4
	Status = 5
	Count = 6

# DMZ device list columns
class DmzCol(IntEnum):
	ID = 0
	IP = 1
	Device = 2
	ExtIPs = 3
	Count = 4


# ################################ LmActions class ################################
class LmActions:

	### Create actions tab
	def createActionsTab(self):
		self._actionsTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# Wifi & Misc column
		aLeftZone = QtWidgets.QVBoxLayout()
		aLeftZone.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aLeftZone.setSpacing(20)

		# Wifi buttons group
		aWifiButtons = QtWidgets.QVBoxLayout()
		aWifiButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aWifiButtons.setSpacing(20)

		aWifiSet = QtWidgets.QHBoxLayout()
		aWifiSet.setSpacing(20)

		aWifiOnButton = QtWidgets.QPushButton(lx('Wifi ON'), objectName = 'wifiOn')
		aWifiOnButton.clicked.connect(self.wifiOnButtonClick)
		aWifiOnButton.setMinimumWidth(BUTTON_WIDTH)
		aWifiSet.addWidget(aWifiOnButton)

		aWifiOffButton = QtWidgets.QPushButton(lx('Wifi OFF'), objectName = 'wifiOff')
		aWifiOffButton.clicked.connect(self.wifiOffButtonClick)
		aWifiOffButton.setMinimumWidth(BUTTON_WIDTH)
		aWifiSet.addWidget(aWifiOffButton)
		aWifiButtons.addLayout(aWifiSet, 0)

		aGuestWifiSet = QtWidgets.QHBoxLayout()
		aGuestWifiSet.setSpacing(20)

		aGuestWifiOnButton = QtWidgets.QPushButton(lx('Guest Wifi ON'), objectName = 'guestWifiOn')
		aGuestWifiOnButton.clicked.connect(self.guestWifiOnButtonClick)
		aGuestWifiOnButton.setMinimumWidth(BUTTON_WIDTH)
		aGuestWifiSet.addWidget(aGuestWifiOnButton)

		aGuestWifiOffButton = QtWidgets.QPushButton(lx('Guest Wifi OFF'), objectName = 'guestWifiOff')
		aGuestWifiOffButton.clicked.connect(self.guestWifiOffButtonClick)
		aGuestWifiOffButton.setMinimumWidth(BUTTON_WIDTH)
		aGuestWifiSet.addWidget(aGuestWifiOffButton)
		aWifiButtons.addLayout(aGuestWifiSet, 0)

		aSchedulerSet = QtWidgets.QHBoxLayout()
		aSchedulerSet.setSpacing(20)

		aSchedulerOnButton = QtWidgets.QPushButton(lx('Wifi Scheduler ON'), objectName = 'schedulerOn')
		aSchedulerOnButton.clicked.connect(self.schedulerOnButtonClick)
		aSchedulerOnButton.setMinimumWidth(BUTTON_WIDTH)
		aSchedulerSet.addWidget(aSchedulerOnButton)

		aSchedulerOffButton = QtWidgets.QPushButton(lx('Wifi Scheduler OFF'), objectName = 'schedulerOff')
		aSchedulerOffButton.clicked.connect(self.schedulerOffButtonClick)
		aSchedulerOffButton.setMinimumWidth(BUTTON_WIDTH)
		aSchedulerSet.addWidget(aSchedulerOffButton)
		aWifiButtons.addLayout(aSchedulerSet, 0)

		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		aWifiButtons.addWidget(aSeparator)

		aWifiGlobalStatusButton = QtWidgets.QPushButton(lx('Show Global Status...'), objectName = 'wifiGlobalStatus')
		aWifiGlobalStatusButton.clicked.connect(self.wifiGlobalStatusButtonClick)
		aWifiButtons.addWidget(aWifiGlobalStatusButton)

		aWifiGroupBox = QtWidgets.QGroupBox(lx('Wifi'), objectName = 'wifiGroup')
		aWifiGroupBox.setLayout(aWifiButtons)
		aLeftZone.addWidget(aWifiGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Misc buttons
		aMiscButtons = QtWidgets.QVBoxLayout()
		aMiscButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aMiscButtons.setSpacing(20)

		aBackupRestoreButton = QtWidgets.QPushButton(lx('Backup and Restore...'), objectName = 'backupRestore')
		aBackupRestoreButton.clicked.connect(self.backupRestoreButtonClick)
		aBackupRestoreButton.setMinimumWidth(BUTTON_WIDTH)
		aMiscButtons.addWidget(aBackupRestoreButton)

		aMiscGroupBox = QtWidgets.QGroupBox(lx('Miscellaneous'), objectName = 'miscGroup')
		aMiscGroupBox.setLayout(aMiscButtons)
		aLeftZone.addWidget(aMiscGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Reboot & Firewall column
		aMiddleZone = QtWidgets.QVBoxLayout()
		aMiddleZone.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aMiddleZone.setSpacing(20)

		# Reboot buttons
		aRebootButtons = QtWidgets.QVBoxLayout()
		aRebootButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aRebootButtons.setSpacing(20)

		aRebootLiveboxButton = QtWidgets.QPushButton(lx('Reboot Livebox...'), objectName = 'rebootLivebox')
		aRebootLiveboxButton.clicked.connect(self.rebootLiveboxButtonClick)
		aRebootLiveboxButton.setMinimumWidth(BUTTON_WIDTH)
		aRebootButtons.addWidget(aRebootLiveboxButton)

		aRebootHistoryButton = QtWidgets.QPushButton(lx('Reboot History...'), objectName = 'rebootHistory')
		aRebootHistoryButton.clicked.connect(self.rebootHistoryButtonClick)
		aRebootHistoryButton.setMinimumWidth(BUTTON_WIDTH)
		aRebootButtons.addWidget(aRebootHistoryButton)

		aRebootGroupBox = QtWidgets.QGroupBox(lx('Reboots'), objectName = 'rebootGroup')
		aRebootGroupBox.setLayout(aRebootButtons)
		aMiddleZone.addWidget(aRebootGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Network buttons
		aNetworkButtons = QtWidgets.QVBoxLayout()
		aNetworkButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aNetworkButtons.setSpacing(20)

		aFirewallLevelButton = QtWidgets.QPushButton(lx('Firewall Levels...'), objectName = 'firewallLevel')
		aFirewallLevelButton.clicked.connect(self.firewallLevelButtonClick)
		aFirewallLevelButton.setMinimumWidth(BUTTON_WIDTH)
		aNetworkButtons.addWidget(aFirewallLevelButton)

		aPingResponseButton = QtWidgets.QPushButton(lx('Ping Responses...'), objectName = 'pingResponse')
		aPingResponseButton.clicked.connect(self.pingResponseButtonClick)
		aPingResponseButton.setMinimumWidth(BUTTON_WIDTH)
		aNetworkButtons.addWidget(aPingResponseButton)

		aDynDNSButton = QtWidgets.QPushButton(lx('DynDNS...'), objectName = 'dynDNS')
		aDynDNSButton.clicked.connect(self.dynDNSButtonClick)
		aDynDNSButton.setMinimumWidth(BUTTON_WIDTH)
		aNetworkButtons.addWidget(aDynDNSButton)

		aDmzButton = QtWidgets.QPushButton(lx('DMZ...'), objectName = 'dmz')
		aDmzButton.clicked.connect(self.dmzButtonClick)
		aDmzButton.setMinimumWidth(BUTTON_WIDTH)
		aNetworkButtons.addWidget(aDmzButton)

		aNetworkGroupBox = QtWidgets.QGroupBox(lx('Network'), objectName = 'networkGroup')
		aNetworkGroupBox.setLayout(aNetworkButtons)
		aMiddleZone.addWidget(aNetworkGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# About, preferences, debug and quit column
		aRightZone = QtWidgets.QVBoxLayout()

		# About box
		aAboutWidgets = QtWidgets.QVBoxLayout()
		aAboutWidgets.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aAboutWidgets.setSpacing(15)

		aAppIcon = QtWidgets.QLabel(objectName = 'appIcon')
		aAppIcon.setPixmap(LmIcon.AppIconPixmap)
		aAppIcon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		aAppIcon.setMaximumWidth(64)
		aAppIcon.setMinimumWidth(64)
		aAboutWidgets.addWidget(aAppIcon, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAppName = QtWidgets.QLabel(self._applicationName, objectName = 'appName')
		aAppName.setFont(LmTools.BOLD_FONT)
		aAboutWidgets.addWidget(aAppName, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAboutWidgets.addWidget(QtWidgets.QLabel(lx('An Open Source project')), 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aOpenSourceURL = QtWidgets.QLabel(__url__, objectName = 'openSourceURL')
		aOpenSourceURL.setStyleSheet('QLabel { color : blue }')
		aOpenSourceURL.mousePressEvent = self.openSourceButtonClick
		aAboutWidgets.addWidget(aOpenSourceURL, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAboutWidgets.addWidget(QtWidgets.QLabel(__copyright__), 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAboutGroupBox = QtWidgets.QGroupBox(lx('About'), objectName = 'aboutGroup')
		aAboutGroupBox.setLayout(aAboutWidgets)

		aRightZone.addWidget(aAboutGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Setup box
		aSetupButtons = QtWidgets.QVBoxLayout()
		aSetupButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aSetupButtons.setSpacing(15)

		aPrefsButton = QtWidgets.QPushButton(lx('Preferences...'), objectName = 'prefs')
		aPrefsButton.clicked.connect(self.prefsButtonClick)
		aSetupButtons.addWidget(aPrefsButton)

		aChangeProfileButton = QtWidgets.QPushButton(lx('Change Profile...'), objectName = 'changeProfile')
		aChangeProfileButton.clicked.connect(self.changeProfileButtonClick)
		aSetupButtons.addWidget(aChangeProfileButton)

		aEmailSetupButton = QtWidgets.QPushButton(lx('Email Setup...'), objectName = 'emailSetup')
		aEmailSetupButton.clicked.connect(self.emailSetupButtonClick)
		aSetupButtons.addWidget(aEmailSetupButton)

		aSetupGroupBox = QtWidgets.QGroupBox(lx('Setup'), objectName = 'setupGroup')
		aSetupGroupBox.setLayout(aSetupButtons)

		aRightZone.addWidget(aSetupGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Debug box
		aDebugButtons = QtWidgets.QVBoxLayout()
		aDebugButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aDebugButtons.setSpacing(10)

		aShowRawDeviceListButton = QtWidgets.QPushButton(lx('Raw Device List...'), objectName = 'showRawDeviceList')
		aShowRawDeviceListButton.clicked.connect(self.showRawDeviceListButtonClick)
		aDebugButtons.addWidget(aShowRawDeviceListButton)
		aShowRawTopologyButton = QtWidgets.QPushButton(lx('Raw Topology...'), objectName = 'showRawTopology')
		aShowRawTopologyButton.clicked.connect(self.showRawTopologyButtonClick)
		aDebugButtons.addWidget(aShowRawTopologyButton)
		aSetLogLevelButton = QtWidgets.QPushButton(lx('Set Log Level...'), objectName = 'setLogLevel')
		aSetLogLevelButton.clicked.connect(self.setLogLevelButtonClick)
		aDebugButtons.addWidget(aSetLogLevelButton)
		aGenDocButton = QtWidgets.QPushButton(lx('Generate API Documentation...'), objectName = 'getApiDoc')
		aGenDocButton.clicked.connect(self.getDocButtonClick)
		aDebugButtons.addWidget(aGenDocButton)

		aDebugGroupBox = QtWidgets.QGroupBox(lx('Debug'), objectName = 'debugGroup')
		aDebugGroupBox.setLayout(aDebugButtons)

		aRightZone.addWidget(aDebugGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Quit button
		aQuitButton = QtWidgets.QPushButton(lx('Quit Application'), objectName = 'quit')
		aQuitButton.clicked.connect(self.quitButtonClick)
		aQuitButton.setMinimumWidth(BUTTON_WIDTH)
		aRightZone.addWidget(aQuitButton, 1, QtCore.Qt.AlignmentFlag.AlignBottom)

		# Layout
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		aHBox.setSpacing(40)
		aHBox.addLayout(aLeftZone, 1)
		aHBox.addLayout(aMiddleZone, 1)
		aHBox.addLayout(aRightZone, 1)
		self._actionsTab.setLayout(aHBox)

		LmConfig.SetToolTips(self._actionsTab, 'actions')
		self._tabWidget.addTab(self._actionsTab, lx('Actions'))


	### Click on Wifi ON button
	def wifiOnButtonClick(self):
		self.startTask(lx('Activating Wifi...'))
		try:
			d = self._session.request('NMC.Wifi', 'set', { 'Enable': True, 'Status' : True })
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				self.displayError('NMC.Wifi:set service failed.')
			else:
				self.displayStatus(mx('Wifi activated.', 'wifiOn'))
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Wifi:set service error.')
		self.endTask()


	### Click on Wifi OFF button
	def wifiOffButtonClick(self):
		self.startTask(lx('Deactivating Wifi...'))
		try:
			d = self._session.request('NMC.Wifi', 'set', { 'Enable': False, 'Status' : False })
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				self.displayError('NMC.Wifi:set service failed.')
			else:
				self.displayStatus(mx('Wifi deactivated.', 'wifiOff'))
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Wifi:set service error.')
		self.endTask()


	### Click on guest Wifi ON button
	def guestWifiOnButtonClick(self):
		self.startTask(lx('Activating Guest Wifi...'))
		try:
			d = self._session.request('NMC.Guest', 'set', { 'Enable': True })
			if d is None:
				self.displayError('NMC.Guest:set service failed.')
			else:
				self.displayStatus(mx('Guest Wifi activated. Reactivate Scheduler if required.', 'gwifiOn'))
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Guest:set service error.')
		self.endTask()


	### Click on guest Wifi OFF button
	def guestWifiOffButtonClick(self):
		self.startTask(lx('Deactivating Guest Wifi...'))
		try:
			d = self._session.request('NMC.Guest', 'set', { 'Enable': False })
			if d is None:
				self.displayError('NMC.Guest:set service failed.')
			else:
				self.displayStatus(mx('Guest Wifi deactivated.', 'gwifiOff'))
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Guest:set service error.')
		self.endTask()


	### Click on Scheduler ON button
	def schedulerOnButtonClick(self):
		self.startTask(lx('Activating Wifi Scheduler...'))
		if self.schedulerOnOff(True):
			self.displayStatus(mx('Scheduler activated.', 'schedOn'))
		else:
			self.displayStatus(mx('Something failed while trying to activate the scheduler.', 'schedOnErr'))
		self.endTask()


	### Click on Scheduler OFF button
	def schedulerOffButtonClick(self):
		self.startTask(lx('Deactivating Wifi Scheduler...'))
		if self.schedulerOnOff(False):
			self.displayStatus(mx('Scheduler deactivated.', 'schedOff'))
		else:
			self.displayError(mx('Something failed while trying to deactivate the scheduler.', 'schedOffErr'))
		self.endTask()


	### Set Wifi Scheduler on or off, returns True if successful, False if failed
	def schedulerOnOff(self, iEnable):
		# Set PowerManagement profile
		if iEnable:
			p = [{ 'profile': 'WiFi',
				   'activate': True,
				   'type': 'Weekly',
				   'schedules': [{
                        'Day': 1,
                        'Hour': 0,
                        'Minute': 0,
                        'Second': 0,
                        'enable': True
                    }]
				}]
			d = self._session.request('PowerManagement', 'setScheduledProfiles', { 'profiles' : p })
		else:
			d = self._session.request('PowerManagement', 'setProfiles', { 'profiles' : [{'profile' : 'WiFi', 'activate' : False}] })
		if d:
			d = d.get('status')
		if d and (type(d).__name__ != 'dict'):
			d = None
		if not d:
			LmTools.Error('Error: PowerManagement method failed, trying legacy method.')
			return self.schedulerOnOff_Legacy(iEnable)

		# ID has to remain 'wl0' - it is NOT corresponding to an intf key
		aID = 'wl0'

		# Get current schedule info
		d = self._session.request('Scheduler', 'getSchedule', { 'type' : 'WLAN', 'ID' : aID })
		aErrors = LmTools.GetErrorsFromLiveboxReply(d)
		if d:
			aStatus = d.get('status')
		else:
			aStatus = False
		if aStatus:
			d = d.get('data')
			if d:
				d = d.get('scheduleInfo')
		else:
			d = None
		if d:
			aSchedule = d
		else:
			self.displayError('Scheduler:getSchedule service failed for {} interface.\n{}'.format(aID, aErrors))
			return False

		# Add schedule with proper status
		p = {}
		p['base'] = aSchedule.get('base')
		p['def'] = aSchedule.get('def')
		p['ID'] = aID
		p['schedule'] = aSchedule.get('schedule')
		p['enable'] = iEnable
		p['override'] = ''
		d = self._session.request('Scheduler', 'addSchedule', { 'type' : 'WLAN', 'info' : p })
		aErrors = LmTools.GetErrorsFromLiveboxReply(d)
		if d:
			d = d.get('status')
		if not d:
			self.displayError('Scheduler:addSchedule service failed for {} interface.\n{}'.format(aID, aErrors))
			return False
	
		return True


	### Legacy method to set Wifi Scheduler on or off, returns True if successful, False if failed
	### These calls were used by the deprecated "MaLiveBox" iOS app
	def schedulerOnOff_Legacy(self, iEnable):
		# First save network configuration
		d = self._session.request('NMC.NetworkConfig', 'launchNetworkBackup', { 'delay' : True })
		aFailed = False
		aRestore = False

		# Loop on each Wifi interface
		n = 0
		for i in LmConfig.NET_INTF:
			if i['Type'] == 'wif':
				# Get current schedule info
				d = self._session.request('Scheduler', 'getSchedule', { 'type' : 'WLAN', 'ID' : i['Key'] })
				aErrors = LmTools.GetErrorsFromLiveboxReply(d)
				if d:
					aStatus = d.get('status')
				else:
					aStatus = False
				if aStatus:
					d = d.get('data')
					if d:
						d = d.get('scheduleInfo')
				else:
					d = None
				if d:
					aSchedule = d
				else:
					self.displayError('Scheduler:getSchedule service failed for {} interface.\n{}'.format(i['Key'], aErrors))
					aFailed = True
					break

				# Add schedule with proper status
				p = {}
				p['enable'] = iEnable
				p['base'] = aSchedule.get('base')
				p['def'] = aSchedule.get('def')
				if iEnable:
					p['override'] = ''
				else:
					p['override'] = 'Enable'
				p['value'] = aSchedule.get('value')
				p['ID'] = i['Key']
				p['schedule'] = aSchedule.get('schedule')
				d = self._session.request('Scheduler', 'addSchedule', { 'type' : 'WLAN', 'info' : p })
				aErrors = LmTools.GetErrorsFromLiveboxReply(d)
				if d:
					d = d.get('status')
				if not d:
					self.displayError('Scheduler:addSchedule service failed for {} interface.\nLivebox might reboot.\n{}'.format(i['Key'], aErrors))
					aFailed = True
					if n:	# Trigger a restore (causing a Livebox reboot) if at least one succeeded previously
						aRestore = True
					break
				else:
					n += 1

		# Restore network configuration if failed and try another way
		if aFailed:
			if aRestore:
				self._session.request('NMC.NetworkConfig', 'launchNetworkRestore')		# Restore config, triggering a Livebox reboot
			aFailed = False

			for i in LmConfig.NET_INTF:
				if i['Type'] == 'wif':
					d = self._session.request('Scheduler', 'enableSchedule', { 'type' : 'WLAN', 'ID' : i['Key'], 'enable': iEnable })
					aErrors = LmTools.GetErrorsFromLiveboxReply(d)
					if d:
						d = d.get('status')
					if not d:
						self.displayError('Scheduler:enableSchedule service failed for {} interface.\n{}'.format(i['Key'], aErrors))
						aFailed = True

		if aFailed:
			return False
		return True


	### Click on Global Wifi Status button
	def wifiGlobalStatusButtonClick(self):
		self.startTask(lx('Getting Wifi Global Status...'))

		# Getting Livebox status
		aLiveboxStatus = self.getLiveboxWifiStatus()

		# Getting Repeater statuses
		aGlobalStatus = self.getRepeatersWifiStatus()
		aGlobalStatus.insert(0, aLiveboxStatus)

		self.endTask()

		aStatusDialog = WifiGlobalStatusDialog(self, aGlobalStatus, self._liveboxModel)
		aStatusDialog.exec()


	### Click on the Backup & Restore button
	def backupRestoreButtonClick(self):
		aBackupRestoreDialog = BackupRestoreSetupDialog(self)
		aBackupRestoreDialog.exec()


	### Click on Reboot Livebox button
	def rebootLiveboxButtonClick(self):
		if self.askQuestion(mx('Are you sure you want to reboot the Livebox?', 'lbReboot')):
			self.startTask(lx('Rebooting Livebox...'))
			try:
				r = self._session.request('NMC', 'reboot', { 'reason': 'GUI_Reboot' })
				if r is None:
					self.displayError('NMC:reboot service failed.')
				else:
					self.endTask()
					self.displayStatus(mx('Application will now quit.', 'appQuit'))
					self.close()
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('NMC:reboot service error.')
			self.endTask()


	### Click on Reboot History button
	def rebootHistoryButtonClick(self):
		self.startTask(lx('Getting Reboot History...'))

		try:
			d = self._session.request('NMC.Reboot.Reboot', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')

		self.endTask()

		if d is None:
			self.displayError('NMC.Reboot.Reboot:get service error.')
			return

		aHistoryDialog = RebootHistoryDialog('Livebox', self)
		aHistoryDialog.loadHistory(d)
		aHistoryDialog.exec()


	### Click on Firewall Level button
	def firewallLevelButtonClick(self):
		# Get current IPv4 firewall level
		try:
			aReply = self._session.request('Firewall', 'getFirewallLevel')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall:getFirewallLevel query error.')
			return

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return
			aFirewallIPv4Level = aReply['status']
		else:
			self.displayError('Firewall:getFirewallLevel query failed.')
			return

		# Get current IPv6 firewall level
		try:
			aReply = self._session.request('Firewall', 'getFirewallIPv6Level')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall:getFirewallIPv6Level query error.')
			return

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return
			aFirewallIPv6Level = aReply['status']
		else:
			self.displayError('Firewall:getFirewallIPv6Level query failed.')
			return

		aFirewallLevelDialog = FirewallLevelDialog(aFirewallIPv4Level, aFirewallIPv6Level, self)
		if aFirewallLevelDialog.exec():
			self.startTask(lx('Set Firewall Levels...'))

			# Set new IPv4 firewall level if changed
			aNewFirewallIPv4Level = aFirewallLevelDialog.getIPv4Level()
			if aNewFirewallIPv4Level != aFirewallIPv4Level:
				try:
					aReply = self._session.request('Firewall', 'setFirewallLevel', { 'level': aNewFirewallIPv4Level })
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Firewall:setFirewallLevel query error.')
				else:
					if (aReply is not None) and ('status' in aReply):
						aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
						if len(aErrors):
							self.displayError(aErrors)
						elif not aReply['status']:
							self.displayError('Firewall:setFirewallLevel query failed.')
					else:
						self.displayError('Firewall:setFirewallLevel query failed.')

			# Set new IPv6 firewall level if changed
			aNewFirewallIPv6Level = aFirewallLevelDialog.getIPv6Level()
			if aNewFirewallIPv6Level != aFirewallIPv6Level:
				try:
					aReply = self._session.request('Firewall', 'setFirewallIPv6Level', { 'level': aNewFirewallIPv6Level })
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Firewall:setFirewallIPv6Level query error.')
				else:
					if (aReply is not None) and ('status' in aReply):
						aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
						if len(aErrors):
							self.displayError(aErrors)
						elif not aReply['status']:
							self.displayError('Firewall:setFirewallIPv6Level query failed.')
					else:
						self.displayError('Firewall:setFirewallIPv6Level query failed.')

			self.endTask()


	### Click on Ping Response button
	def pingResponseButtonClick(self):
		# ###Info### - works also for other sourceInterfaces such as veip0, eth0, voip, etc, but usefulness?

		# Get current ping reponses
		try:
			aReply = self._session.request('Firewall', 'getRespondToPing', { 'sourceInterface': 'data' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall:getRespondToPing query error.')
			return

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return

			aReply = aReply['status']
			aIPv4Ping = aReply.get('enableIPv4')
			aIPv6Ping = aReply.get('enableIPv6')
			if (aIPv4Ping is None) or (aIPv6Ping is None):
				self.displayError('Firewall:getRespondToPing query failed.')
				return
		else:
			self.displayError('Firewall:getRespondToPing query failed.')
			return

		aPingResponseDialog = PingResponseDialog(aIPv4Ping, aIPv6Ping, self)
		if aPingResponseDialog.exec():
			# Set new ping responses level if changed
			aNewIPv4Ping = aPingResponseDialog.getIPv4()
			aNewIPv6Ping = aPingResponseDialog.getIPv6()
			if (aNewIPv4Ping != aIPv4Ping) or (aNewIPv6Ping != aIPv6Ping):
				self.startTask(lx('Set Ping Responses...'))

				p = {}
				p['enableIPv4'] = aNewIPv4Ping
				p['enableIPv6'] = aNewIPv6Ping
				try:
					aReply = self._session.request('Firewall', 'setRespondToPing', { 'sourceInterface': 'data', 'service_enable': p })
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Firewall:setRespondToPing query error.')
				else:
					if (aReply is not None) and ('status' in aReply):
						aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
						if len(aErrors):
							self.displayError(aErrors)
						elif not aReply['status']:
							self.displayError('Firewall:setRespondToPing query failed.')
					else:
						self.displayError('Firewall:setRespondToPing query failed.')

				self.endTask()


	### Click on DynDNS button
	def dynDNSButtonClick(self):
		aDynDNSSetupDialog = DynDNSSetupDialog(self)
		aDynDNSSetupDialog.exec()


	### Click on DMZ button
	def dmzButtonClick(self):
		aDmzSetupDialog = DmzSetupDialog(self)
		aDmzSetupDialog.exec()


	### Open Source project web button
	def openSourceButtonClick(self, iEvent):
		webbrowser.open_new_tab(__url__)


	### Click on preferences button
	def prefsButtonClick(self):
		aPrefsDialog = PrefsDialog(self)
		if aPrefsDialog.exec():
			LmConf.assignProfile()
			LmConf.save()
			LmConf.apply()
			SetApplicationStyle()
			self.resetUI()


	### Change the current profile in use
	def changeProfileButtonClick(self):
		r = LmConf.askProfile(None)
		if r == 1:
			LmConf.assignProfile()
			self.resetUI()
		elif r == 2:
			self.prefsButtonClick()


	### Click on email setup button
	def emailSetupButtonClick(self):
		aEmailSetupDialog = EmailSetupDialog(self)
		if aEmailSetupDialog.exec():
			LmConf.setEmailSetup(aEmailSetupDialog.getSetup())
			LmConf.save()


	### Click on show raw device list button
	def showRawDeviceListButtonClick(self):
		self.displayInfos(lx('Raw Device List'), json.dumps(self._liveboxDevices, indent = 2))


	### Click on show raw topology button
	def showRawTopologyButtonClick(self):
		self.displayInfos(lx('Raw Topology'), json.dumps(self._liveboxTopology, indent = 2))


	### Click on set log level button
	def setLogLevelButtonClick(self):
		aLevels = ['0', '1', '2']
		aLevel, aOK = QtWidgets.QInputDialog.getItem(None, lx('Log level selection'),
													 lx('Please select a log level:'),
													 aLevels, LmConf.LogLevel, False)
		if aOK:
			LmConf.setLogLevel(int(aLevel))


	### Click on generate API documentation button
	def getDocButtonClick(self):
		# Check Ctlr key to switch to filtering mode
		aModifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
		aFilterValues = aModifiers == QtCore.Qt.KeyboardModifier.ControlModifier

		aFolder = QtWidgets.QFileDialog.getExistingDirectory(self, lx('Select Export Folder'))
		if len(aFolder):
			aFolder = QtCore.QDir.toNativeSeparators(aFolder)

			# Check Ctlr key again to possibly switch to filtering mode
			if not aFilterValues:
				aModifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
				aFilterValues = aModifiers == QtCore.Qt.KeyboardModifier.ControlModifier

			self.startTask(lx('Generating API document files...'))
			g = LmGenApiDocumentation.LmGenApiDoc(self, aFolder, aFilterValues)
			g.genModuleFiles()
			g.genFullFile()
			g.genProcessListFile()
			self.endTask()


	### Click on Quit Application button
	def quitButtonClick(self):
		self.close()



# ############# Display reboot history dialog #############
class RebootHistoryDialog(QtWidgets.QDialog):
	def __init__(self, iName, iParent = None):
		super(RebootHistoryDialog, self).__init__(iParent)
		self.resize(550, 56 + LmConfig.DialogHeight(10))

		self._historyTable = QtWidgets.QTableWidget(objectName = 'historyTable')
		self._historyTable.setColumnCount(4)
		self._historyTable.setHorizontalHeaderLabels((lrx('Boot Date'), lrx('Boot Reason'), lrx('Shutdown Date'), lrx('Shutdown Reason')))
		aHeader = self._historyTable.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, 'reboot_BootDate', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, 'reboot_BootReason', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, 'reboot_ShutdownDate', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, 'reboot_ShutdownReason', QtCore.Qt.ItemDataRole.UserRole)
		self._historyTable.setColumnWidth(0, 125)
		self._historyTable.setColumnWidth(1, 225)
		self._historyTable.setColumnWidth(2, 125)
		self._historyTable.setColumnWidth(3, 225)
		self._historyTable.verticalHeader().hide()
		self._historyTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._historyTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._historyTable)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(lrx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._historyTable, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'rhistory')

		self.setWindowTitle(lrx('{} Reboot History').format(iName))
		self.setModal(True)
		self.show()


	def loadHistory(self, iHistory):
		i = 0

		for aKey in iHistory:
			d = iHistory[aKey]
			self._historyTable.insertRow(i)
			self._historyTable.setItem(i, 0, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('BootDate'))))
			self._historyTable.setItem(i, 1, QtWidgets.QTableWidgetItem(d.get('BootReason', lrx('Unknown'))))
			self._historyTable.setItem(i, 2, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('ShutdownDate'))))
			self._historyTable.setItem(i, 3, QtWidgets.QTableWidgetItem(d.get('ShutdownReason', lrx('Unknown'))))
			i += 1



# ############# Display Wifi global status dialog #############
class WifiGlobalStatusDialog(QtWidgets.QDialog):
	def __init__(self, iParent, iStatus, iLiveboxModel):
		super(WifiGlobalStatusDialog, self).__init__(iParent)

		self._status = iStatus
		self._statusTable = QtWidgets.QTableWidget(objectName = 'statusTable')
		self._statusTable.setColumnCount(1 + len(iStatus))
		aHeaders = []
		aHeaders.append(lwx('Interfaces'))
		for s in self._status:
			aHeaders.append(s[WifiKey.AccessPoint])
		self._statusTable.setHorizontalHeaderLabels((*aHeaders,))
		aTableHeader = self._statusTable.horizontalHeader()
		aTableHeader.setSectionsMovable(False)
		aTableHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aTableHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._statusTable.setColumnWidth(0, 200)
		i = 1
		while i <= len(self._status):
			self._statusTable.setColumnWidth(i, 125)
			i += 1
		self._statusTable.verticalHeader().hide()
		self._statusTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._statusTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._statusTable)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(lwx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._statusTable, 0)
		aVBox.addLayout(aHBox, 1)

		i = self.loadStatus(iLiveboxModel)
		self.resize(550, 56 + LmConfig.DialogHeight(i))

		LmConfig.SetToolTips(self, 'wglobal')

		self.setWindowTitle(lwx('Wifi Global Status'))
		self.setModal(True)
		self.show()


	def loadStatus(self, iLiveboxModel):
		i = 0
		i = self.addStatusLine(lwx('{} Enabled').format('Wifi'), WifiKey.Enable, i)
		i = self.addStatusLine(lwx('{} Active').format('Wifi'), WifiKey.Status, i)
		i = self.addStatusLine(lwx('Wifi Scheduler'), WifiKey.Scheduler, i)
		i = self.addStatusLine(lwx('{} Enabled').format('Wifi 2.4GHz'), WifiKey.Wifi2Enable, i)
		i = self.addStatusLine(lwx('{} Active').format('Wifi 2.4GHz'), WifiKey.Wifi2Status, i)
		i = self.addStatusLine(lwx('{} VAP').format('Wifi 2.4GHz'), WifiKey.Wifi2VAP, i)
		i = self.addStatusLine(lwx('{} Enabled').format('Wifi 5GHz'), WifiKey.Wifi5Enable, i)
		i = self.addStatusLine(lwx('{} Active').format('Wifi 5GHz'), WifiKey.Wifi5Status, i)
		i = self.addStatusLine(lwx('{} VAP').format('Wifi 5GHz'), WifiKey.Wifi5VAP, i)
		if iLiveboxModel >= 6:
			i = self.addStatusLine(lwx('{} Enabled').format('Wifi 6GHz'), WifiKey.Wifi6Enable, i)
			i = self.addStatusLine(lwx('{} Active').format('Wifi 6GHz'), WifiKey.Wifi6Status, i)
			i = self.addStatusLine(lwx('{} VAP').format('Wifi 6GHz'), WifiKey.Wifi6VAP, i)
		i = self.addStatusLine(lwx('{} VAP').format(lwx('Guest 2.4GHz')), WifiKey.Guest2VAP, i)
		i = self.addStatusLine(lwx('{} VAP').format(lwx('Guest 5GHz')), WifiKey.Guest5VAP, i)
		return i


	def addStatusLine(self, iTitle, iKey, iIndex):
		self._statusTable.insertRow(iIndex)

		self._statusTable.setItem(iIndex, 0, QtWidgets.QTableWidgetItem(iTitle))

		i = 1
		for s in self._status:
			aStatus = s.get(iKey)
			if aStatus == WifiStatus.Enable:
				aIconItem = QtWidgets.QLabel()
				aIconItem.setPixmap(LmIcon.TickPixmap)
				aIconItem.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setCellWidget(iIndex, i, aIconItem)
			elif aStatus == WifiStatus.Disable:
				aIconItem = QtWidgets.QLabel()
				aIconItem.setPixmap(LmIcon.CrossPixmap)
				aIconItem.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setCellWidget(iIndex, i, aIconItem)
			elif aStatus == WifiStatus.Error:
				aItem = QtWidgets.QTableWidgetItem(lwx('Error'))
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			elif aStatus == WifiStatus.Inactive:
				aItem = QtWidgets.QTableWidgetItem(lwx('Inactive'))
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			elif aStatus == WifiStatus.Unsigned:
				aItem = QtWidgets.QTableWidgetItem(lwx('Not signed'))
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			i += 1

		return iIndex + 1



# ############# Backup & Restore Setup dialog #############
class BackupRestoreSetupDialog(QtWidgets.QDialog):
	def __init__(self, iParent = None):
		super(BackupRestoreSetupDialog, self).__init__(iParent)
		self.resize(400, 300)

		self._app = iParent

		# Backup info box
		aAutoBackupEnabledLabel = QtWidgets.QLabel(lbx('Auto backup enabled:'), objectName = 'autoBackEnabledLabel')
		self._autoBackupEnabled = QtWidgets.QLabel(objectName = 'autoBackEnabled')

		aStatusLabel = QtWidgets.QLabel(lbx('Status:'), objectName = 'statusLabel')
		self._status = QtWidgets.QLabel(objectName = 'status')

		aLastBackupLabel = QtWidgets.QLabel(lbx('Last Backup:'), objectName = 'lastBackupLabel')
		self._lastBackup = QtWidgets.QLabel(objectName = 'lastBackup')

		aInfoGrid = QtWidgets.QGridLayout()
		aInfoGrid.setSpacing(5)
		aInfoGrid.addWidget(aAutoBackupEnabledLabel, 0, 0)
		aInfoGrid.addWidget(self._autoBackupEnabled, 0, 1)
		aInfoGrid.addWidget(aStatusLabel, 1, 0)
		aInfoGrid.addWidget(self._status, 1, 1)
		aInfoGrid.addWidget(aLastBackupLabel, 2, 0)
		aInfoGrid.addWidget(self._lastBackup, 2, 1)

		aRefreshButton = QtWidgets.QPushButton(lbx('Refresh'), objectName = 'refresh')
		aRefreshButton.clicked.connect(self.refreshStatus)

		aEnableAutoBackupButton = QtWidgets.QPushButton(lbx('Enable Auto Backup'), objectName = 'enaAutoBack')
		aEnableAutoBackupButton.clicked.connect(self.enableAutoBackup)

		aDisableAutoBackupButton = QtWidgets.QPushButton(lbx('Disable Auto Backup'), objectName = 'disAutoBack')
		aDisableAutoBackupButton.clicked.connect(self.disableAutoBackup)

		aForceBackupButton = QtWidgets.QPushButton(lbx('Force Backup'), objectName = 'forceBackup')
		aForceBackupButton.clicked.connect(self.forceBackup)

		aForceRestoreButton = QtWidgets.QPushButton(lbx('Force Restore'), objectName = 'forceRestore')
		aForceRestoreButton.clicked.connect(self.forceRestore)

		aButtonGrid = QtWidgets.QGridLayout()
		aButtonGrid.setSpacing(10)
		aButtonGrid.addWidget(aRefreshButton, 0, 0)
		aButtonGrid.addWidget(aEnableAutoBackupButton, 1, 0)
		aButtonGrid.addWidget(aDisableAutoBackupButton, 2, 0)
		aButtonGrid.addWidget(aForceBackupButton, 3, 0)
		aButtonGrid.addWidget(aForceRestoreButton, 4, 0)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(lbx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(40)
		aVBox.addLayout(aInfoGrid, 0)
		aVBox.addLayout(aButtonGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'backrest')

		self.refreshStatus()

		self.setWindowTitle(lbx('Backup and Restore Setup'))
		self.setModal(True)
		self.show()


	def refreshStatus(self):
		try:
			d = self._app._session.request('NMC.NetworkConfig', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None or not len(d):
			self._app.displayError(mx('Cannot load backup and restore status.', 'backRestSvcErr'))
			return

		aEnabled = d.get('Enable', False)
		if aEnabled:
			self._autoBackupEnabled.setPixmap(LmIcon.TickPixmap)
		else:
			self._autoBackupEnabled.setPixmap(LmIcon.CrossPixmap)

		aStatus = d.get('Status', '-')
		self._status.setText(aStatus)

		aLastBackup = d.get('ConfigDate')
		if aLastBackup:
			self._lastBackup.setText(LmTools.FmtLiveboxTimestamp(aLastBackup))
		else:
			self._lastBackup.setText('-')


	def enableAutoBackup(self):
		try:
			d = self._app._session.request('NMC.NetworkConfig', 'enableNetworkBR', { 'state': True })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if 'status' in d:
			self.refreshStatus()
		else:
			self._app.displayError(mx('Cannot enable auto backup.', 'backEnableSvcErr'))


	def disableAutoBackup(self):
		try:
			d = self._app._session.request('NMC.NetworkConfig', 'enableNetworkBR', { 'state': False })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if 'status' in d:
			self.refreshStatus()
		else:
			self._app.displayError(mx('Cannot disable auto backup.', 'backDisableSvcErr'))


	def forceBackup(self):
		try:
			d = self._app._session.request('NMC.NetworkConfig', 'launchNetworkBackup', { 'delay' : True })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if 'status' in d:
			self.refreshStatus()
		else:
			self._app.displayError(mx('Backup request failed.', 'backupSvcErr'))


	def forceRestore(self):
		try:
			d = self._app._session.request('NMC.NetworkConfig', 'launchNetworkRestore')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if 'status' in d:
			self._app.displayStatus(mx('Restore requested. Livebox will restart.', 'restoreSvcOk'))
		else:
			self._app.displayError(mx('Restore request failed.', 'restoreSvcErr'))



# ############# Firewall Level dialog #############
class FirewallLevelDialog(QtWidgets.QDialog):
	def __init__(self, iIPv4Level, iIPv6Level, iParent = None):
		super(FirewallLevelDialog, self).__init__(iParent)
		self.setMinimumWidth(230)
		self.resize(300, 150)

		aIpV4LevelLabel = QtWidgets.QLabel(lfx('IPv4 Firewall Level'), objectName = 'ipV4Label')
		self._ipV4LevelCombo = QtWidgets.QComboBox(objectName = 'ipV4Combo')
		for l in FIREWALL_LEVELS:
			self._ipV4LevelCombo.addItem(lfx(l), userData = l)
		self._ipV4LevelCombo.setCurrentIndex(FIREWALL_LEVELS.index(iIPv4Level))

		aIpV6LevelLabel = QtWidgets.QLabel(lfx('IPv6 Firewall Level'), objectName = 'ipV6Label')
		self._ipV6LevelCombo = QtWidgets.QComboBox(objectName = 'ipV6Combo')
		for l in FIREWALL_LEVELS:
			self._ipV6LevelCombo.addItem(lfx(l), userData = l)
		self._ipV6LevelCombo.setCurrentIndex(FIREWALL_LEVELS.index(iIPv6Level))

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(aIpV4LevelLabel, 0, 0)
		aGrid.addWidget(self._ipV4LevelCombo, 0, 1)
		aGrid.addWidget(aIpV6LevelLabel, 1, 0)
		aGrid.addWidget(self._ipV6LevelCombo, 1, 1)
		aGrid.setColumnStretch(0, 0)
		aGrid.setColumnStretch(1, 1)

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

		LmConfig.SetToolTips(self, 'fwlevel')

		self.setWindowTitle(lfx('Firewall Levels'))

		self.setModal(True)
		self.show()


	def getIPv4Level(self):
		return self._ipV4LevelCombo.currentData()


	def getIPv6Level(self):
		return self._ipV6LevelCombo.currentData()



# ############# Ping Response dialog #############
class PingResponseDialog(QtWidgets.QDialog):
	def __init__(self, iIPv4, iIPv6, iParent = None):
		super(PingResponseDialog, self).__init__(iParent)
		self.setMinimumWidth(230)
		self.resize(230, 150)

		self._ipV4CheckBox = QtWidgets.QCheckBox(lpx('Respond to IPv4 ping'), objectName = 'ipV4Checkbox')
		if iIPv4:
				self._ipV4CheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
				self._ipV4CheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		self._ipV6CheckBox = QtWidgets.QCheckBox(lpx('Respond to IPv6 ping'), objectName = 'ipV6Checkbox')
		if iIPv6:
				self._ipV6CheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
				self._ipV6CheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

		aVCBox = QtWidgets.QVBoxLayout()
		aVCBox.setSpacing(10)
		aVCBox.addWidget(self._ipV4CheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aVCBox.addWidget(self._ipV6CheckBox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

		self._okButton = QtWidgets.QPushButton(lpx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lpx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aVCBox, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'pingr')

		self.setWindowTitle(lpx('Ping Responses'))

		self.setModal(True)
		self.show()


	def getIPv4(self):
		return self._ipV4CheckBox.checkState() == QtCore.Qt.CheckState.Checked


	def getIPv6(self):
		return self._ipV6CheckBox.checkState() == QtCore.Qt.CheckState.Checked



# ################################ DynDNS setup dialog ################################
class DynDNSSetupDialog(QtWidgets.QDialog):
	### Constructor
	def __init__(self, iParent = None):
		super(DynDNSSetupDialog, self).__init__(iParent)
		self.resize(720, 400)

		self._app = iParent
		self._hostSelection = -1
		self._init = True
		self._showPasswords = False

		# Host box
		aHostLayout = QtWidgets.QHBoxLayout()
		aHostLayout.setSpacing(30)

		aHostListLayout = QtWidgets.QVBoxLayout()
		aHostListLayout.setSpacing(5)

		# Host list columns
		self._hostList = QtWidgets.QTableWidget(objectName = 'hostList')
		self._hostList.setColumnCount(HostCol.Count)

		# Set columns
		self._hostList.setHorizontalHeaderLabels((ldx('Service'), ldx('Host Name'), ldx('User Email'), ldx('Password'), ldx('Last Update'), ldx('Status')))

		aHeader = self._hostList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
		aHeader.setSectionResizeMode(HostCol.HostName, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(HostCol.UserName, QtWidgets.QHeaderView.ResizeMode.Stretch)

		# Assign tags for tooltips
		aModel = aHeader.model()
		aModel.setHeaderData(HostCol.Service, QtCore.Qt.Orientation.Horizontal, 'hlist_Service', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(HostCol.HostName, QtCore.Qt.Orientation.Horizontal, 'hlist_HostName', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(HostCol.UserName, QtCore.Qt.Orientation.Horizontal, 'hlist_UserName', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(HostCol.Password, QtCore.Qt.Orientation.Horizontal, 'hlist_Password', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(HostCol.LastUpdate, QtCore.Qt.Orientation.Horizontal, 'hlist_LastUpdate', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(HostCol.Status, QtCore.Qt.Orientation.Horizontal, 'hlist_Status', QtCore.Qt.ItemDataRole.UserRole)

		self._hostList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._hostList.setColumnWidth(HostCol.Service, 90)
		self._hostList.setColumnWidth(HostCol.HostName, 80)
		self._hostList.setColumnWidth(HostCol.UserName, 80)
		self._hostList.setColumnWidth(HostCol.Password, 130)
		self._hostList.setColumnWidth(HostCol.LastUpdate, 120)
		self._hostList.setColumnWidth(HostCol.Status, 120)
		self._hostList.verticalHeader().hide()
		self._hostList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._hostList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._hostList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._hostList.setMinimumWidth(880)
		self._hostList.itemSelectionChanged.connect(self.hostListClick)
		LmConfig.SetTableStyle(self._hostList)
		self._hostList.setMinimumHeight(LmConfig.TableHeight(4))

		aHostListLayout.addWidget(self._hostList, 1)

		aHostButtonBox = QtWidgets.QHBoxLayout()
		aHostButtonBox.setSpacing(5)

		aRefreshButton = QtWidgets.QPushButton(ldx('Refresh'), objectName = 'refresh')
		aRefreshButton.clicked.connect(self.refreshButtonClick)
		aHostButtonBox.addWidget(aRefreshButton)
		self._showPasswordButton = QtWidgets.QPushButton(ldx('Show Passwords'), objectName = 'showPassword')
		self._showPasswordButton.clicked.connect(self.showPasswordButtonClick)
		aHostButtonBox.addWidget(self._showPasswordButton)
		self._delHostButton = QtWidgets.QPushButton(ldx('Delete'), objectName = 'delHost')
		self._delHostButton.clicked.connect(self.delHostButtonClick)
		aHostButtonBox.addWidget(self._delHostButton)
		aHostListLayout.addLayout(aHostButtonBox, 0)
		aHostLayout.addLayout(aHostListLayout, 0)

		aHostGroupBox = QtWidgets.QGroupBox(ldx('Hosts'), objectName = 'hostGroup')
		aHostGroupBox.setLayout(aHostLayout)

		# Add host box
		aServiceLabel = QtWidgets.QLabel(ldx('Service'), objectName = 'serviceLabel')
		self._serviceCombo = QtWidgets.QComboBox(objectName = 'serviceCombo')
		self.loadServiceCombo()
		aHostNameLabel = QtWidgets.QLabel(ldx('Host Name'), objectName = 'hostNameLabel')
		self._hostName = QtWidgets.QLineEdit(objectName = 'hostNameEdit')
		self._hostName.textChanged.connect(self.hostTyped)
		aUserNameLabel = QtWidgets.QLabel(ldx('User Email'), objectName = 'userNameLabel')
		self._userName = QtWidgets.QLineEdit(objectName = 'userNameEdit')
		self._userName.textChanged.connect(self.hostTyped)
		aPasswordLabel = QtWidgets.QLabel(ldx('Password'), objectName = 'passwordLabel')
		self._password = QtWidgets.QLineEdit(objectName = 'passwordEdit')
		self._password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
		self._password.textChanged.connect(self.hostTyped)
		self._addHostButton = QtWidgets.QPushButton(ldx('Add'), objectName = 'addHost')
		self._addHostButton.clicked.connect(self.addHostButtonClick)
		self._addHostButton.setDisabled(True)

		aHostEditGrid = QtWidgets.QGridLayout()
		aHostEditGrid.setSpacing(10)

		aHostEditGrid.addWidget(aServiceLabel, 0, 0)
		aHostEditGrid.addWidget(self._serviceCombo, 0, 1)
		aHostEditGrid.addWidget(aHostNameLabel, 0, 2)
		aHostEditGrid.addWidget(self._hostName, 0, 3)
		aHostEditGrid.addWidget(aUserNameLabel, 1, 0)
		aHostEditGrid.addWidget(self._userName, 1, 1)
		aHostEditGrid.addWidget(aPasswordLabel, 1, 2)
		aHostEditGrid.addWidget(self._password, 1, 3)
		aHostEditGrid.addWidget(self._addHostButton, 0, 4, 2, 2)

		aHostEditGroupBox = QtWidgets.QGroupBox(ldx('Add Host'), objectName = 'addHostGroup')
		aHostEditGroupBox.setLayout(aHostEditGrid)

		# Button bar
		self._disableButton = QtWidgets.QPushButton(self.getDisableButtonTitle(), objectName = 'disableAll')
		self._disableButton.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 3px; padding-bottom: 3px;')
		self._disableButton.clicked.connect(self.disableButtonClick)
		aOkButton = QtWidgets.QPushButton(ldx('OK'), objectName = 'ok')
		aOkButton.clicked.connect(self.accept)
		aOkButton.setDefault(True)
		aButtonBar = QtWidgets.QHBoxLayout()
		aButtonBar.setSpacing(10)
		aButtonBar.addWidget(self._disableButton, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aButtonBar.addWidget(aOkButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		# Final layout
		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(20)
		aVBox.addWidget(aHostGroupBox, 1)
		aVBox.addWidget(aHostEditGroupBox, 0)
		aVBox.addLayout(aButtonBar, 0)

		self._hostName.setFocus()

		LmConfig.SetToolTips(self, 'dyndns')

		self.setWindowTitle(ldx('DynDNS'))
		self.setModal(True)
		self.loadHosts()
		self.show()

		self._init = False


	### Load host list
	def loadHosts(self):
		self._app.startTask(ldx('Loading DynDNS hosts...'))

		try:
			d = self._app._session.request('DynDNS', 'getHosts')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			self._app.displayError(mx('Cannot load DynDNS host list.', 'dynDnsLoadErr'))
			return

		i = 0
		for h in d:
			self._hostList.insertRow(i)
			self._hostList.setItem(i, HostCol.Service, QtWidgets.QTableWidgetItem(h.get('service', '')))
			self._hostList.setItem(i, HostCol.HostName, QtWidgets.QTableWidgetItem(h.get('hostname', '')))
			self._hostList.setItem(i, HostCol.UserName, QtWidgets.QTableWidgetItem(h.get('username', '')))
			if self._showPasswords:
				self._hostList.setItem(i, HostCol.Password, QtWidgets.QTableWidgetItem(h.get('password', '')))
			else:
				self._hostList.setItem(i, HostCol.Password, QtWidgets.QTableWidgetItem('******'))
			self._hostList.setItem(i, HostCol.LastUpdate, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(h.get('last_update'))))
			self._hostList.setItem(i, HostCol.Status, QtWidgets.QTableWidgetItem(h.get('status', '')))

			i += 1

		self.hostListClick()
		self._app.endTask()


	### Click on host list item
	def hostListClick(self):
		aNewSelection = self._hostList.currentRow()

		# Check if selection really changed
		if not self._init and self._hostSelection == aNewSelection:
			return
		self._hostSelection = aNewSelection

		self._delHostButton.setDisabled(aNewSelection < 0)


	### Load service combo box
	def loadServiceCombo(self):
		try:
			d = self._app._session.request('DynDNS', 'getServices')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None or not len(d):
			self._app.displayError(mx('Cannot load DynDNS services.', 'dynDnsSvcErr'))
			return

		for s in d:
			self._serviceCombo.addItem(s)


	### Text changed in host edit box field
	def hostTyped(self, iText):
		h = self._hostName.text()
		u = self._userName.text()
		p = self._password.text()
		self._addHostButton.setDisabled(not len(h) or not len(u) or not len(p))


	### Click on refresh button
	def refreshButtonClick(self):
		self._hostList.clearContents()
		self._hostList.setRowCount(0)
		self._hostSelection = -1
		self._init = True
		self.loadHosts()
		self._init = False


	### Click on show password button
	def showPasswordButtonClick(self):
		if self._showPasswords:
			self._showPasswordButton.setText(ldx('Show Passwords'))
			self._showPasswords = False
		else:
			self._showPasswordButton.setText(ldx('Hide Passwords'))
			self._showPasswords = True
		self.refreshButtonClick()


	### Click on delete host button
	def delHostButtonClick(self):
		i = self._hostSelection
		if i < 0:
			return

		# Delete the host entry
		aHostName = self._hostList.item(i, HostCol.HostName).text()
		try:
			d = self._app._session.request('DynDNS', 'delHost', { 'hostname': aHostName })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None or not d:
			self._app.displayError(mx('Cannot delete DynDNS host.', 'dynDnsDelErr'))
			return

		# Delete the list line
		self._hostSelection = -1
		self._init = True
		self._hostList.removeRow(i)
		self._init = False

		# Update selection
		self._hostSelection = self._hostList.currentRow()


	### Click on add host button
	def addHostButtonClick(self):
		# Hostname has to be unique
		aHostName = self._hostName.text()
		if not len(aHostName):
			return
		i = 0
		n = self._hostList.rowCount()
		while (i < n):
			if self._hostList.item(i, HostCol.HostName).text() == aHostName:
				self._app.displayError(mx('Host name {} is already used.', 'dynDnsHostName').format(aHostName))
				return
			i += 1

		# Set parameters
		h = {}
		h['service'] = self._serviceCombo.currentText()
		h['username'] = self._userName.text()
		h['hostname'] = aHostName
		h['password'] = self._password.text()

		# Call Livebox API
		try:
			d = self._app._session.request('DynDNS', 'addHost', h)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self._app.displayError('DynDNS:addHost query error.')
			return

		if (d is not None) and ('status' in d):
			aErrors = LmTools.GetErrorsFromLiveboxReply(d)
			if len(aErrors):
				self._app.displayError(aErrors)
				return
			self.refreshButtonClick()
			self._userName.setText('')
			self._hostName.setText('')
			self._password.setText('')
		else:
			self._app.displayError('DynDNS:addHost query failed.')


	### Get global enable status
	def getGlobalEnableStatus(self):
		try:
			d = self._app._session.request('DynDNS', 'getGlobalEnable')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.Error(mx('Cannot get DynDNS global enable status.', 'dynDnsEnableErr'))
			return False
		return d


	### Click on enable/disable button
	def disableButtonClick(self):
		try:
			d = self._app._session.request('DynDNS', 'setGlobalEnable', { 'enable': not self.getGlobalEnableStatus() })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None or not d:
			LmTools.Error('Cannot set DynDNS global enable status.')

		self._disableButton.setText(self.getDisableButtonTitle())
		self.refreshButtonClick()


	### get disable all button title
	def getDisableButtonTitle(self):
		if self.getGlobalEnableStatus():
			return ldx('Disable All')
		else:
			return ldx('Enable All')



# ################################ DMZ setup dialog ################################
class DmzSetupDialog(QtWidgets.QDialog):
	### Constructor
	def __init__(self, iParent = None):
		super(DmzSetupDialog, self).__init__(iParent)
		self.resize(720, 400)

		self._app = iParent
		self._dmzSelection = -1
		self._init = True
		self._ignoreSignal = False

		# DMZ box
		aDmzLayout = QtWidgets.QHBoxLayout()
		aDmzLayout.setSpacing(30)

		aDmzListLayout = QtWidgets.QVBoxLayout()
		aDmzListLayout.setSpacing(5)

		# DMZ list columns
		self._dmzList = QtWidgets.QTableWidget(objectName = 'dmzList')
		self._dmzList.setColumnCount(DmzCol.Count)

		# Set columns
		self._dmzList.setHorizontalHeaderLabels((lzx('ID'), lzx('IP'), lzx('Device'), lzx('External IPs')))

		aHeader = self._dmzList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
		aHeader.setSectionResizeMode(DmzCol.Device, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(DmzCol.ExtIPs, QtWidgets.QHeaderView.ResizeMode.Stretch)

		# Assign tags for tooltips
		aModel = aHeader.model()
		aModel.setHeaderData(DmzCol.ID, QtCore.Qt.Orientation.Horizontal, 'zlist_ID', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DmzCol.IP, QtCore.Qt.Orientation.Horizontal, 'zlist_IP', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DmzCol.Device, QtCore.Qt.Orientation.Horizontal, 'zlist_Device', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DmzCol.ExtIPs, QtCore.Qt.Orientation.Horizontal, 'zlist_ExtIPs', QtCore.Qt.ItemDataRole.UserRole)

		self._dmzList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._dmzList.setColumnWidth(DmzCol.ID, 100)
		self._dmzList.setColumnWidth(DmzCol.IP, 100)
		self._dmzList.setColumnWidth(DmzCol.Device, 150)
		self._dmzList.setColumnWidth(DmzCol.ExtIPs, 150)
		self._dmzList.verticalHeader().hide()
		self._dmzList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._dmzList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._dmzList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._dmzList.setMinimumWidth(680)
		self._dmzList.itemSelectionChanged.connect(self.dmzListClick)
		LmConfig.SetTableStyle(self._dmzList)
		self._dmzList.setMinimumHeight(LmConfig.TableHeight(4))

		aDmzListLayout.addWidget(self._dmzList, 1)

		aDmzButtonBox = QtWidgets.QHBoxLayout()
		aDmzButtonBox.setSpacing(5)

		aRefreshButton = QtWidgets.QPushButton(lzx('Refresh'), objectName = 'refresh')
		aRefreshButton.clicked.connect(self.refreshButtonClick)
		aDmzButtonBox.addWidget(aRefreshButton)
		self._delDmzButton = QtWidgets.QPushButton(lzx('Delete'), objectName = 'delDmz')
		self._delDmzButton.clicked.connect(self.delDmzButtonClick)
		aDmzButtonBox.addWidget(self._delDmzButton)
		aDmzListLayout.addLayout(aDmzButtonBox, 0)
		aDmzLayout.addLayout(aDmzListLayout, 0)

		aDmzGroupBox = QtWidgets.QGroupBox(lzx('DMZ Devices'), objectName = 'dmzGroup')
		aDmzGroupBox.setLayout(aDmzLayout)

		# Add DMZ box
		aIdLabel = QtWidgets.QLabel(lzx('ID'), objectName = 'idLabel')
		self._id = QtWidgets.QLineEdit(objectName = 'id')
		self._id.setText('webui')
		self._id.textChanged.connect(self.idTyped)
		aDeviceLabel = QtWidgets.QLabel(lzx('Device'), objectName = 'deviceLabel')
		self._deviceCombo = QtWidgets.QComboBox(objectName = 'deviceCombo')
		self._deviceCombo.activated.connect(self.deviceSelected)
		aIpLabel = QtWidgets.QLabel(lzx('IP Address'), objectName = 'ipLabel')
		self._ip = QtWidgets.QLineEdit(objectName = 'ipEdit')
		self._ip.textChanged.connect(self.ipTyped)
		aIPValidator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('^' + LmTools.IPv4_RS + '$'))
		self._ip.setValidator(aIPValidator)
		aExtIPsLabel = QtWidgets.QLabel(lzx('External IPs'), objectName = 'extIPsLabel')
		self._extIPs = LmTools.MultiLinesEdit(objectName = 'extIPsEdit')
		self._extIPs.setTabChangesFocus(True)
		self._extIPs.setLineNumber(2)
		self._addDmzButton = QtWidgets.QPushButton(lzx('Add'), objectName = 'addDmz')
		self._addDmzButton.clicked.connect(self.addDmzButtonClick)
		self._addDmzButton.setDisabled(True)

		aDmzEditGrid = QtWidgets.QGridLayout()
		aDmzEditGrid.setSpacing(10)

		aDmzEditGrid.addWidget(aIdLabel, 0, 0)
		aDmzEditGrid.addWidget(self._id, 0, 1)
		aDmzEditGrid.addWidget(aDeviceLabel, 1, 0)
		aDmzEditGrid.addWidget(self._deviceCombo, 1, 1)
		aDmzEditGrid.addWidget(aIpLabel, 2, 0)
		aDmzEditGrid.addWidget(self._ip, 2, 1)
		aDmzEditGrid.addWidget(aExtIPsLabel, 0, 2)
		aDmzEditGrid.addWidget(self._extIPs, 0, 3, 1, 2)
		aDmzEditGrid.addWidget(self._addDmzButton, 2, 4)

		aDmzEditGroupBox = QtWidgets.QGroupBox(lzx('Add DMZ'), objectName = 'addDmzGroup')
		aDmzEditGroupBox.setLayout(aDmzEditGrid)

		# Button bar
		aOkButton = QtWidgets.QPushButton(lzx('OK'), objectName = 'ok')
		aOkButton.clicked.connect(self.accept)
		aOkButton.setDefault(True)
		aButtonBar = QtWidgets.QHBoxLayout()
		aButtonBar.setSpacing(10)
		aButtonBar.addWidget(aOkButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		# Final layout
		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(20)
		aVBox.addWidget(aDmzGroupBox, 1)
		aVBox.addWidget(aDmzEditGroupBox, 0)
		aVBox.addLayout(aButtonBar, 0)

		self._ip.setFocus()

		LmConfig.SetToolTips(self, 'dmz')

		self.setWindowTitle(lzx('DMZ'))
		self.setModal(True)
		self._app.loadDeviceIpNameMap()
		self.loadDeviceList()
		self.loadDMZ()
		self.show()

		self._init = False


	### Load DMZ list
	def loadDMZ(self):
		self._app.startTask(lzx('Loading DMZ devices...'))

		try:
			d = self._app._session.request('Firewall', 'getDMZ')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			self._app.displayError(mx('Cannot load DMZ device list.', 'dmzLoadErr'))
			return

		i = 0
		for k in d:
			self._dmzList.insertRow(i)
			self._dmzList.setItem(i, DmzCol.ID, QtWidgets.QTableWidgetItem(k))

			z = d[k]
			aIP = z.get('DestinationIPAddress', '')
			self._dmzList.setItem(i, DmzCol.IP, QtWidgets.QTableWidgetItem(aIP))
			self._dmzList.setItem(i, DmzCol.Device, QtWidgets.QTableWidgetItem(self._app.getDeviceNameFromIp(aIP)))

			aExternalIPs = z.get('SourcePrefix', '')
			if len(aExternalIPs) == 0:
				aExternalIPs = lzx('All')
			self._dmzList.setItem(i, DmzCol.ExtIPs, QtWidgets.QTableWidgetItem(aExternalIPs))

			i += 1

		self.dmzListClick()
		self._app.endTask()


	### Click on DMZ list item
	def dmzListClick(self):
		aNewSelection = self._dmzList.currentRow()

		# Check if selection really changed
		if not self._init and self._dmzSelection == aNewSelection:
			return
		self._dmzSelection = aNewSelection

		self._delDmzButton.setDisabled(aNewSelection < 0)


	### Click on refresh button
	def refreshButtonClick(self):
		self._dmzList.clearContents()
		self._dmzList.setRowCount(0)
		self._dmzSelection = -1
		self._init = True
		self._app.loadDeviceIpNameMap()
		self.loadDMZ()
		self._init = False


	### Click on delete DMZ button
	def delDmzButtonClick(self):
		i = self._dmzSelection
		if i < 0:
			return

		# Delete the DMZ entry
		aID = self._dmzList.item(i, DmzCol.ID).text()
		try:
			d = self._app._session.request('Firewall', 'deleteDMZ', { 'id': aID })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None or not d:
			self._app.displayError(mx('Cannot delete DMZ device.', 'dmzDelErr'))
			return

		# Delete the list line
		self._dmzSelection = -1
		self._init = True
		self._dmzList.removeRow(i)
		self._init = False

		# Update selection
		self._dmzSelection = self._dmzList.currentRow()


	### Click on add DMZ button
	def addDmzButtonClick(self):
		# Set parameters
		h = {}
		h['id'] = self._id.text()
		h['sourceInterface'] = 'data'
		h['destinationIPAddress'] = self._ip.text()
		aExternalIPs = self._extIPs.toPlainText()
		if len(aExternalIPs):
			h['sourcePrefix'] = aExternalIPs
		h['enable'] = True

		# Call Livebox API
		try:
			d = self._app._session.request('Firewall', 'setDMZ', h)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self._app.displayError('Firewall:setDMZ query error.')
			return

		if (d is not None) and ('status' in d):
			aErrors = LmTools.GetErrorsFromLiveboxReply(d)
			if len(aErrors):
				self._app.displayError(aErrors)
				return
			self.refreshButtonClick()
			self._id.setText('webui')
			self._ip.setText('')
			self._extIPs.setPlainText('')
		else:
			self._app.displayError('Firewall:setDMZ query failed.')


	def loadDeviceList(self):
		aDeviceMap = self._app._deviceIpNameMap
		self._deviceCombo.clear()

		# Load IPv4 devices
		for i in aDeviceMap:
			if aDeviceMap[i]['IPVers'] == 'IPv4':
				self._deviceCombo.addItem(self._app.getDeviceNameFromIp(i), userData = i)

		# Sort by name
		self._deviceCombo.model().sort(0)

		# Insert unknown device at the beginning
		self._deviceCombo.insertItem(0, lzx('-Unknown-'), userData = '')
		self._deviceCombo.setCurrentIndex(0)


	def idTyped(self, iText):
		self.setAddButtonState()


	def deviceSelected(self, iIndex):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			self._ip.setText(self._deviceCombo.currentData())
			self._ignoreSignal = False


	def ipTyped(self, iText):
		if not self._ignoreSignal:
			self._ignoreSignal = True
			i = self._deviceCombo.findData(iText)
			if i < 0:
				i = 0
			self._deviceCombo.setCurrentIndex(i)
			self._ignoreSignal = False

		self.setAddButtonState()


	def setAddButtonState(self):
		self._addDmzButton.setDisabled((len(self._id.text()) == 0) or
									   (len(self._ip.text()) == 0))
