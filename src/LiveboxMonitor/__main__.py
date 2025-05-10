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
from LiveboxMonitor.app.LmConfig import (LmConf, SetApplicationStyle, SetLiveboxModel, ReleaseCheck)
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.api.LmApiRegistry import ApiRegistry
from LiveboxMonitor.tabs import (LmDeviceListTab, LmInfoTab, LmGraphTab, LmDeviceInfoTab, LmEventsTab,
								 LmDhcpTab, LmNatPatTab, LmPhoneTab, LmActionsTab, LmRepeaterTab)
from LiveboxMonitor.dlg.LmLiveboxCnx import LiveboxCnxDialog
from LiveboxMonitor.dlg.LmLiveboxSignin import LiveboxSigninDialog
from LiveboxMonitor.lang.LmLanguages import LANGUAGES_LOCALE, get_main_label as lx, get_main_message as mx

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
			self._api = ApiRegistry(self._session)
			if not self._api._intf.build_list():
				LmTools.error('Failed to build interface list.')
			self.adjustToLiveboxModel()
			self.initUI()
			self.setWindowTitle(self.appWindowTitle())
			LmConf.loadMacAddrTable()
			LmConf.loadSpamCallsTable()
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
			match t:
				case LmDeviceListTab.TAB_NAME:
					self.createDeviceListTab()
				case LmInfoTab.TAB_NAME:
					self.createLiveboxInfoTab()
				case LmGraphTab.TAB_NAME:
					self.createGraphTab()
				case LmDeviceInfoTab.TAB_NAME:
					self.createDeviceInfoTab()
				case LmEventsTab.TAB_NAME:
					self.createEventsTab()
				case LmDhcpTab.TAB_NAME:
					self.createDhcpTab()
				case LmNatPatTab.TAB_NAME:
					self.createNatPatTab()
				case LmPhoneTab.TAB_NAME:
					self.createPhoneTab()
				case LmActionsTab.TAB_NAME:
					self.create_actions_tab()

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
			match aTabName:
				case LmDeviceListTab.TAB_NAME:
					if not NO_THREAD:
						self.resumeWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
				case LmInfoTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.resumeStatsLoop()
						self.suspendRepeaterStatsLoop()
				case LmGraphTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
					self.graphTabClick()
				case LmDeviceInfoTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
				case LmEventsTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
				case LmDhcpTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
					self.dhcpTabClick()
				case LmNatPatTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
					self.natPatTabClick()
				case LmPhoneTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
					self.phoneTabClick()
				case LmActionsTab.TAB_NAME:
					if not NO_THREAD:
						self.suspendWifiStatsLoop()
						self.suspendStatsLoop()
						self.suspendRepeaterStatsLoop()
				case LmRepeaterTab.TAB_NAME:
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
		for i in range(n):
			aTab = self._tabWidget.widget(i)
			aKey = aTab.property('Key')
			if aKey is not None:
				LmConf.Tabs.append(aTab.objectName() + '_' + aKey)
			else:
				LmConf.Tabs.append(aTab.objectName())
		LmConf.save()


	### Get tab index from name & key, key can be None, returns -1 of not found
	def getTabIndex(self, iName, iKey):
		n = self._tabWidget.count()
		for i in range(n):
			aTab = self._tabWidget.widget(i)
			aKey = aTab.property('Key')
			if (iName == aTab.objectName()) and (iKey == aTab.property('Key')):
				return i
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
				LmTools.error(str(e))
				r = -1
			self.endTask()
			if r > 0:
				return True
			self._session = None
			self.close()

			if r < 0:
				aDialog = LiveboxCnxDialog(LmConf.LiveboxURL, self)
				if aDialog.exec():
					aURL = aDialog.get_url()
					# Remove unwanted characters (can be set via Paste action) + cleanup
					aURL = LmTools.clean_url(re.sub('[\n\t]', '', aURL))
					LmConf.setLiveboxURL(aURL)
					self.show()
					continue
				else:
					self.display_error(mx('Cannot connect to the Livebox.', 'cnx'))
					return False

			aDialog = LiveboxSigninDialog(LmConf.LiveboxUser, LmConf.LiveboxPassword, LmConf.SavePasswords, self)
			if aDialog.exec():
				# Remove unwanted characters (can be set via Paste action)
				aUser = re.sub('[\n\t]', '', aDialog.get_user())
				aPassword = re.sub('[\n\t]', '', aDialog.get_password())
				LmConf.SavePasswords = aDialog.get_save_passwords()
				LmConf.setLiveboxUserPassword(aUser, aPassword)
				self.show()
			else:
				self.display_error(mx('Livebox authentication failed.', 'auth'))
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
		LmConf.setLiveboxMAC(self._api._info.get_livebox_mac())
		self._liveboxSoftwareVersion = self._api._info.get_software_version()
		self._liveboxModel = self._api._info.get_livebox_model()

		LmTools.log_debug(1, f'Identified Livebox model: {self._liveboxModel} ({self._api._info.get_livebox_model_name()})')

		self.determineFiberLink()
		self.determineLiveboxPro()
		SetLiveboxModel(self._liveboxModel)


	### Determine link type and if fiber or not
	def determineFiberLink(self):
		# Determine link type
		d = None
		try:
			q = self._session.request('NMC', 'getWANStatus')
		except BaseException as e:
			LmTools.error(f'NMC:getWANStatus error: {e}')
			q = None
		if q is not None:
			d = q.get('status')
		if not d:
			LmTools.error('NMC:getWANStatus query error')
		if q is not None:
			d = q.get('data')
		else:
			d = None
		if d is None:
			LmTools.error('NMC:getWANStatus data error')
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

		LmTools.log_debug(1, f'Identified link type: {self._linkType}')
		LmTools.log_debug(1, f'Identified fiber link: {self._fiberLink}')


	### Determine if Pro or Residential subscription
	def determineLiveboxPro(self):
		d = None
		try:
			d = self._session.request('NMC', 'get')
		except BaseException as e:
			LmTools.error(f'NMC:get error: {e}')
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.error('NMC:get query error')
			self._liveboxPro = False
		else:
			aOfferType = d.get('OfferType')
			if aOfferType is None:
				LmTools.error('Missing offer type in NMC:get, cannot determine Livebox Pro model')
				self._liveboxPro = False
			else:
				self._liveboxPro = 'PRO' in aOfferType.upper()

		LmTools.log_debug(1, f'Identified Livebox Pro: {self._liveboxPro}')


	### Exit with escape
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key.Key_Escape:
			self.close()


	### Return window base title to use
	def appWindowTitle(self):
		if (self._statusBar is None) and (len(LmConf.Profiles) > 1):
			return self._applicationName + ' [' + LmConf.CurrProfile['Name'] + ']'
		return self._applicationName


	### Show the start of a long task - they can be nested - ###TODO### makes it a class
	def startTask(self, iTask):
		self._taskNb += 1
		self._taskStack.append(iTask)
		LmTools.mouse_cursor_busy()	# Stack cursor change

		if self._statusBar is None:
			self.setWindowTitle(self.appWindowTitle() + ' - ' + iTask)
		else:
			self._statusBar.showMessage(iTask)
			QtCore.QCoreApplication.sendPostedEvents()
			QtCore.QCoreApplication.processEvents()

		LmTools.log_debug(1, f'TASK STARTING stack={self._taskNb} task={iTask}')


	### Suspend a potential running task
	def suspendTask(self):
		if self._taskNb:
			LmTools.mouse_cursor_force_normal()


	### Resume a potential running task
	def resumeTask(self):
		if self._taskNb:
			LmTools.mouse_cursor_force_busy()


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

			LmTools.log_debug(1, f'TASK UPDATE stack={self._taskNb} - task={aTask} - status={iStatus}')


	### End a long (nested) task
	def endTask(self):
		if self._taskNb:
			self._taskNb -= 1
			self._taskStack.pop()
			LmTools.mouse_cursor_normal()	# Unstack cursor change

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

			LmTools.log_debug(1, f'TASK ENDING stack={self._taskNb} - restoring={aTask}')


	# Display an error popup
	def display_error(self, error_msg):
		self.suspendTask()
		LmTools.display_error(error_msg, self)
		self.resumeTask()


	# Display a status popup
	def display_status(self, status_msg):
		self.suspendTask()
		LmTools.display_status(status_msg, self)
		self.resumeTask()


	# Ask a question and return True if OK clicked
	def ask_question(self, question_msg):
		self.suspendTask()
		aAnswer = LmTools.ask_question(question_msg, self)
		self.resumeTask()
		return aAnswer


	# Display an info text popup
	def display_infos(self, title, info_msg, info_doc=None):
		self.suspendTask()
		LmTools.display_infos(title, info_msg, info_doc, self)
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
		self._tabWidget.setCurrentWidget(self._actions_tab)


# ### wakepy error handler
def wakePyFailure(iResult):
	LmTools.error(f'Failed to keep system awake mode={iResult.mode_name} active={iResult.active_method} success={iResult.success} err={iResult.get_failure_text()}')


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
		aArgParser.add_argument('--redir', '-r', help='add a url redirection, REDIR format must be "url1=url2"', action='append')
		aArgs = aArgParser.parse_args()
		if aArgs.redir:
			LmSession.load_url_redirections(aArgs.redir)

		while True:
			SetApplicationStyle()

			# Apply decoupled saved preferences
			LmConf.applySavedPrefs()

			# Assign Python locale to selected preference (useful e.g. for pyqtgraph time axis localization)
			try:
				locale.setlocale(locale.LC_ALL, (LANGUAGES_LOCALE[LmConf.Language], 'UTF-8'))
			except BaseException as e:
				LmTools.error(f'setlocale() error: {e}')

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
					with keep.running(on_fail=wakePyFailure):
						aApp.exec()
				else:
					aApp.exec()
				if not aUI._resetFlag:
					break
			else:
				break


if __name__ == '__main__':
	main(True)
