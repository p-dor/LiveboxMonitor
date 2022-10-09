### Python program to monitor a Livebox 5 ###
# Livebox authentication & service request interfaces copied/adapted from sysbus package

# References:
# Qt6 ->    https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
#			https://doc.qt.io/

import sys

from enum import IntEnum

from PyQt6 import QtCore
from PyQt6 import QtWidgets

import LmTools
from LmIcons import LmIcon
from LmConfig import LmConf
from LmConfig import MonitorTab
from LmSession import LmSession
import LmDeviceListTab
import LmInfoTab
import LmDeviceInfoTab
import LmEventsTab
import LmActionsTab
import LmRepeaterTab



# ################################ VARS & DEFS ################################

# Static Config
from __init__ import __version__
WINDOW_TITLE = 'Livebox Monitor v' + __version__

NO_THREAD = False 	# Use only to speed up testing while developping



# ################################ APPLICATION ################################

# ############# Main window class #############
class LiveboxMonitorUI(QtWidgets.QWidget, LmDeviceListTab.LmDeviceList,
										  LmInfoTab.LmInfo,
										  LmDeviceInfoTab.LmDeviceInfo,
										  LmEventsTab.LmEvents,
										  LmActionsTab.LmActions,
										  LmRepeaterTab.LmRepeater):

	### Initialize the application
	def __init__(self):
		super(LiveboxMonitorUI, self).__init__()
		self._appReady = False
		self._repeaters = []
		if not NO_THREAD:
			self.initEventLoop()
			self.initWifiStatsLoop()
			self.initStatsLoop()
			self.initRepeaterStatsLoop()
		self.initUI()
		if self.signin():
			LmConf.loadMacAddrTable()
			self.loadDeviceList()
			self.initRepeaters()
			self._appReady = True
			if not NO_THREAD:
				self.startEventLoop()
				self.startWifiStatsLoop()


	### Create main window
	def initUI(self):
		self.setWindowTitle(WINDOW_TITLE)

		# Tab Widgets
		self._tabWidget = QtWidgets.QTabWidget(self)
		self._tabWidget.currentChanged.connect(self.tabChangedEvent)
		self.createDeviceListTab()
		self.createLiveboxInfoTab()
		self.createDeviceInfoTab()
		self.createEventsTab()
		self.createActionsTab()

		# Layout
		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(self._tabWidget)

		self.setLayout(aGrid)
		self.setGeometry(200, 200, 1300, 761)

		self.show()


	### Handle change of tab event
	def tabChangedEvent(self, iNewTabIndex):
		if NO_THREAD:
			return

		if self._appReady:
			if iNewTabIndex == MonitorTab.DeviceList:
				self.resumeWifiStatsLoop()
				self.suspendStatsLoop()
				self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.LiveboxInfos:
				self.suspendWifiStatsLoop()
				self.resumeStatsLoop()
				self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.DeviceInfos:
				self.suspendWifiStatsLoop()
				self.suspendStatsLoop()
				self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.DeviceEvents:
				self.suspendWifiStatsLoop()
				self.suspendStatsLoop()
				self.suspendRepeaterStatsLoop()
			elif iNewTabIndex == MonitorTab.Actions:
				self.suspendWifiStatsLoop()
				self.suspendStatsLoop()
				self.suspendRepeaterStatsLoop()
			elif iNewTabIndex >= MonitorTab.Repeaters:
				self.suspendWifiStatsLoop()
				self.suspendStatsLoop()
				self.resumeRepeaterStatsLoop()


	### Window close event
	def closeEvent(self, iEvent):
		self.startTask('Terminating threads...')
		if not NO_THREAD:
			self.stopEventLoop()
			self.stopStatsLoop()
			self.stopWifiStatsLoop()
			self.stopRepeaterStatsLoop()
		self.endTask()
		self.signoutRepeaters()
		self.signout()
		self._appReady = False
		iEvent.accept()


	### Sign in to Livebox
	def signin(self):
		while True:
			self.startTask('Signing in...')
			self._session = LmSession()
			r = self._session.signin(True)
			self.endTask()
			if r:
				return True
			self._session = None
			self.close()

			aPassword, aOK = QtWidgets.QInputDialog.getText(self, 'Wrong password',
															'Please enter Livebox password:',
															QtWidgets.QLineEdit.EchoMode.Password,
															text = LmConf.LiveboxPassword)
			if aOK:
				LmConf.setLiveboxPassword(aPassword)
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


	### Exit with escape
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key.Key_Escape:
			self.close()


	### Show the start of a long task
	def startTask(self, iTask):
		self.setWindowTitle(WINDOW_TITLE + ' - ' + iTask)
		LmTools.MouseCursor_Busy()


	### End a long task
	def endTask(self):
		LmTools.MouseCursor_Normal()
		self.setWindowTitle(WINDOW_TITLE)


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


	### Switch to actions tab
	def switchToActionsTab(self):
		self._tabWidget.setCurrentIndex(MonitorTab.Actions)



# ############# Main #############

if __name__ == '__main__':
	LmConf.load()
	LmTools.SetApplicationStyle()
	aApp = QtWidgets.QApplication(sys.argv)
	LmIcon.load()
	aUI = LiveboxMonitorUI()
	if aUI.isSigned():
		aApp.exec()
