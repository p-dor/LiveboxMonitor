### Livebox Monitor Backup & Restore setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.lang.LmLanguages import GetBackupRestoreDialogLabel as lx, GetActionsMessage as mx


# ################################ Backup & Restore setup dialog ################################
class BackupRestoreDialog(QtWidgets.QDialog):
	def __init__(self, iParent = None):
		super(BackupRestoreDialog, self).__init__(iParent)
		self.resize(400, 300)

		self._app = iParent
		self._api = iParent._api

		# Backup info box
		aAutoBackupEnabledLabel = QtWidgets.QLabel(lx('Auto backup enabled:'), objectName = 'autoBackEnabledLabel')
		self._autoBackupEnabled = QtWidgets.QLabel(objectName = 'autoBackEnabled')

		aStatusLabel = QtWidgets.QLabel(lx('Status:'), objectName = 'statusLabel')
		self._status = QtWidgets.QLabel(objectName = 'status')

		aLastBackupLabel = QtWidgets.QLabel(lx('Last Backup:'), objectName = 'lastBackupLabel')
		self._lastBackup = QtWidgets.QLabel(objectName = 'lastBackup')

		aInfoGrid = QtWidgets.QGridLayout()
		aInfoGrid.setSpacing(5)
		aInfoGrid.addWidget(aAutoBackupEnabledLabel, 0, 0)
		aInfoGrid.addWidget(self._autoBackupEnabled, 0, 1)
		aInfoGrid.addWidget(aStatusLabel, 1, 0)
		aInfoGrid.addWidget(self._status, 1, 1)
		aInfoGrid.addWidget(aLastBackupLabel, 2, 0)
		aInfoGrid.addWidget(self._lastBackup, 2, 1)

		aRefreshButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refresh')
		aRefreshButton.clicked.connect(self.refreshStatus)

		aEnableAutoBackupButton = QtWidgets.QPushButton(lx('Enable Auto Backup'), objectName = 'enaAutoBack')
		aEnableAutoBackupButton.clicked.connect(self.enableAutoBackup)

		aDisableAutoBackupButton = QtWidgets.QPushButton(lx('Disable Auto Backup'), objectName = 'disAutoBack')
		aDisableAutoBackupButton.clicked.connect(self.disableAutoBackup)

		aForceBackupButton = QtWidgets.QPushButton(lx('Force Backup'), objectName = 'forceBackup')
		aForceBackupButton.clicked.connect(self.forceBackup)

		aForceRestoreButton = QtWidgets.QPushButton(lx('Force Restore'), objectName = 'forceRestore')
		aForceRestoreButton.clicked.connect(self.forceRestore)

		aButtonGrid = QtWidgets.QGridLayout()
		aButtonGrid.setSpacing(10)
		aButtonGrid.addWidget(aRefreshButton, 0, 0)
		aButtonGrid.addWidget(aEnableAutoBackupButton, 1, 0)
		aButtonGrid.addWidget(aDisableAutoBackupButton, 2, 0)
		aButtonGrid.addWidget(aForceBackupButton, 3, 0)
		aButtonGrid.addWidget(aForceRestoreButton, 4, 0)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(lx('OK'), objectName = 'ok')
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

		self.setWindowTitle(lx('Backup and Restore Setup'))
		self.setModal(True)
		self.show()


	def refreshStatus(self):
		try:
			d = self._api._backup.get_status()
		except BaseException as e:
			LmTools.Error(str(e))
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
			self._lastBackup.setText(LmTools.FmtLiveboxTimestamp(aLastBackup, False))
		else:
			self._lastBackup.setText('-')


	def enableAutoBackup(self):
		try:
			self._api._backup.set_auto_backup_enable(True)
		except BaseException as e:
			LmTools.Error(str(e))
			self._app.displayError(mx('Cannot enable auto backup.', 'backEnableSvcErr'))
		else:
			self.refreshStatus()


	def disableAutoBackup(self):
		try:
			self._api._backup.set_auto_backup_enable(False)
		except BaseException as e:
			LmTools.Error(str(e))
			self._app.displayError(mx('Cannot disable auto backup.', 'backDisableSvcErr'))
		else:
			self.refreshStatus()


	def forceBackup(self):
		try:
			self._api._backup.do_backup()
		except BaseException as e:
			LmTools.Error(str(e))
			self._app.displayError(mx('Backup request failed.', 'backupSvcErr'))
		else:
			self._app.displayStatus(mx('Backup requested.', 'backupSvcOk'))
			self.refreshStatus()


	def forceRestore(self):
		try:
			self._api._backup.do_restore()
		except BaseException as e:
			LmTools.Error(str(e))
			self._app.displayError(mx('Restore request failed.', 'restoreSvcErr'))
		else:
			self._app.displayStatus(mx('Restore requested. Livebox will restart.', 'restoreSvcOk'))
