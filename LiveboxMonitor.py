### Python program to monitor a Livebox 5 ###
# Livebox authentication & service request interfaces copied/adapted from sysbus package

# References:
# Qt6 ->    https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
#			https://doc.qt.io/

import sys
import re

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
from src import LmPhoneTab
from src import LmActionsTab
from src import LmRepeaterTab

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
			self._appReady = True
			if not NO_THREAD:
				self.startEventLoop()
				self.startWifiStatsLoop()


	### Create main window
	def initUI(self):
		# Tab Widgets
		self._tabWidget = QtWidgets.QTabWidget(self)
		self._tabWidget.currentChanged.connect(self.tabChangedEvent)
		self.createDeviceListTab()
		self.createLiveboxInfoTab()
		self.createDeviceInfoTab()
		self.createEventsTab()
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
			self.startTask('Terminating threads...')
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
			self.startTask('Signing in...')
			self._session = LmSession(LmConf.LiveboxURL)
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
					aURL = LmTools.cleanURL(re.sub('[\n\t]', '', aURL))
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
			aModel = d.get('ProductClass', '')
			if aModel == 'Livebox 6':
				self._liveboxModel = 'LB6'
			elif aModel == 'Livebox Fibre':
				self._liveboxModel = 'LB5'
			else:
				self._liveboxModel = 'LBx'

		SetLiveboxModel(self._liveboxModel)
		LmRepeaterTab.SetRepeaterLiveboxModel(self._liveboxModel)


	### Exit with escape
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key.Key_Escape:
			self.close()


	### Return window's base title to use
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


	### Switch to phone tab
	def switchToPhoneTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.Phone)


	### Switch to actions tab
	def switchToActionsTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.Actions)



# ############# Main #############

if __name__ == '__main__':
	aApp = QtWidgets.QApplication(sys.argv)
	if LmConf.load():
		SetApplicationStyle()
		LmIcon.load()
		while True:
			aUI = LiveboxMonitorUI()
			aApp.aboutToQuit.connect(aUI.appTerminate)
			if aUI.isSigned():
				aApp.exec()
				if not aUI._resetFlag:
					break
			else:
				break
