#!/usr/bin/env python3
### Python program to monitor & administrate a Livebox 4, 5 or 6 ###

import sys
import re
import traceback
import locale
import argparse

from PyQt6 import QtCore, QtGui, QtWidgets
from wakepy import keep, ActivationResult

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmConfig import (LmConf, SetApplicationStyle, SetLiveboxModel,
										 ReleaseCheck, LiveboxCnxDialog, LiveboxSigninDialog)
from LiveboxMonitor.app.LmSession import LmSession
from LiveboxMonitor.tabs import (LmDeviceListTab, LmInfoTab, LmGraphTab, LmDeviceInfoTab, LmEventsTab,
								 LmDhcpTab, LmNatPatTab, LmPhoneTab, LmActionsTab, LmRepeaterTab)
from LiveboxMonitor.lang.LmLanguages import LANGUAGES_LOCALE, GetMainLabel as lx, GetMainMessage as mx

from LiveboxMonitor.__init__ import __version__


# ################################ VARS & DEFS ################################

# Static Config
NO_THREAD = False 	# Use only to speed up testing while developping
TAB_ORDER = [
	LmDeviceListTab.TAB_NAME,
	LmInfoTab.TAB_NAME,
	LmGraphTab.TAB_NAME,
	LmDeviceInfoTab.TAB_NAME,
	LmEventsTab.TAB_NAME,
	LmDhcpTab.TAB_NAME,
	LmNatPatTab.TAB_NAME,
	LmPhoneTab.TAB_NAME,
	LmActionsTab.TAB_NAME
]


# ################################ APPLICATION ################################

# ############# Main window class #############
class LiveboxMonitorUI(QtWidgets.QMainWindow, LmDeviceListTab.LmDeviceList,
											  LmInfoTab.LmInfo,
											  LmGraphTab.LmGraph,
											  LmDeviceInfoTab.LmDeviceInfo,
											  LmEventsTab.LmEvents,
											  LmDhcpTab.LmDhcp,
											  LmNatPatTab.LmNatPat,
											  LmPhoneTab.LmPhone,
											  LmActionsTab.LmActions,
											  LmRepeaterTab.LmRepeater):

	### Initialize the application
	def __init__(self):
		super(LiveboxMonitorUI, self).__init__()
		self._taskNb = 0
		self._taskStack = []
		self._resetFlag = False
		self._appReady = False
		self._statusBar = None
		self._repeaters = []
		if not NO_THREAD:
			self.initEventLoop()
			self.initWifiStatsLoop()
			self.initStatsLoop()
			self.initRepeaterStatsLoop()
		self._applicationName = 'Livebox Monitor v' + __version__
		self.setWindowIcon(QtGui.QIcon(LmIcon.AppIconPixmap))
		self.setGeometry(100, 100, 1300, 102 + LmConfig.WindowHeight(21))
		self.show()
		QtCore.QCoreApplication.processEvents()
		if self.signin():
			self.adjustToLiveboxModel()
			self.initUI()
			self.setWindowTitle(self.appWindowTitle())
			LmConf.loadMacAddrTable()
			QtCore.QCoreApplication.processEvents()
			self.loadDeviceList()
			self.initRepeaters()
			LmConfig.SetToolTips(self, 'main')
			self._appReady = True
			if not NO_THREAD:
				self.startEventLoop()
				self.startWifiStatsLoop()

			# Force tag change tasks once app is ready
			self.tabChangedEvent(self._tabWidget.currentIndex())

			# Propose to assign local names as LB name if no name base setup yet
			self.proposeToAssignNamesToUnkownDevices()


	### Create main window
	def initUI(self):
		# Status bar
		self._statusBar = QtWidgets.QStatusBar()
		self._statusBarProfile = QtWidgets.QLabel('[' + LmConf.CurrProfile['Name'] + ']')
		self._statusBarProfile.mousePressEvent = self.statusBarProfileClick
		self._statusBar.addPermanentWidget(self._statusBarProfile)
		self.setStatusBar(self._statusBar)
		QtCore.QCoreApplication.processEvents()

		# Tab Widgets
		self._tabWidget = QtWidgets.QTabWidget(self, objectName = 'tabWidget')
		self._tabWidget.setMovable(True)
		self._tabWidget.currentChanged.connect(self.tabChangedEvent)
		self._tabWidget.tabBar().tabMoved.connect(self.tabMovedEvent)

		aTabOrder = self.getTabsOrder()
		for t in aTabOrder:
			if t == LmDeviceListTab.TAB_NAME:
				self.createDeviceListTab()
			elif t == LmInfoTab.TAB_NAME:
				self.createLiveboxInfoTab()
			elif t == LmGraphTab.TAB_NAME:
				self.createGraphTab()
			elif t == LmDeviceInfoTab.TAB_NAME:
				self.createDeviceInfoTab()
			elif t == LmEventsTab.TAB_NAME:
				self.createEventsTab()
			elif t == LmDhcpTab.TAB_NAME:
				self.createDhcpTab()
			elif t == LmNatPatTab.TAB_NAME:
				self.createNatPatTab()
			elif t == LmPhoneTab.TAB_NAME:
				self.createPhoneTab()
			elif t == LmActionsTab.TAB_NAME:
				self.createActionsTab()

		self.setCentralWidget(self._tabWidget)


	### Reset the UI, e.g. after a change of profile
	def resetUI(self):
		self._resetFlag = True
		self.close()


	### Click on the profile indication in the status bar
	def statusBarProfileClick(self, iEvent):
		self.changeProfileButtonClick()


	### Handle change of tab event
	def tabChangedEvent(self, iNewTabIndex):
		if self._appReady:
			aTabName = self._tabWidget.widget(iNewTabIndex).objectName()
			if aTabName == LmDeviceListTab.TAB_NAME:
				if not NO_THREAD:
					self.resumeWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif aTabName == LmInfoTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.resumeStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif aTabName == LmGraphTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
				self.graphTabClick()
			elif aTabName == LmDeviceInfoTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif aTabName == LmEventsTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif aTabName == LmDhcpTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
				self.dhcpTabClick()
			elif aTabName == LmNatPatTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
				self.natPatTabClick()
			elif aTabName == LmPhoneTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
				self.phoneTabClick()
			elif aTabName == LmActionsTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif aTabName == LmRepeaterTab.TAB_NAME:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.resumeRepeaterStatsLoop()


	### Handle move of tab event
	def tabMovedEvent(self, iFromIndex, iToIndex):
		self.saveTabsOrder()


	### Get tabs order
	def getTabsOrder(self):
		# If nothing in config return the standard order
		if LmConf.Tabs is None:
			return TAB_ORDER
		else:
			# Rebuild the list by checking in case it would be corrupted / incomplete
			o = []
			for t in LmConf.Tabs:
				if t in TAB_ORDER:
					o.append(t)
			for t in TAB_ORDER:
				if t not in LmConf.Tabs:
					o.append(t)
			return o


	### Save tabs order in configuration
	def saveTabsOrder(self):
		LmConf.Tabs = []	# Reset
		n = self._tabWidget.count()
		i = 0
		while i < n:
			aTab = self._tabWidget.widget(i)
			aKey = aTab.property('Key')
			if aKey is not None:
				LmConf.Tabs.append(aTab.objectName() + '_' + aKey)
			else:
				LmConf.Tabs.append(aTab.objectName())
			i += 1
		LmConf.save()


	### Get tab index from name & key, key can be None, returns -1 of not found
	def getTabIndex(self, iName, iKey):
		n = self._tabWidget.count()
		i = 0
		while i < n:
			aTab = self._tabWidget.widget(i)
			aKey = aTab.property('Key')
			if (iName == aTab.objectName()) and (iKey == aTab.property('Key')):
				return i
			i += 1
		return -1


	### Window close event
	def closeEvent(self, iEvent):
		if not NO_THREAD:
			self.startTask(lx('Terminating threads...'))
			self.stopEventLoop()
			self.stopStatsLoop()
			self.stopWifiStatsLoop()
			self.stopRepeaterStatsLoop()
			self.endTask()
		iEvent.accept()


	### Last chance to release resources
	def appTerminate(self):
		self.signoutRepeaters()
		self.signout()
		self._appReady = False


	### Sign in to Livebox
	def signin(self):
		while True:
			self.startTask(lx('Signing in...'))
			self._session = LmSession(LmConf.LiveboxURL, 'LiveboxMonitor_' + LmConf.CurrProfile['Name'])
			try:
				r = self._session.signin(LmConf.LiveboxUser, LmConf.LiveboxPassword, not LmConf.SavePasswords)
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				r = -1
			self.endTask()
			if r > 0:
				return True
			self._session = None
			self.close()

			if r < 0:
				aDialog = LiveboxCnxDialog(LmConf.LiveboxURL, self)
				if aDialog.exec():
					aURL = aDialog.getURL()
					# Remove unwanted characters (can be set via Paste action) + cleanup
					aURL = LmTools.CleanURL(re.sub('[\n\t]', '', aURL))
					LmConf.setLiveboxURL(aURL)
					self.show()
					continue
				else:
					self.displayError(mx('Cannot connect to the Livebox.', 'cnx'))
					return False

			aDialog = LiveboxSigninDialog(LmConf.LiveboxUser, LmConf.LiveboxPassword, LmConf.SavePasswords, self)
			if aDialog.exec():
				# Remove unwanted characters (can be set via Paste action)
				aUser = re.sub('[\n\t]', '', aDialog.getUser())
				aPassword = re.sub('[\n\t]', '', aDialog.getPassword())
				LmConf.SavePasswords = aDialog.getSavePasswords()
				LmConf.setLiveboxUserPassword(aUser, aPassword)
				self.show()
			else:
				self.displayError(mx('Livebox authentication failed.', 'auth'))
				return False


	### Check if signed to Livebox
	def isSigned(self):
		return self._session is not None


	### Sign out from Livebox
	def signout(self):
		if self.isSigned():
			self._session.close()
			self._session = None


	### Adjust configuration to Livebox model
	def adjustToLiveboxModel(self):
		try:
			d = self._session.request('DeviceInfo', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.Error('Error: cannot determine Livebox model')
			self._liveboxModel = 0
			self._liveboxSoftwareVersion = ''
		else:
			aMacAddr = d.get('BaseMAC', '').upper()
			LmConf.setLiveboxMAC(aMacAddr)
			self._liveboxSoftwareVersion = d.get('SoftwareVersion', '')
			aModel = d.get('ProductClass', '')
			if aModel == 'Livebox 7':
				self._liveboxModel = 7
			elif aModel == 'Livebox 6':
				self._liveboxModel = 6
			elif aModel == 'Livebox Fibre':
				self._liveboxModel = 5
			elif aModel == 'Livebox 4':
				self._liveboxModel = 4
			else:
				self._liveboxModel = 0

		self.determineFiberLink()
		SetLiveboxModel(self._liveboxModel)


	### Determine link type and if fiber or not
	def determineFiberLink(self):
		# Determine link type
		d = None
		try:
			q = self._session.request('NMC', 'getWANStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			q = None
		if q is not None:
			d = q.get('status')
		if not d:
			LmTools.Error('NMC:getWANStatus query error')
		if q is not None:
			d = q.get('data')
		else:
			d = None
		if d is None:
			LmTools.Error('NMC:getWANStatus data error')
			self._linkType = 'UNKNOWN'
		else:
			self._linkType = d.get('LinkType', 'UNKNOWN').upper()

		# Determine fiber link
		if self._liveboxModel >= 5:
			self._fiberLink = True
		elif self._liveboxModel <= 3:
			self._fiberLink = False
		else:
			# Check link type for Livebox 4
			self._fiberLink = (self._linkType == 'SFP')


	### Exit with escape
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key.Key_Escape:
			self.close()


	### Return window base title to use
	def appWindowTitle(self):
		if (self._statusBar is None) and (len(LmConf.Profiles) > 1):
			return self._applicationName + ' [' + LmConf.CurrProfile['Name'] + ']'
		return self._applicationName


	### Show the start of a long task - they can be nested
	def startTask(self, iTask):
		self._taskNb += 1
		self._taskStack.append(iTask)
		LmTools.MouseCursor_Busy()	# Stack cursor change

		if self._statusBar is None:
			self.setWindowTitle(self.appWindowTitle() + ' - ' + iTask)
		else:
			self._statusBar.showMessage(iTask)
			QtCore.QCoreApplication.sendPostedEvents()
			QtCore.QCoreApplication.processEvents()

		LmTools.LogDebug(1, 'TASK STARTING stack={} task={}'.format(self._taskNb, iTask))


	### Suspend a potential running task
	def suspendTask(self):
		if self._taskNb:
			LmTools.MouseCursor_ForceNormal()


	### Resume a potential running task
	def resumeTask(self):
		if self._taskNb:
			LmTools.MouseCursor_ForceBusy()


	### Update a task by adding a status
	def updateTask(self, iStatus):
		if self._taskNb:
			aTask = self._taskStack[self._taskNb - 1]
			if self._statusBar is None:
				self.setWindowTitle(self.appWindowTitle() + ' - ' + aTask + ' ' + iStatus + '.')
			else:
				self._statusBar.showMessage(aTask + ' ' + iStatus + '.')
				QtCore.QCoreApplication.sendPostedEvents()
				QtCore.QCoreApplication.processEvents()

			LmTools.LogDebug(1, 'TASK UPDATE stack={} - task={} - status={}'.format(self._taskNb, aTask, iStatus))


	### End a long (nested) task
	def endTask(self):
		if self._taskNb:
			self._taskNb -= 1
			self._taskStack.pop()
			LmTools.MouseCursor_Normal()	# Unstack cursor change

			if self._taskNb:
				aTask = self._taskStack[self._taskNb - 1]
				if self._statusBar is None:
					self.setWindowTitle(self.appWindowTitle() + ' - ' + aTask)
				else:
					self._statusBar.showMessage(aTask)
					QtCore.QCoreApplication.sendPostedEvents()
					QtCore.QCoreApplication.processEvents()
			else:
				aTask = '<None>'
				if self._statusBar is None:
					self.setWindowTitle(self.appWindowTitle())
				else:
					self._statusBar.clearMessage()
					QtCore.QCoreApplication.processEvents()

			LmTools.LogDebug(1, 'TASK ENDING stack={} - restoring={}'.format(self._taskNb, aTask))


	# Display an error popup
	def displayError(self, iErrorMsg):
		self.suspendTask()
		LmTools.DisplayError(iErrorMsg, self)
		self.resumeTask()


	# Display a status popup
	def displayStatus(self, iStatusMsg):
		self.suspendTask()
		LmTools.DisplayStatus(iStatusMsg, self)
		self.resumeTask()


	# Ask a question and return True if OK clicked
	def askQuestion(self, iQuestionMsg):
		self.suspendTask()
		aAnswer = LmTools.AskQuestion(iQuestionMsg, self)
		self.resumeTask()
		return aAnswer


	# Display an info text popup
	def displayInfos(self, iTitle, iInfoMsg, iInfoDoc = None):
		self.suspendTask()
		LmTools.DisplayInfos(iTitle, iInfoMsg, iInfoDoc, self)
		self.resumeTask()


	### Switch to device list tab
	def switchToDeviceListTab(self):
		self._tabWidget.setCurrentWidget(self._deviceListTab)


	### Switch to Livebox infos tab
	def switchToLiveboxInfosTab(self):
		self._tabWidget.setCurrentWidget(self._liveboxInfoTab)


	### Switch to graph tab
	def switchToGraphTab(self):
		self._tabWidget.setCurrentWidget(self._graphTab)


	### Switch to device infos tab
	def switchToDeviceInfosTab(self):
		self._tabWidget.setCurrentWidget(self._deviceInfoTab)


	### Switch to device events tab
	def switchToDeviceEventsTab(self):
		self._tabWidget.setCurrentWidget(self._eventsTab)


	### Switch to DHCP tab
	def switchToDhcpTab(self):
		self._tabWidget.setCurrentWidget(self._dhcpTab)


	### Switch to NAT/PAT tab
	def switchToNatPatTab(self):
		self._tabWidget.setCurrentWidget(self._natPatTab)


	### Switch to phone tab
	def switchToPhoneTab(self):
		self._tabWidget.setCurrentWidget(self._phoneTab)


	### Switch to actions tab
	def switchToActionsTab(self):
		self._tabWidget.setCurrentWidget(self._actionsTab)


# ### wakepy error handler
def wakePyFailure(iResult):
	LmTools.Error('Failed to keep system awake mode={} active={} success={} err={}'.format(iResult.mode_name, iResult.active_method, iResult.success, iResult.get_failure_text()))


# ### Fatal error handler
def exceptHook(iType, iValue, iTraceBack):
	aTraceBack = ''.join(traceback.format_exception(iType, iValue, iTraceBack))

	aMsgBox = QtWidgets.QMessageBox()
	aMsgBox.setWindowTitle(lx('Fatal Error'))
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
	aMsgBox.setText(aTraceBack + '\nApplication will now quit.')
	aMsgBox.exec()

	QtWidgets.QApplication.quit()


# ############# Main #############
def main(iNativeRun = False):
	# Prevent logging to fail if running without console
	if sys.stderr is None:
		sys.stderr = open(os.devnull, 'w')
	if sys.stdout is None:
		sys.stdout = open(os.devnull, 'w')

	LmConf.setNativeRun(iNativeRun)

	aApp = QtWidgets.QApplication(sys.argv)
	sys.excepthook = exceptHook
	if LmConf.load():
		LmIcon.load()
		LmConf.loadCustomDeviceIcons()
		ReleaseCheck()

		# Command line parameters
		aArgParser = argparse.ArgumentParser()
		aArgParser.add_argument('--redir', '-r', help = 'add a url redirection, REDIR format must be "url1=url2"', action = 'append')
		aArgs = aArgParser.parse_args()
		if aArgs.redir:
			LmSession.loadUrlRedirections(aArgs.redir)

		while True:
			SetApplicationStyle()

			# Apply decoupled saved preferences
			LmConf.applySavedPrefs()

			# Assign Python locale to selected preference (useful e.g. for pyqtgraph time axis localization)
			try:
				locale.setlocale(locale.LC_ALL, (LANGUAGES_LOCALE[LmConf.Language], 'UTF-8'))
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))

			# Set Qt language to selected preference
			aTranslator = QtCore.QTranslator()
			aTransPath = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.TranslationsPath)
			aTranslator.load("qtbase_" + LmConf.Language.lower(), aTransPath)
			aApp.installTranslator(aTranslator)

			# Start UI
			aUI = LiveboxMonitorUI()
			aApp.aboutToQuit.connect(aUI.appTerminate)
			if aUI.isSigned():
				if LmConf.PreventSleep:
					with keep.running(on_fail = wakePyFailure):
						aApp.exec()
				else:
					aApp.exec()
				if not aUI._resetFlag:
					break
			else:
				break


if __name__ == '__main__':
	main(True)
