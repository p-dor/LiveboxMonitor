### Livebox Monitor Signin dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang.LmLanguages import get_config_signin_label as lx


# ################################ Livebox signin dialog ################################
class LiveboxSigninDialog(QtWidgets.QDialog):
	def __init__(self, user, password, save_passwords, parent=None):
		super(LiveboxSigninDialog, self).__init__(parent)
		self.resize(450, 130)

		user_label = QtWidgets.QLabel(lx('User'), objectName='userLabel')
		self._user_edit = QtWidgets.QLineEdit(objectName='userEdit')
		self._user_edit.textChanged.connect(self.text_changed)

		password_label = QtWidgets.QLabel(lx('Password'), objectName='passwordLabel')
		self._password_edit = QtWidgets.QLineEdit(objectName='passwordEdit')
		self._password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
		self._password_edit.textChanged.connect(self.text_changed)

		edit_grid = QtWidgets.QGridLayout()
		edit_grid.setSpacing(10)
		edit_grid.addWidget(user_label, 0, 0)
		edit_grid.addWidget(self._user_edit, 0, 1)
		edit_grid.addWidget(password_label, 1, 0)
		edit_grid.addWidget(self._password_edit, 1, 1)

		self._save_passwords = QtWidgets.QCheckBox(lx('Save passwords'), objectName='savePasswords')
		self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
		self._ok_button.clicked.connect(self.accept)
		self._ok_button.setDefault(True)
		cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
		cancel_button.clicked.connect(self.reject)
		button_bar = QtWidgets.QHBoxLayout()
		button_bar.setSpacing(10)
		button_bar.addWidget(self._save_passwords, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		ok_button_bar = QtWidgets.QHBoxLayout()
		ok_button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		ok_button_bar.setSpacing(10)
		ok_button_bar.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		ok_button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.addLayout(ok_button_bar)

		vbox = QtWidgets.QVBoxLayout(self)
		vbox.addLayout(edit_grid, 0)
		vbox.addLayout(button_bar, 1)

		self._user_edit.setFocus()

		LmConfig.SetToolTips(self, 'signin')

		title = lx('Enter password')
		if len(LmConf.Profiles) > 1:
			title += ' [' + LmConf.CurrProfile['Name'] + ']'
		self.setWindowTitle(title)

		self._user_edit.setText(user)
		self._password_edit.setText(password)
		self._save_passwords.setChecked(save_passwords)

		self.setModal(True)
		self.show()


	def text_changed(self, iText):
		self._ok_button.setDisabled((len(self.get_user()) == 0) or (len(self.get_password()) == 0))


	def get_user(self):
		return self._user_edit.text()


	def get_password(self):
		return self._password_edit.text()


	def get_save_passwords(self):
		return self._save_passwords.isChecked()
