### Livebox Monitor actions tab module ###

import json
import webbrowser

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmGenApiDocumentation
from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmConfig import LmConf, PrefsDialog, SetApplicationStyle, EmailSetupDialog
from LiveboxMonitor.dlg.LmWifiConfig import WifiConfigDialog
from LiveboxMonitor.dlg.LmWifiGlobalStatus import WifiGlobalStatusDialog
from LiveboxMonitor.dlg.LmRebootHistory import RebootHistoryDialog
from LiveboxMonitor.dlg.LmFirewall import FirewallLevelDialog
from LiveboxMonitor.dlg.LmPingResponse import PingResponseDialog
from LiveboxMonitor.dlg.LmDynDns import DynDnsSetupDialog
from LiveboxMonitor.dlg.LmDmz import DmzSetupDialog
from LiveboxMonitor.dlg.LmBackupRestore import BackupRestoreDialog
from LiveboxMonitor.dlg.LmScreen import ScreenDialog
from LiveboxMonitor.lang.LmLanguages import GetActionsLabel as lx, GetActionsMessage as mx

from LiveboxMonitor.__init__ import __url__, __copyright__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'actionTab'

# Static Config
BUTTON_WIDTH = 150


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

		aWifiConfigButton = QtWidgets.QPushButton(lx('Configuration...'), objectName = 'wifiConfig')
		aWifiConfigButton.clicked.connect(self.wifiConfigButtonClick)
		aWifiConfigButton.setMinimumWidth(BUTTON_WIDTH)
		aWifiSet.addWidget(aWifiConfigButton)

		aWifiOnButton = QtWidgets.QPushButton(lx('Wifi ON'), objectName = 'wifiOn')
		aWifiOnButton.clicked.connect(self.wifiOnButtonClick)
		aWifiSet.addWidget(aWifiOnButton)

		aWifiOffButton = QtWidgets.QPushButton(lx('Wifi OFF'), objectName = 'wifiOff')
		aWifiOffButton.clicked.connect(self.wifiOffButtonClick)
		aWifiSet.addWidget(aWifiOffButton)
		aWifiButtons.addLayout(aWifiSet, 0)

		aGuestWifiSet = QtWidgets.QHBoxLayout()
		aGuestWifiSet.setSpacing(20)

		aWifiGuestConfigButton = QtWidgets.QPushButton(lx('Guest...'), objectName = 'wifiGuestConfig')
		aWifiGuestConfigButton.clicked.connect(self.wifiGuestConfigButtonClick)
		aWifiGuestConfigButton.setMinimumWidth(BUTTON_WIDTH)
		aGuestWifiSet.addWidget(aWifiGuestConfigButton)

		aGuestWifiOnButton = QtWidgets.QPushButton(lx('Guest ON'), objectName = 'guestWifiOn')
		aGuestWifiOnButton.clicked.connect(self.guestWifiOnButtonClick)
		aGuestWifiSet.addWidget(aGuestWifiOnButton)

		aGuestWifiOffButton = QtWidgets.QPushButton(lx('Guest OFF'), objectName = 'guestWifiOff')
		aGuestWifiOffButton.clicked.connect(self.guestWifiOffButtonClick)
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

		aScreenButton = QtWidgets.QPushButton(lx('LEDs and Screen...'), objectName = 'screen')
		aScreenButton.clicked.connect(self.screenButtonClick)
		aScreenButton.setMinimumWidth(BUTTON_WIDTH)
		aMiscButtons.addWidget(aScreenButton)
		if self._liveboxModel < 6:
			aScreenButton.setEnabled(False)

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
		aDynDNSButton.clicked.connect(self.dynDnsButtonClick)
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


	### Click on Wifi config button
	def wifiConfigButtonClick(self):
		self.startTask(lx('Getting Wifi Configuration...'))
		c = self._api._wifi.get_config()
		self.endTask()
		if (c is None) or (not len(c['Intf'])):
			self.displayError(mx('Something failed while trying to get wifi configuration.', 'wifiGetConfErr'))
		else:
			aWifiConfigDialog = WifiConfigDialog(self, c, False)
			if aWifiConfigDialog.exec():
				self.startTask(lx('Setting Wifi Configuration...'))
				n = aWifiConfigDialog.get_config()
				if not self._api._wifi.set_config(c, n):
					self.displayError(mx('Something failed while trying to set wifi configuration.', 'wifiSetConfErr'))
				self.endTask()


	### Click on Wifi guest config button
	def wifiGuestConfigButtonClick(self):
		self.startTask(lx('Getting Guest Wifi Configuration...'))
		c = self._api._wifi.get_guest_config()
		self.endTask()
		if (c is None) or (not len(c['Intf'])):
			self.displayError(mx('Something failed while trying to get wifi configuration.', 'wifiGetConfErr'))
		else:
			aWifiConfigDialog = WifiConfigDialog(self, c, True)
			if aWifiConfigDialog.exec():
				self.startTask(lx('Setting Guest Wifi Configuration...'))
				n = aWifiConfigDialog.get_config()
				if not self._api._wifi.set_guest_config(c, n):
					self.displayError(mx('Something failed while trying to set wifi configuration.', 'wifiSetConfErr'))
				self.endTask()


	### Click on Wifi ON button
	def wifiOnButtonClick(self):
		self.startTask(lx('Activating Wifi...'))
		try:
			self._api._wifi.set_enable(True)
		except BaseException as e:
			self.displayError(str(e))
		else:
			self.displayStatus(mx('Wifi activated.', 'wifiOn'))
		self.endTask()


	### Click on Wifi OFF button
	def wifiOffButtonClick(self):
		self.startTask(lx('Deactivating Wifi...'))
		try:
			self._api._wifi.set_enable(False)
		except BaseException as e:
			self.displayError(str(e))
		else:
			self.displayStatus(mx('Wifi deactivated.', 'wifiOff'))
		self.endTask()


	### Click on guest Wifi ON button
	def guestWifiOnButtonClick(self):
		self.startTask(lx('Activating Guest Wifi...'))
		try:
			self._api._wifi.set_guest_enable(True)
		except BaseException as e:
			self.displayError(str(e))
		else:
			self.displayStatus(mx('Guest Wifi activated. Reactivate Scheduler if required.', 'gwifiOn'))
		self.endTask()


	### Click on guest Wifi OFF button
	def guestWifiOffButtonClick(self):
		self.startTask(lx('Deactivating Guest Wifi...'))
		try:
			self._api._wifi.set_guest_enable(False)
		except BaseException as e:
			self.displayError(str(e))
		else:
			self.displayStatus(mx('Guest Wifi deactivated.', 'gwifiOff'))
		self.endTask()


	### Click on Scheduler ON button
	def schedulerOnButtonClick(self):
		self.startTask(lx('Activating Wifi Scheduler...'))
		try:
			self._api._wifi.set_scheduler_enable(True)
		except BaseException as e:
			self.displayError(str(e))
		else:
			self.displayStatus(mx('Scheduler activated.', 'schedOn'))
		self.endTask()


	### Click on Scheduler OFF button
	def schedulerOffButtonClick(self):
		self.startTask(lx('Deactivating Wifi Scheduler...'))
		try:
			self._api._wifi.set_scheduler_enable(False)
		except BaseException as e:
			self.displayError(str(e))
		else:
			self.displayStatus(mx('Scheduler deactivated.', 'schedOff'))
		self.endTask()


	### Click on Global Wifi Status button
	def wifiGlobalStatusButtonClick(self):
		self.startTask(lx('Getting Wifi Global Status...'))

		# Getting Livebox status
		aLiveboxStatus = self._api._wifi.get_global_wifi_status()

		# Getting Repeater statuses
		aGlobalStatus = self.getRepeatersWifiStatus()
		aGlobalStatus.insert(0, aLiveboxStatus)

		self.endTask()

		aStatusDialog = WifiGlobalStatusDialog(self, aGlobalStatus, self._liveboxModel)
		aStatusDialog.exec()


	### Click on the Backup & Restore button
	def backupRestoreButtonClick(self):
		aBackupRestoreDialog = BackupRestoreDialog(self)
		aBackupRestoreDialog.exec()


	### Click on LEDs & Screen setup button
	def screenButtonClick(self):
		try:
			aOrangeLedLevel = self._api._screen.get_orange_led_level()
			aShowWifiPassword = self._api._screen.get_show_wifi_password()
		except BaseException as e:
			self.displayError(str(e))
			return

		aScreenDialog = ScreenDialog(aOrangeLedLevel, aShowWifiPassword, self)
		if aScreenDialog.exec():
			self.startTask(lx('Setting LEDs & Screen Setup...'))

			# Set orange LED level if changed
			aNewOrangeLedLevel = aScreenDialog.get_orange_led_level()
			if aNewOrangeLedLevel != aOrangeLedLevel:
				try:
					self._api._screen.set_orange_led_level(aNewOrangeLedLevel)
				except BaseException as e:
					self.displayError(str(e))

			# Set show wifi password if changed
			aNewShowWifiPassword = aScreenDialog.get_show_wifi_password()
			if aNewShowWifiPassword != aShowWifiPassword:
				try:
					self._api._screen.set_show_wifi_password(aNewShowWifiPassword)
				except BaseException as e:
					self.displayError(str(e))

			self.endTask()


	### Click on Reboot Livebox button
	def rebootLiveboxButtonClick(self):
		if self.askQuestion(mx('Are you sure you want to reboot the Livebox?', 'lbReboot')):
			self.startTask(lx('Rebooting Livebox...'))
			try:
				self._api._reboot.reboot_livebox()
			except BaseException as e:
				self.endTask()
				self.displayError(str(e))
				return

			self.endTask()
			self.displayStatus(mx('Application will now quit.', 'appQuit'))
			self.close()


	### Click on Reboot History button
	def rebootHistoryButtonClick(self):
		self.startTask(lx('Getting Reboot History...'))

		try:
			d = self._api._reboot.get_reboot_history()
		except BaseException as e:
			self.endTask()
			self.displayError(str(e))
			return

		self.endTask()

		aHistoryDialog = RebootHistoryDialog('Livebox', self)
		aHistoryDialog.load_history(d)
		aHistoryDialog.exec()


	### Click on Firewall Level button
	def firewallLevelButtonClick(self):
		try:
			aFirewallIPv4Level = self._api._firewall.get_ipv4_firewall_level()
			aFirewallIPv6Level = self._api._firewall.get_ipv6_firewall_level()
		except BaseException as e:
			self.displayError(str(e))
			return

		aFirewallLevelDialog = FirewallLevelDialog(aFirewallIPv4Level, aFirewallIPv6Level, self)
		if aFirewallLevelDialog.exec():
			self.startTask(lx('Setting Firewall Levels...'))

			# Set new IPv4 firewall level if changed
			aNewFirewallIPv4Level = aFirewallLevelDialog.get_ipv4_level()
			if aNewFirewallIPv4Level != aFirewallIPv4Level:
				try:
					self._api._firewall.set_ipv4_firewall_level(aNewFirewallIPv4Level)
				except BaseException as e:
					self.displayError(str(e))

			# Set new IPv6 firewall level if changed
			aNewFirewallIPv6Level = aFirewallLevelDialog.get_ipv6_level()
			if aNewFirewallIPv6Level != aFirewallIPv6Level:
				try:
					self._api._firewall.set_ipv6_firewall_level(aNewFirewallIPv6Level)
				except BaseException as e:
					self.displayError(str(e))

			self.endTask()


	### Click on Ping Response button
	def pingResponseButtonClick(self):
		# Get current ping reponses
		try:
			d = self._api._firewall.get_respond_to_ping()
		except BaseException as e:
			self.displayError(str(e))
			return
		aIPv4Ping = d.get('enableIPv4')
		aIPv6Ping = d.get('enableIPv6')
		if (aIPv4Ping is None) or (aIPv6Ping is None):
			LmTools.Error('Cannot get respond to ping setup')

		aPingResponseDialog = PingResponseDialog(aIPv4Ping, aIPv6Ping, self)
		if aPingResponseDialog.exec():
			# Set new ping responses level if changed
			aNewIPv4Ping = aPingResponseDialog.get_ipv4()
			aNewIPv6Ping = aPingResponseDialog.get_ipv6()
			if (aNewIPv4Ping != aIPv4Ping) or (aNewIPv6Ping != aIPv6Ping):
				self.startTask(lx('Set Ping Responses...'))
				p = {}
				p['enableIPv4'] = aNewIPv4Ping
				p['enableIPv6'] = aNewIPv6Ping
				try:
					self._api._firewall.set_respond_to_ping(p)
				except BaseException as e:
					self.displayError(str(e))
				self.endTask()


	### Click on DynDNS button
	def dynDnsButtonClick(self):
		aDynDnsSetupDialog = DynDnsSetupDialog(self)
		aDynDnsSetupDialog.exec()


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
