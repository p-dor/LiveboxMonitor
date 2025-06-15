### Livebox Monitor Connection dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang.LmLanguages import get_config_cnx_label as lx


# ################################ Livebox connection dialog ################################
class LiveboxCnxDialog(QtWidgets.QDialog):
	def __init__(self, url, parent=None):
		super().__init__(parent)
		self.resize(450, 150)

		warn_box = QtWidgets.QVBoxLayout()
		warn_box.setSpacing(4)
		w1_label = QtWidgets.QLabel(lx('Cannot connect to the Livebox.'), objectName='w1Label')
		w1_label.setFont(LmTools.BOLD_FONT)
		warn_box.addWidget(w1_label)
		w2_label = QtWidgets.QLabel(lx('It might be unreachable, in that case just wait.'), objectName='w2Label')
		warn_box.addWidget(w2_label)
		aW3Label = QtWidgets.QLabel(lx('Otherwise, try {0}, {1} or {2}.').format('http://livebox.home/', 'http://livebox/', 'http://192.168.1.1/'),
									objectName='w3Label')
		warn_box.addWidget(aW3Label)

		url_label = QtWidgets.QLabel(lx('Livebox URL'), objectName='urlLabel')
		self._url_edit = QtWidgets.QLineEdit(objectName='urlEdit')
		self._url_edit.textChanged.connect(self.text_changed)

		edit_grid = QtWidgets.QGridLayout()
		edit_grid.setSpacing(10)
		edit_grid.addWidget(url_label, 0, 0)
		edit_grid.addWidget(self._url_edit, 0, 1)

		button_bar = QtWidgets.QHBoxLayout()
		self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
		self._ok_button.clicked.connect(self.accept)
		self._ok_button.setDefault(True)
		cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
		cancel_button.clicked.connect(self.reject)
		button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.setSpacing(10)
		button_bar.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		vbox = QtWidgets.QVBoxLayout(self)
		vbox.setSpacing(15)
		vbox.addLayout(warn_box, 0)
		vbox.addLayout(edit_grid, 0)
		vbox.addLayout(button_bar, 1)

		self._url_edit.setFocus()

		LmConfig.set_tooltips(self, 'cnx')

		title = lx('Livebox connection')
		if len(LmConf.Profiles) > 1:
			title += ' [' + LmConf.CurrProfile['Name'] + ']'
		self.setWindowTitle(title)

		self._url_edit.setText(url)

		self.setModal(True)
		self.show()


	def text_changed(self, iText):
		self._ok_button.setDisabled(len(self.get_url()) == 0)


	def get_url(self):
		return self._url_edit.text()
