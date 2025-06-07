### Livebox Monitor Backup & Restore setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.lang.LmLanguages import get_backup_restore_label as lx, get_actions_message as mx


# ################################ Backup & Restore setup dialog ################################
class BackupRestoreDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BackupRestoreDialog, self).__init__(parent)
        self.resize(400, 300)

        self._app = parent
        self._api = parent._api

        # Backup info box
        auto_backup_enabled_label = QtWidgets.QLabel(lx('Auto backup enabled:'), objectName='autoBackEnabledLabel')
        self._auto_backup_enabled = QtWidgets.QLabel(objectName='autoBackEnabled')

        status_label = QtWidgets.QLabel(lx('Status:'), objectName='statusLabel')
        self._status = QtWidgets.QLabel(objectName='status')

        last_backup_label = QtWidgets.QLabel(lx('Last Backup:'), objectName='lastBackupLabel')
        self._last_backup = QtWidgets.QLabel(objectName='lastBackup')

        info_grid = QtWidgets.QGridLayout()
        info_grid.setSpacing(5)
        info_grid.addWidget(auto_backup_enabled_label, 0, 0)
        info_grid.addWidget(self._auto_backup_enabled, 0, 1)
        info_grid.addWidget(status_label, 1, 0)
        info_grid.addWidget(self._status, 1, 1)
        info_grid.addWidget(last_backup_label, 2, 0)
        info_grid.addWidget(self._last_backup, 2, 1)

        refresh_button = QtWidgets.QPushButton(lx('Refresh'), objectName='refresh')
        refresh_button.clicked.connect(self.refresh_status)

        enable_auto_backup_button = QtWidgets.QPushButton(lx('Enable Auto Backup'), objectName='enaAutoBack')
        enable_auto_backup_button.clicked.connect(self.enable_auto_backup)

        disable_auto_backup_button = QtWidgets.QPushButton(lx('Disable Auto Backup'), objectName='disAutoBack')
        disable_auto_backup_button.clicked.connect(self.disable_auto_backup)

        force_backup_button = QtWidgets.QPushButton(lx('Force Backup'), objectName='forceBackup')
        force_backup_button.clicked.connect(self.force_backup)

        force_restore_button = QtWidgets.QPushButton(lx('Force Restore'), objectName='forceRestore')
        force_restore_button.clicked.connect(self.force_restore)

        button_grid = QtWidgets.QGridLayout()
        button_grid.setSpacing(10)
        button_grid.addWidget(refresh_button, 0, 0)
        button_grid.addWidget(enable_auto_backup_button, 1, 0)
        button_grid.addWidget(disable_auto_backup_button, 2, 0)
        button_grid.addWidget(force_backup_button, 3, 0)
        button_grid.addWidget(force_restore_button, 4, 0)

        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.setSpacing(10)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(40)
        vbox.addLayout(info_grid, 0)
        vbox.addLayout(button_grid, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, 'backrest')

        self.refresh_status()

        self.setWindowTitle(lx('Backup and Restore Setup'))
        self.setModal(True)
        self.show()


    def refresh_status(self):
        try:
            d = self._api._backup.get_status()
        except Exception as e:
            LmTools.error(str(e))
            self._app.display_error(mx('Cannot load backup and restore status.', 'backRestSvcErr'))
            return

        enabled = d.get('Enable', False)
        if enabled:
            self._auto_backup_enabled.setPixmap(LmIcon.TickPixmap)
        else:
            self._auto_backup_enabled.setPixmap(LmIcon.CrossPixmap)

        status = d.get('Status', '-')
        self._status.setText(status)

        last_backup = d.get('ConfigDate')
        if last_backup:
            self._last_backup.setText(LmTools.fmt_livebox_timestamp(last_backup, False))
        else:
            self._last_backup.setText('-')


    def enable_auto_backup(self):
        try:
            self._api._backup.set_auto_backup_enable(True)
        except Exception as e:
            LmTools.error(str(e))
            self._app.display_error(mx('Cannot enable auto backup.', 'backEnableSvcErr'))
        else:
            self.refresh_status()


    def disable_auto_backup(self):
        try:
            self._api._backup.set_auto_backup_enable(False)
        except Exception as e:
            LmTools.error(str(e))
            self._app.display_error(mx('Cannot disable auto backup.', 'backDisableSvcErr'))
        else:
            self.refresh_status()


    def force_backup(self):
        try:
            self._api._backup.do_backup()
        except Exception as e:
            LmTools.error(str(e))
            self._app.display_error(mx('Backup request failed.', 'backupSvcErr'))
        else:
            self._app.display_status(mx('Backup requested.', 'backupSvcOk'))
            self.refresh_status()


    def force_restore(self):
        try:
            self._api._backup.do_restore()
        except Exception as e:
            LmTools.error(str(e))
            self._app.display_error(mx('Restore request failed.', 'restoreSvcErr'))
        else:
            self._app.display_status(mx('Restore requested. Livebox will restart.', 'restoreSvcOk'))
