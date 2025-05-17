### Livebox Monitor Email setup dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang.LmLanguages import get_config_email_label as lx,  get_config_message as mx


# ################################ Email setup dialog ################################
class EmailSetupDialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(EmailSetupDialog, self).__init__(parent)
		self.resize(515, 310)

		self._init = True

		email_reg_exp = QtCore.QRegularExpression(LmTools.EMAIL_RS)
		email_validator = QtGui.QRegularExpressionValidator(email_reg_exp)

		from_addr_label = QtWidgets.QLabel(lx('From Address'), objectName='fromAddrLabel')
		self._from_address = QtWidgets.QLineEdit(objectName='fromAddrEdit')
		self._from_address.textChanged.connect(self.setup_changed)
		self._from_address.setValidator(email_validator)

		to_addr_label = QtWidgets.QLabel(lx('To Address'), objectName='toAddrLabel')
		self._to_address = QtWidgets.QLineEdit(objectName='toAddrEdit')
		self._to_address.textChanged.connect(self.setup_changed)
		self._to_address.setValidator(email_validator)

		subject_prefix_label = QtWidgets.QLabel(lx('Subject Prefix'), objectName='subjectPrefixLabel')
		self._subject_prefix = QtWidgets.QLineEdit(objectName='subjectPrefixEdit')

		smtp_server_label = QtWidgets.QLabel(lx('SMTP Server'), objectName='smtpServerLabel')
		self._smtp_server = QtWidgets.QLineEdit(objectName='smtpServerEdit')
		self._smtp_server.textChanged.connect(self.setup_changed)

		port_reg_exp = QtCore.QRegularExpression(LmTools.PORTS_RS)
		port_validator = QtGui.QRegularExpressionValidator(port_reg_exp)
		smtp_port_label = QtWidgets.QLabel(lx('Port'), objectName='smtpPortLabel')
		self._smtp_port = QtWidgets.QLineEdit(objectName='smtpPortEdit')
		self._smtp_port.setValidator(port_validator)

		options_label = QtWidgets.QLabel(lx('Options'), objectName='optionsLabel')
		self._use_starttls = QtWidgets.QCheckBox(lx('Use STARTTLS'), objectName='useSTARTTLS')
		self._use_starttls.stateChanged.connect(self.starttls_changed)
		self._use_tls = QtWidgets.QCheckBox(lx('Use TLS'), objectName='useTLS')
		self._use_tls.stateChanged.connect(self.tls_changed)
		self._authentication = QtWidgets.QCheckBox(lx('Authentication'), objectName='authentication')
		self._authentication.stateChanged.connect(self.setup_changed)

		user_label = QtWidgets.QLabel(lx('User'), objectName='userLabel')
		self._user = QtWidgets.QLineEdit(objectName='userEdit')
		self._user.textChanged.connect(self.setup_changed)

		password_label = QtWidgets.QLabel(lx('Password'), objectName='passwordLabel')
		self._password = QtWidgets.QLineEdit(objectName='passwordEdit')
		self._password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
		self._password.textChanged.connect(self.setup_changed)

		edit_grid = QtWidgets.QGridLayout()
		edit_grid.setSpacing(10)
		edit_grid.addWidget(from_addr_label, 0, 0)
		edit_grid.addWidget(self._from_address, 0, 1, 1, 10)
		edit_grid.addWidget(to_addr_label, 1, 0)
		edit_grid.addWidget(self._to_address, 1, 1, 1, 10)
		edit_grid.addWidget(subject_prefix_label, 2, 0)
		edit_grid.addWidget(self._subject_prefix, 2, 1, 1, 10)
		edit_grid.addWidget(smtp_server_label, 3, 0)
		edit_grid.addWidget(self._smtp_server, 3, 1, 1, 8)
		edit_grid.addWidget(smtp_port_label, 3, 9)
		edit_grid.addWidget(self._smtp_port, 3, 10)
		edit_grid.addWidget(options_label, 4, 0)
		edit_grid.addWidget(self._use_starttls, 4, 1)
		edit_grid.addWidget(self._use_tls, 4, 3)
		edit_grid.addWidget(self._authentication, 4, 5)
		edit_grid.addWidget(user_label, 5, 0)
		edit_grid.addWidget(self._user, 5, 1, 1, 10)
		edit_grid.addWidget(password_label, 6, 0)
		edit_grid.addWidget(self._password, 6, 1, 1, 10)

		# Button bar
		self._test_button = QtWidgets.QPushButton(lx('Test Sending'), objectName='test')
		self._test_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 3px; padding-bottom: 3px;')
		self._test_button.clicked.connect(self.test_button_click)
		self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
		self._ok_button.clicked.connect(self.accept)
		self._ok_button.setDefault(True)
		cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
		cancel_button.clicked.connect(self.reject)
		button_bar = QtWidgets.QHBoxLayout()
		button_bar.setSpacing(10)
		button_bar.addWidget(self._test_button, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		ok_button_bar = QtWidgets.QHBoxLayout()
		ok_button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		ok_button_bar.setSpacing(10)
		ok_button_bar.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		ok_button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.addLayout(ok_button_bar)

		# Final layout
		vbox = QtWidgets.QVBoxLayout(self)
		vbox.setSpacing(20)
		vbox.addLayout(edit_grid, 0)
		vbox.addLayout(button_bar, 1)

		self._from_address.setFocus()

		LmConfig.set_tooltips(self, 'email')

		self.setWindowTitle(lx('Email Setup'))
		self.setModal(True)
		self.load_setup()
		self.show()

		self._init = False


	### Load preferences data
	def load_setup(self):
		# If no config set to default values
		c = LmConf.load_email_setup()
		if c is None:
			c = {}

		self._from_address.setText(c.get('From', ''))
		self._to_address.setText(c.get('To', ''))
		self._subject_prefix.setText(c.get('Prefix', '[LiveboxMonitor] '))
		self._smtp_server.setText(c.get('Server', ''))
		self._smtp_port.setText(str(int(c.get('Port', 587))))
		starttls = c.get('TLS', True)
		self._use_starttls.setChecked(starttls)
		self._use_tls.setChecked(c.get('SSL', False) and not starttls)
		self._authentication.setChecked(c.get('Authentication', True))
		self._user.setText(c.get('User', ''))
		self._password.setText(c.get('Password', ''))

		self.setup_changed(None)


	### Return current setup in dialog
	def get_setup(self):
		c = {}
		c['From'] = self._from_address.text()
		c['To'] = self._to_address.text()
		c['Prefix'] = self._subject_prefix.text()
		c['Server'] = self._smtp_server.text()
		try:
			c['Port'] = int(self._smtp_port.text())
		except:
			c['Port'] = 0
		c['TLS'] = self._use_starttls.isChecked()
		c['SSL'] = self._use_tls.isChecked()
		c['Authentication'] = self._authentication.isChecked()
		c['User'] = self._user.text()
		c['Password'] = self._password.text()
		return c


	### Click on test button
	def test_button_click(self):
		app = self.parentWidget()
		app.startTask(lx('Sending test email...'))
		c = self.get_setup()
		if LmTools.send_email(c, lx('Test Message'), lx('This is a test email from LiveboxMonitor.')):
			app.display_status(mx('Message sent successfully.', 'emailSuccess'))
		else:
			app.display_error(mx('Message send failure. Check your setup.', 'emailFail'))
		app.endTask()


	def starttls_changed(self, iState):
		if not self._init and self._use_starttls.isChecked():
			self._use_tls.setChecked(False)


	def tls_changed(self, iState):
		if not self._init:
			if self._use_tls.isChecked():
				self._use_starttls.setChecked(False)
				self._smtp_port.setText('465')
			else:
				self._smtp_port.setText('587')


	def setup_changed(self, iSetup):
		c = self.get_setup()
		m = len(c['From']) and len(c['To']) and len(c['Server'])
		if c['Authentication']:
			self._user.setDisabled(False)
			self._password.setDisabled(False)
			m = m and len(c['User']) and len (c['Password'])
		else:
			self._user.setDisabled(True)
			self._password.setDisabled(True)

		self._test_button.setDisabled(not m)
		self._ok_button.setDisabled(not m)
