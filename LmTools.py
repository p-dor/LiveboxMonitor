### Livebox Monitor tools module ###

import sys
import functools
import re
import datetime
import time

from enum import IntEnum
from dateutil import tz

from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWidgets


# ################################ VARS & DEFS ################################

# Debug verbosity
gVerbosity = 0

# Useful objects
MAC_RE = re.compile('(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})')
IPv4_RE = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
BOLD_FONT = QtGui.QFont()
BOLD_FONT.setBold(True)

# Value qualifiers
class ValQual(IntEnum):
	Default = 0
	Good = 1
	Warn = 2
	Error = 3



# ################################ Tools ################################

# Lambda function to output on stderr
Error = functools.partial(print, file = sys.stderr)


# Debug logging according to level
def LogDebug(iLevel, *iArgs):
	if gVerbosity >= iLevel:
		sys.stderr.write('###DEBUG-L' + str(iLevel) + ': ' + ' '.join(iArgs) + '\n')


# Display an error popup
def DisplayError(iErrorMsg):
	aMsgBox = QtWidgets.QMessageBox()
	aMsgBox.setWindowTitle('Error')
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
	aMsgBox.setText(iErrorMsg)
	aMsgBox.exec()


# Display a status popup
def DisplayStatus(iStatusMsg):
	aMsgBox = QtWidgets.QMessageBox()
	aMsgBox.setWindowTitle('Status')
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Information)
	aMsgBox.setText(iStatusMsg)
	aMsgBox.exec()


# Ask a question and return True if OK clicked
def AskQuestion(iQuestionMsg):
	aMsgBox = QtWidgets.QMessageBox()
	aMsgBox.setWindowTitle('Please confirm')
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Question)
	aMsgBox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
	aMsgBox.setText(iQuestionMsg)
	return aMsgBox.exec() == QtWidgets.QMessageBox.StandardButton.Ok


# Display an info text popup
def DisplayInfos(iTitle, iInfoMsg, iInfoDoc = None):
	aTextDialog = TextDialog()
	aTextDialog.display(iTitle, iInfoMsg, iInfoDoc)
	aTextDialog.exec()


# Set mouse cursor to busy
def MouseCursor_Busy():
	QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))


# Set mouse cursor to busy
def MouseCursor_Normal():
	QtWidgets.QApplication.restoreOverrideCursor()


# Extract a valid MAC Addr from any string
def ExtractMacAddrFromString(iString):
	aMatch = re.search(MAC_RE, iString) 
	if (aMatch is None):
		return ''
	return aMatch.group(0)


# Check if valid IPv4 address
def isIPv4(iString):
	return re.fullmatch(IPv4_RE, iString) is not None



# ################################ Formatting Tools ################################

# Format bytes
def FmtBytes(iBytes, iSuffix = 'B'):
	for aUnit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
		if abs(iBytes) < 1024.0:
			return f'{iBytes:3.1f} {aUnit}{iSuffix}'
		iBytes /= 1024.0
	return f'{iBytes:.1f} Y{iSuffix}'


# Format boolean
def FmtBool(iBool):
	if iBool is None:
		return ''
	if iBool:
		return 'True'
	return 'False'


# Format integer
def FmtInt(iInt):
	if iInt is None:
		return ''
	return str(iInt)


# Format a string with capitalize
def FmtStrCapitalize(iString):
	if iString is None:
		return ''
	return iString.capitalize()


# Format a string in upper string
def FmtStrUpper(iString):
	if iString is None:
		return ''
	return iString.upper()


# Format time
def FmtTime(iSeconds):
	if iSeconds is None:
		return ''

	aDay = iSeconds // (24 * 3600)
	n = iSeconds % (24 * 3600)
	aHour = n // 3600
	n %= 3600
	aMinutes = n // 60
	aSeconds = n % 60

	return '{:02d}d {:02d}h {:02d}m {:02d}s'.format(aDay, aHour, aMinutes, aSeconds)


# Format Livebox timestamps
def FmtLiveboxTimestamp(iTimestamp):
	if iTimestamp is None:
		return ''
	aDateTime = LiveboxTimestamp(iTimestamp)
	if aDateTime is None:
		return ''
	return aDateTime.strftime('%Y-%m-%d %H:%M:%S')


# Parse Livebox timestamp (UTC time)
def LiveboxTimestamp(iTimestamp):
	try:
		return datetime.datetime.fromisoformat(iTimestamp.replace('Z','+00:00')).replace(tzinfo = tz.tzutc()).astimezone(tz.tzlocal())
	except:
		return None



# ############# Display text dialog #############
class TextDialog(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(TextDialog, self).__init__(parent)

		aVbox = QtWidgets.QVBoxLayout(self)

		self._textBox = QtWidgets.QTextEdit()
		self._OKButton = QtWidgets.QPushButton('OK', self)
		self._OKButton.clicked.connect(self.accept)
		self._OKButton.setDefault(True)

		aVbox.addWidget(self._textBox, 1)
		aVbox.addWidget(self._OKButton, 0)
	

	def display(self, iTitle, iText, iDoc = None):
		self.setWindowTitle(iTitle)
		if iDoc is None:
			aTextDoc = QtGui.QTextDocument(iText)
			aFont = QtGui.QFont('Courier', 9)
			aTextDoc.setDefaultFont(aFont)
			self._textBox.setDocument(aTextDoc)
		else:
			self._textBox.setDocument(iDoc)
		self.setGeometry(200, 200, 800, 500)
		self.setModal(True)
		self.show()
