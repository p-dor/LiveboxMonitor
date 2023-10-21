### Livebox Monitor actions tab module ###

import json
import webbrowser

from PyQt6 import QtCore, QtGui, QtWidgets

from src import LmGenApiDocumentation
from src import LmTools
from src.LmIcons import LmIcon
from src import LmConfig
from src.LmConfig import LmConf, PrefsDialog, SetApplicationStyle
from src.LmLanguages import (GetActionsLabel as lx,
							 GetActionsRHistoryDialogLabel as lrx,
							 GetActionsWGlobalDialogLabel as lwx,
							 GetActionsFirewallLevelDialogLabel as lfx,
							 GetActionsPingResponseDialogLabel as lpx)

from __init__ import __url__, __copyright__


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



# ################################ LmActions class ################################
class LmActions:

	### Create actions tab
	def createActionsTab(self):
		self._actionsTab = QtWidgets.QWidget(objectName = TAB_NAME)

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

		# Reboot & Firewall column
		aMiddleZone = QtWidgets.QVBoxLayout()
		aMiddleZone.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aMiddleZone.setSpacing(20)

		# Reboot buttons column
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

		# Firewall buttons column
		aFirewallButtons = QtWidgets.QVBoxLayout()
		aFirewallButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aFirewallButtons.setSpacing(20)

		aFirewallLevelButton = QtWidgets.QPushButton(lx('Firewall Levels...'), objectName = 'firewallLevel')
		aFirewallLevelButton.clicked.connect(self.firewallLevelButtonClick)
		aFirewallLevelButton.setMinimumWidth(BUTTON_WIDTH)
		aFirewallButtons.addWidget(aFirewallLevelButton)

		aPingResponseButton = QtWidgets.QPushButton(lx('Ping Responses...'), objectName = 'pingResponse')
		aPingResponseButton.clicked.connect(self.pingResponseButtonClick)
		aPingResponseButton.setMinimumWidth(BUTTON_WIDTH)
		aFirewallButtons.addWidget(aPingResponseButton)

		aFirewallGroupBox = QtWidgets.QGroupBox(lx('Firewall'), objectName = 'firewallGroup')
		aFirewallGroupBox.setLayout(aFirewallButtons)
		aMiddleZone.addWidget(aFirewallGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

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
		aSetupButtons.setSpacing(20)

		aPrefsButton = QtWidgets.QPushButton(lx('Preferences...'), objectName = 'prefs')
		aPrefsButton.clicked.connect(self.prefsButtonClick)
		aSetupButtons.addWidget(aPrefsButton)

		aChangeProfileButton = QtWidgets.QPushButton(lx('Change Profile...'), objectName = 'changeProfile')
		aChangeProfileButton.clicked.connect(self.changeProfileButtonClick)
		aSetupButtons.addWidget(aChangeProfileButton)

		aSetupGroupBox = QtWidgets.QGroupBox(lx('Setup'), objectName = 'setupGroup')
		aSetupGroupBox.setLayout(aSetupButtons)

		aRightZone.addWidget(aSetupGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Debug box
		aDebugButtons = QtWidgets.QVBoxLayout()
		aDebugButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aDebugButtons.setSpacing(20)

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
		aHBox.addWidget(aWifiGroupBox, 1, QtCore.Qt.AlignmentFlag.AlignTop)
		aHBox.addLayout(aMiddleZone, 1)
		aHBox.addLayout(aRightZone, 1)
		self._actionsTab.setLayout(aHBox)

		LmConfig.SetToolTips(self._actionsTab, 'actions')
		self._tabWidget.addTab(self._actionsTab, lx('Actions'))


	### Click on Wifi ON button
	def wifiOnButtonClick(self):
		self.startTask(lx('Activating Wifi...'))
		try:
			d = self._session.request('NMC.Wifi:set', { 'Enable': True, 'Status' : True })
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				self.displayError('NMC.Wifi:set service failed.')
			else:
				self.displayStatus('Wifi activated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Wifi:set service error.')
		self.endTask()


	### Click on Wifi OFF button
	def wifiOffButtonClick(self):
		self.startTask(lx('Deactivating Wifi...'))
		try:
			d = self._session.request('NMC.Wifi:set', { 'Enable': False, 'Status' : False })
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				self.displayError('NMC.Wifi:set service failed.')
			else:
				self.displayStatus('Wifi deactivated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Wifi:set service error.')
		self.endTask()


	### Click on guest Wifi ON button
	def guestWifiOnButtonClick(self):
		self.startTask(lx('Activating Guest Wifi...'))
		try:
			d = self._session.request('NMC.Guest:set', { 'Enable': True })
			if d is None:
				self.displayError('NMC.Guest:set service failed.')
			else:
				self.displayStatus('Guest Wifi activated. Reactivate Scheduler if required.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Guest:set service error.')
		self.endTask()


	### Click on guest Wifi OFF button
	def guestWifiOffButtonClick(self):
		self.startTask(lx('Deactivating Guest Wifi...'))
		try:
			d = self._session.request('NMC.Guest:set', { 'Enable': False })
			if d is None:
				self.displayError('NMC.Guest:set service failed.')
			else:
				self.displayStatus('Guest Wifi deactivated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('NMC.Guest:set service error.')
		self.endTask()


	### Click on Scheduler ON button
	def schedulerOnButtonClick(self):
		self.startTask(lx('Activating Wifi Scheduler...'))
		if self.schedulerOnOff(True):
			self.displayStatus('Scheduler activated.')
		else:
			self.displayStatus('Something failed while trying to activate the scheduler.')
		self.endTask()


	### Click on Scheduler OFF button
	def schedulerOffButtonClick(self):
		self.startTask(lx('Deactivating Wifi Scheduler...'))
		if self.schedulerOnOff(False):
			self.displayStatus('Scheduler deactivated.')
		else:
			self.displayError('Something failed while trying to deactivate the scheduler.')
		self.endTask()


	### Set Wifi Scheduler on or off, returns True if successful, False if failed
	def schedulerOnOff(self, iEnable):
		# First save network configuration
		d = self._session.request('NMC.NetworkConfig:launchNetworkBackup', { 'delay' : True })
		aFailed = False
		aRestore = False

		# Loop on each Wifi interface
		n = 0
		for i in LmConfig.NET_INTF:
			if i['Type'] == 'wif':
				# Get current schedule info
				d = self._session.request('Scheduler:getSchedule', { 'type' : 'WLAN', 'ID' : i['Key'] })
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
				d = self._session.request('Scheduler:addSchedule', { 'type' : 'WLAN', 'info' : p })
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
				self._session.request('NMC.NetworkConfig:launchNetworkRestore')		# Restore config, triggering a Livebox reboot
			aFailed = False

			for i in LmConfig.NET_INTF:
				if i['Type'] == 'wif':
					d = self._session.request('Scheduler:enableSchedule', { 'type' : 'WLAN', 'ID' : i['Key'], 'enable': iEnable })
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


	### Click on Reboot Livebox button
	def rebootLiveboxButtonClick(self):
		if self.askQuestion('Are you sure you want to reboot the Livebox?'):
			self.startTask(lx('Rebooting Livebox...'))
			try:
				r = self._session.request('NMC:reboot', { 'reason': 'GUI_Reboot' })
				if r is None:
					self.displayError('NMC:reboot service failed.')
				else:
					self.endTask()
					self.displayStatus('Application will now quit.')
					self.close()
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				self.displayError('NMC:reboot service error.')
			self.endTask()


	### Click on Reboot History button
	def rebootHistoryButtonClick(self):
		self.startTask(lx('Getting Reboot History...'))

		try:
			d = self._session.request('NMC.Reboot.Reboot:get')
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
			aReply = self._session.request('Firewall:getFirewallLevel')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall getFirewallLevel query error.')
			return

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return
			aFirewallIPv4Level = aReply['status']
		else:
			self.displayError('Firewall getFirewallLevel query failed.')
			return

		# Get current IPv6 firewall level
		try:
			aReply = self._session.request('Firewall:getFirewallIPv6Level')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall getFirewallIPv6Level query error.')
			return

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				self.displayError(aErrors)
				return
			aFirewallIPv6Level = aReply['status']
		else:
			self.displayError('Firewall getFirewallIPv6Level query failed.')
			return

		aFirewallLevelDialog = FirewallLevelDialog(aFirewallIPv4Level, aFirewallIPv6Level, self)
		if aFirewallLevelDialog.exec():
			self.startTask(lx('Set Firewall Levels...'))

			# Set new IPv4 firewall level if changed
			aNewFirewallIPv4Level = aFirewallLevelDialog.getIPv4Level()
			if aNewFirewallIPv4Level != aFirewallIPv4Level:
				try:
					aReply = self._session.request('Firewall:setFirewallLevel', { 'level': aNewFirewallIPv4Level })
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Firewall setFirewallLevel query error.')
				else:
					if (aReply is not None) and ('status' in aReply):
						aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
						if len(aErrors):
							self.displayError(aErrors)
						elif not aReply['status']:
							self.displayError('Firewall setFirewallLevel query failed.')
					else:
						self.displayError('Firewall setFirewallLevel query failed.')

			# Set new IPv6 firewall level if changed
			aNewFirewallIPv6Level = aFirewallLevelDialog.getIPv6Level()
			if aNewFirewallIPv6Level != aFirewallIPv6Level:
				try:
					aReply = self._session.request('Firewall:setFirewallIPv6Level', { 'level': aNewFirewallIPv6Level })
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Firewall setFirewallIPv6Level query error.')
				else:
					if (aReply is not None) and ('status' in aReply):
						aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
						if len(aErrors):
							self.displayError(aErrors)
						elif not aReply['status']:
							self.displayError('Firewall setFirewallIPv6Level query failed.')
					else:
						self.displayError('Firewall setFirewallIPv6Level query failed.')

			self.endTask()


	### Click on Ping Response button
	def pingResponseButtonClick(self):
		# ###Info### - works also for other sourceInterfaces such as veip0, eth0, voip, etc, but usefulness?

		# Get current ping reponses
		try:
			aReply = self._session.request('Firewall:getRespondToPing', { 'sourceInterface': 'data' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError('Firewall getRespondToPing query error.')
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
				self.displayError('Firewall getRespondToPing query failed.')
				return
		else:
			self.displayError('Firewall getRespondToPing query failed.')
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
					aReply = self._session.request('Firewall:setRespondToPing', { 'sourceInterface': 'data', 'service_enable': p })
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					self.displayError('Firewall setRespondToPing query error.')
				else:
					if (aReply is not None) and ('status' in aReply):
						aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
						if len(aErrors):
							self.displayError(aErrors)
						elif not aReply['status']:
							self.displayError('Firewall setRespondToPing query failed.')
					else:
						self.displayError('Firewall setRespondToPing query failed.')

				self.endTask()


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



# ############# Firewall Level dialog #############
class FirewallLevelDialog(QtWidgets.QDialog):
	def __init__(self, iIPv4Level, iIPv6Level, iParent = None):
		super(FirewallLevelDialog, self).__init__(iParent)
		self.setMinimumWidth(230)
		self.resize(300, 150)

		aIpV4LevelLabel = QtWidgets.QLabel(lfx('IPv4 Firewall Level:'), objectName = 'ipV4Label')
		self._ipV4LevelCombo = QtWidgets.QComboBox(objectName = 'ipV4Combo')
		for l in FIREWALL_LEVELS:
			self._ipV4LevelCombo.addItem(lfx(l), userData = l)
		self._ipV4LevelCombo.setCurrentIndex(FIREWALL_LEVELS.index(iIPv4Level))

		aIpV6LevelLabel = QtWidgets.QLabel(lfx('IPv6 Firewall Level:'), objectName = 'ipV6Label')
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

