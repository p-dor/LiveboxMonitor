### Livebox Monitor release warning dialog ###

import webbrowser

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.lang.LmLanguages import get_release_warning_label as lx

from LiveboxMonitor.__init__ import __url__, __version__


# ################################ New release warning dialog ################################
class ReleaseWarningDialog(QtWidgets.QDialog):
	def __init__(self, new_release, parent=None):
		super(ReleaseWarningDialog, self).__init__(parent)
		self.resize(450, 150)

		warn_box = QtWidgets.QVBoxLayout()
		warn_box.setSpacing(4)
		new_release_label = QtWidgets.QLabel(lx('New release {0} has been published.').format(new_release), objectName='nreal')
		new_release_label.setFont(LmTools.BOLD_FONT)
		warn_box.addWidget(new_release_label)
		curr_release_label = QtWidgets.QLabel(lx('You are using release {0}.').format(__version__), objectName='creal')
		warn_box.addWidget(curr_release_label)
		download_url = QtWidgets.QLabel(__url__, objectName='downloadURL')
		download_url.setStyleSheet('QLabel { color : blue }')
		download_url.mousePressEvent = self.download_url_click
		warn_box.addWidget(download_url, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		button_bar = QtWidgets.QHBoxLayout()
		ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
		ok_button.clicked.connect(self.accept)
		ok_button.setDefault(True)
		cancel_button = QtWidgets.QPushButton(lx('Don\'t warn me again'), objectName='nowarning')
		cancel_button.clicked.connect(self.reject)
		button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.setSpacing(10)
		button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		vbox = QtWidgets.QVBoxLayout(self)
		vbox.setSpacing(15)
		vbox.addLayout(warn_box, 0)
		vbox.addLayout(button_bar, 1)

		LmConfig.SetToolTips(self, 'rwarn')

		self.setWindowTitle(lx('You are not using the latest release'))

		self.setModal(True)
		self.show()


	### Project's URL web button
	def download_url_click(self, event):
		webbrowser.open_new_tab(__url__)

