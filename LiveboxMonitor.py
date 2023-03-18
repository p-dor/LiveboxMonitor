### Python program to monitor & administrate a Livebox 4, 5 or 6 ###

import sys
import re
import traceback

from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6 import QtWidgets

from src import LmTools
from src.LmIcons import LmIcon
from src.LmConfig import LmConf
from src.LmConfig import SetApplicationStyle
from src.LmConfig import SetLiveboxModel
from src.LmConfig import MonitorTab
from src.LmConfig import LiveboxCnxDialog
from src.LmConfig import LiveboxSigninDialog
from src.LmSession import LmSession
from src import LmConfig
from src import LmDeviceListTab
from src import LmInfoTab
from src import LmDeviceInfoTab
from src import LmEventsTab
from src import LmDhcpTab
from src import LmPhoneTab
from src import LmActionsTab
from src import LmRepeaterTab
from src.LmLanguages import GetMainLabel as lx

from __init__ import __version__



# ################################ VARS & DEFS ################################

# Static Config
NO_THREAD = False 	# Use only to speed up testing while developping



# ################################ APPLICATION ################################

# ############# Main window class #############
class LiveboxMonitorUI(QtWidgets.QWidget, LmDeviceListTab.LmDeviceList,
										  LmInfoTab.LmInfo,
										  LmDeviceInfoTab.LmDeviceInfo,
										  LmEventsTab.LmEvents,
										  LmDhcpTab.LmDhcp,
										  LmPhoneTab.LmPhone,
										  LmActionsTab.LmActions,
										  LmRepeaterTab.LmRepeater):

	### Initialize the application
	def __init__(self):
		super(LiveboxMonitorUI, self).__init__()
		self._resetFlag = False
		self._appReady = False
		self._repeaters = []
		if not NO_THREAD:
			self.initEventLoop()
			self.initWifiStatsLoop()
			self.initStatsLoop()
			self.initRepeaterStatsLoop()
		self._applicationName = 'Livebox Monitor v' + __version__
		self.setWindowTitle(self.appWindowTitle())
		self.setWindowIcon(QtGui.QIcon(LmIcon.AppIconPixmap))
		self.setGeometry(100, 100, 1300, 102 + LmConfig.WindowHeight(21))
		self.show()
		QtCore.QCoreApplication.processEvents()
		if self.signin():
			self.adjustToLiveboxModel()
			self.initUI()
			LmConf.loadMacAddrTable()
			QtCore.QCoreApplication.processEvents()
			self.loadDeviceList()
			self.initRepeaters()
			LmConfig.SetToolTips(self, 'main')
			self._appReady = True
			if not NO_THREAD:
				self.startEventLoop()
				self.startWifiStatsLoop()


	### Create main window
	def initUI(self):
		# Tab Widgets
		self._tabWidget = QtWidgets.QTabWidget(self, objectName = 'tabWidget')
		self._tabWidget.currentChanged.connect(self.tabChangedEvent)
		self.createDeviceListTab()
		self.createLiveboxInfoTab()
		self.createDeviceInfoTab()
		self.createEventsTab()
		self.createDhcpTab()
		self.createPhoneTab()
		self.createActionsTab()

		# Layout
		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(self._tabWidget)

		self.setLayout(aGrid)


	### Reset the UI, e.g. after a change of profile
	def resetUI(self):
		self._resetFlag = True
		self.close()


	### Handle change of tab event
	def tabChangedEvent(self, iNewTabIndex):
		if self._appReady:
			if iNewTabIndex == MonitorTab.DeviceList:
				if not NO_THREAD:
					self.resumeWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.LiveboxInfos:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.resumeStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.DeviceInfos:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.DeviceEvents:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.Dhcp:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
				self.dhcpTabClick()
			elif iNewTabIndex == MonitorTab.Phone:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
				self.phoneTabClick()
			elif iNewTabIndex == MonitorTab.Actions:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.suspendRepeaterStatsLoop()
			elif iNewTabIndex >= MonitorTab.Repeaters:
				if not NO_THREAD:
					self.suspendWifiStatsLoop()
					self.suspendStatsLoop()
					self.resumeRepeaterStatsLoop()


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
				r = self._session.signin(LmConf.LiveboxUser, LmConf.LiveboxPassword)
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
					LmTools.DisplayError('Cannot connect to the Livebox.')
					return False

			aDialog = LiveboxSigninDialog(LmConf.LiveboxUser, LmConf.LiveboxPassword, self)
			if aDialog.exec():
				# Remove unwanted characters (can be set via Paste action)
				aUser = re.sub('[\n\t]', '', aDialog.getUser())
				aPassword = re.sub('[\n\t]', '', aDialog.getPassword())
				LmConf.setLiveboxUserPassword(aUser, aPassword)
				self.show()
			else:
				LmTools.DisplayError('Livebox authentication failed.')
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
			d = self._session.request('DeviceInfo:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			LmTools.Error('Error: cannot determine Livebox model')
			self._liveboxModel = 'LBx'
		else:
			aMacAddr = d.get('BaseMAC', '').upper()
			LmConf.setLiveboxMAC(aMacAddr)
			aModel = d.get('ProductClass', '')
			if aModel == 'Livebox 6':
				self._liveboxModel = 'LB6'
			elif aModel == 'Livebox Fibre':
				self._liveboxModel = 'LB5'
			elif aModel == 'Livebox 4':
				self._liveboxModel = 'LB4'
			else:
				self._liveboxModel = 'LBx'

		SetLiveboxModel(self._liveboxModel)
		LmRepeaterTab.SetRepeaterLiveboxModel(self._liveboxModel)


	### Exit with escape
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key.Key_Escape:
			self.close()


	### Return window base title to use
	def appWindowTitle(self):
		if len(LmConf.Profiles) > 1:
			return self._applicationName + ' [' + LmConf.CurrProfile['Name'] + ']'
		return self._applicationName


	### Show the start of a long task
	def startTask(self, iTask):
		self.setWindowTitle(self.appWindowTitle() + ' - ' + iTask)
		LmTools.MouseCursor_Busy()


	### End a long task
	def endTask(self):
		LmTools.MouseCursor_Normal()
		self.setWindowTitle(self.appWindowTitle())


	### Switch to device list tab
	def switchToDeviceListTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.DeviceList)


	### Switch to Livebox infos tab
	def switchToLiveboxInfosTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.LiveboxInfos)


	### Switch to device infos tab
	def switchToDeviceInfosTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.DeviceInfos)


	### Switch to device events tab
	def switchToDeviceEventsTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.DeviceEvents)


	### Switch to DHCP tab
	def switchToDhcpTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.Dhcp)


	### Switch to phone tab
	def switchToPhoneTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.Phone)


	### Switch to actions tab
	def switchToActionsTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.Actions)


# ############# Fatal error handler #############

def exceptHook(iType, iValue, iTraceBack):
	aTraceBack = ''.join(traceback.format_exception(iType, iValue, iTraceBack))

	aMsgBox = QtWidgets.QMessageBox()
	aMsgBox.setWindowTitle(lx('Fatal Error'))
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
	aMsgBox.setText(aTraceBack + '\nApplication will now quit.')
	aMsgBox.exec()

	QtWidgets.QApplication.quit()


# ############# Main #############

if __name__ == '__main__':
	# Prevent logging to fail if running without console
	if sys.stderr is None:
		sys.stderr = open(os.devnull, "w")
	if sys.stdout is None:
		sys.stdout = open(os.devnull, "w")

	aApp = QtWidgets.QApplication(sys.argv)
	sys.excepthook = exceptHook
	if LmConf.load():
		SetApplicationStyle()
		LmIcon.load()
		while True:
			# Set Qt language to selected preference
			aTranslator = QtCore.QTranslator()
			aTransPath = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.TranslationsPath)
			aTranslator.load("qtbase_" + LmConf.Language.lower(), aTransPath)
			aApp.installTranslator(aTranslator)

			# Start UI
			aUI = LiveboxMonitorUI()
			aApp.aboutToQuit.connect(aUI.appTerminate)
			if aUI.isSigned():
				aApp.exec()
				if not aUI._resetFlag:
					break
			else:
				break
