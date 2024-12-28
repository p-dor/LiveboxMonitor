### Livebox Monitor tools module ###

import sys
import functools
import re
import datetime, time 
import smtplib
import ssl

from enum import IntEnum
from dateutil import tz
from email.message import EmailMessage

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.lang import LmLanguages
from LiveboxMonitor.lang.LmLanguages import GetToolsLabel as lx


# ################################ VARS & DEFS ################################

# Debug verbosity
gVerbosity = 1

# Regular expressions - https://ihateregex.io/
MAC_RS = r'(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})'
IPv4_RS = r'(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}'
IPv6_RS = (r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|'
		   r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
		   r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
		   r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
		   r':((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
		   r'::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|'
		   r'1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.)'
		   r'{3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))')
PORTS_RS = (r'^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})$|'
			r'^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})-(6553[0-5]|'
			r'655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})$')
EMAIL_RS = r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'

# Useful objects
MAC_RE = re.compile(MAC_RS)
IPv4_RE = re.compile('^' + IPv4_RS + '$')
IPv6_RE = re.compile('^' + IPv6_RS + '$')
PORTS_RE = re.compile(PORTS_RS)
EMAIL_RE = re.compile(EMAIL_RS)
BOLD_FONT = QtGui.QFont()
BOLD_FONT.setBold(True)

# SMTP Timeout
SMTP_TIMEOUT = 5

# Value qualifiers
class ValQual(IntEnum):
	Default = 0
	Good = 1
	Warn = 2
	Error = 3



# ################################ Tools ################################

### Lambda function to output on stderr
Error = functools.partial(print, '###ERROR:', file = sys.stderr)


### Set verbosity
def SetVerbosity(iLevel):
	global gVerbosity
	gVerbosity = iLevel


### Get verbosity
def GetVerbosity():
	return gVerbosity


### Debug logging according to level
def LogDebug(iLevel, *iArgs):
	if gVerbosity >= iLevel:
		sys.stderr.write('###DEBUG-L' + str(iLevel) + ': ' + ' '.join(iArgs) + '\n')


### Display an error popup
def DisplayError(iErrorMsg, iParent = None):
	aMsgBox = QtWidgets.QMessageBox(iParent)
	aMsgBox.setWindowTitle(lx('Error'))
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
	aMsgBox.setText(iErrorMsg)
	aMsgBox.exec()


### Display a status popup
def DisplayStatus(iStatusMsg, iParent = None):
	aMsgBox = QtWidgets.QMessageBox(iParent)
	aMsgBox.setWindowTitle(lx('Status'))
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Information)
	aMsgBox.setText(iStatusMsg)
	aMsgBox.exec()


### Ask a question and return True if OK clicked
def AskQuestion(iQuestionMsg, iParent = None):
	aMsgBox = QtWidgets.QMessageBox(iParent)
	aMsgBox.setWindowTitle(lx('Please confirm'))
	aMsgBox.setIcon(QtWidgets.QMessageBox.Icon.Question)
	aMsgBox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
	aMsgBox.setText(iQuestionMsg)
	return aMsgBox.exec() == QtWidgets.QMessageBox.StandardButton.Ok


### Display an info text popup
def DisplayInfos(iTitle, iInfoMsg, iInfoDoc = None, iParent = None):
	aTextDialog = TextDialog(iParent)
	aTextDialog.display(iTitle, iInfoMsg, iInfoDoc)
	aTextDialog.exec()


### Set mouse cursor to busy - Stack mode
def MouseCursor_Busy():
	QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))


### Restore mouse cursor to previous state - Stack mode
def MouseCursor_Normal():
	QtWidgets.QApplication.restoreOverrideCursor()


### Force mouse cursor to busy
def MouseCursor_ForceBusy():
	QtWidgets.QApplication.changeOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))


### Force mouse cursor to normal arrow
def MouseCursor_ForceNormal():
	QtWidgets.QApplication.changeOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))


### Extract a valid MAC Addr from any string
def ExtractMacAddrFromString(iString):
	aMatch = re.search(MAC_RE, iString) 
	if (aMatch is None):
		return ''
	return aMatch.group(0)


### Check if valid MAC address
def IsMACAddr(iString):
	return re.fullmatch(MAC_RE, iString) is not None


### Check if valid IPv4 address
def IsIPv4(iString):
	return re.fullmatch(IPv4_RE, iString) is not None


### Check if valid IPv6 address
def IsIPv6(iString):
	return re.fullmatch(IPv6_RE, iString) is not None


### Check if valid TCP/UDP port or ports range
def isTcpUdpPort(iString):
	return re.fullmatch(PORTS_RE, iString) is not None


### Cleanup URL
def CleanURL(iURL):
	n = len(iURL)
	if n:
		if not iURL[n - 1] == '/':
			iURL += '/'
		if not iURL.startswith('http://') and not iURL.startswith('https://'):
			iURL = 'http://' + iURL
	return iURL


### Collect error descriptions from Livebox replies
def GetErrorsFromLiveboxReply(iReply):
	d = ''
	if iReply is not None:
		aErrors = iReply.get('errors')
		if (aErrors is not None) and (type(aErrors).__name__ == 'list'):
			for e in aErrors:
				aDesc = e.get('description', '')
				aInfo = e.get('info', '')
				if len(aDesc):
					if len(aInfo):
						d += aDesc + ' -> ' + aInfo + '.\n'
					else:
						d += aDesc + '.\n'
				elif len(aInfo):
					d += aInfo + '.\n'

	return d


### Determine device IPv4 address info from IPv4 list, return the struct, none if nothing found
def DetermineIP(iDevice):
	if iDevice is not None:
		# Retrieve the list
		aIPv4List = iDevice.get('IPv4Address', [])

		# If only one, return it
		if len(aIPv4List) == 1:
			return aIPv4List[0]

		# Retrieve the reference IP address, but it can be an IPv6
		aRefIP = iDevice.get('IPAddress')
		if aRefIP is not None:
			if not IsIPv4(aRefIP):
				aRefIP = None

		# If there is no ref, return the first reachable address, otherwise the first
		if aRefIP is None:
			for i in aIPv4List:
				if i.get('Status', '') == 'reachable':
					return i
			if len(aIPv4List) > 1:
				return aIPv4List[0]

		# If we have a ref, search for it in the list
		else:
			for i in aIPv4List:
				if aRefIP == i.get('Address', ''):
					return i

			# If nothing found, build artificially a struct
			i = []
			i['Address'] = aRefIP
			i['Status'] = ''
			i['Reserved'] = False
			return i

	return None


### Send an email, returns true if successful
def SendEmail(iEmailSetup, iSubject, iMessage):
	# Create a text/plain message
	m = EmailMessage()
	m['From'] = iEmailSetup['From']
	m['To'] = iEmailSetup['To']
	m['Subject'] = iEmailSetup['Prefix'] + iSubject

	# Message body
	try:
		m.set_content(iMessage)
	except BaseException as e:
		Error('Cannot set email content. Error: {}'.format(e))
		return False

	# Create a session
	s = None
	try:
		if iEmailSetup['TLS']:
			s = smtplib.SMTP(iEmailSetup['Server'], iEmailSetup['Port'], timeout = SMTP_TIMEOUT)
			s.starttls(context = ssl.create_default_context())
		elif iEmailSetup['SSL']:
			s = smtplib.SMTP_SSL(iEmailSetup['Server'], iEmailSetup['Port'], timeout = SMTP_TIMEOUT, context = ssl.create_default_context())
		else:
			s = smtplib.SMTP(iEmailSetup['Server'], iEmailSetup['Port'], timeout = SMTP_TIMEOUT)
	except BaseException as e:
		Error('Cannot setup email session. Error: {}'.format(e))
		if s is not None:
			s.quit()
		return False

	# Authenticate if necessary
	if iEmailSetup['Authentication']:
		try:
			s.login(iEmailSetup['User'], iEmailSetup['Password'])
		except BaseException as e:
			Error('Authentication to SMTP server failed. Error: {}'.format(e))
			s.quit()
			return False

	# Send the message
	try:
		s.send_message(m)
	except BaseException as e:
		Error('Cannot send email. Error: {}'.format(e))
		s.quit()
		return False

	s.quit()
	return True


### Async email sending task
class AsyncEmail(QtCore.QRunnable):
	def __init__(self, iEmailSetup, iSubject, iMessage):
		super().__init__()
		self.emailSetup = iEmailSetup
		self.subject = iSubject
		self.message = iMessage

	def run(self):
		if not SendEmail(self.emailSetup, self.subject, self.message):
			Error('Email send failure. Check your email setup.')


### Send an email asynchronously
def SendEmailAsync(iEmailSetup, iSubject, iMessage):
	try:
		if not QtCore.QThreadPool.globalInstance().tryStart(AsyncEmail(iEmailSetup, iSubject, iMessage)):
			Error('Cannot send email. No free thread in the pool.')
	except BaseException as e:
		Error('Cannot send email. Error: {}'.format(e))



# ################################ Formatting Tools ################################

### Format bytes
def FmtBytes(iBytes, iSuffix = 'B'):
	for aUnit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
		if abs(iBytes) < 1024.0:
			return f'{iBytes:3.1f} {aUnit}{iSuffix}'
		iBytes /= 1024.0
	return f'{iBytes:.1f} Y{iSuffix}'


### Format boolean
def FmtBool(iBool):
	if iBool is None:
		return ''
	if iBool:
		return lx('True')
	return lx('False')


### Format integer
def FmtInt(iInt):
	if iInt is None:
		return ''
	return str(iInt)


### Format a string with capitalize
def FmtStrCapitalize(iString):
	if iString is None:
		return ''
	return iString.capitalize()


### Format a string in upper string
def FmtStrUpper(iString):
	if iString is None:
		return ''
	return iString.upper()


### Format time
def FmtTime(iSeconds, iNoZero = False):
	if iSeconds is None:
		return ''

	aDays = iSeconds // (24 * 3600)
	n = iSeconds % (24 * 3600)
	aHours = n // 3600
	n %= 3600
	aMinutes = n // 60
	aSeconds = n % 60

	if iNoZero:
		if aDays:
			return '{:02d}d {:02d}h {:02d}m {:02d}s'.format(aDays, aHours, aMinutes, aSeconds)
		elif aHours:
			return '{:02d}h {:02d}m {:02d}s'.format(aHours, aMinutes, aSeconds)
		elif aMinutes:
			return '{:02d}m {:02d}s'.format(aMinutes, aSeconds)
		elif aSeconds:
			return '{:02d}s'.format(aSeconds)
		else:
			return ''
	else:
		return '{:02d}d {:02d}h {:02d}m {:02d}s'.format(aDays, aHours, aMinutes, aSeconds)


### Format Livebox timestamps
def FmtLiveboxTimestamp(iTimestamp):
	if iTimestamp is None:
		return ''
	aDateTime = LiveboxTimestamp(iTimestamp)
	if aDateTime is None:
		return ''
	return aDateTime.strftime('%Y-%m-%d %H:%M:%S')


### Parse Livebox timestamp (UTC time)
def LiveboxTimestamp(iTimestamp):
	try:
		return datetime.datetime.fromisoformat(iTimestamp.replace('Z','+00:00')).replace(tzinfo = tz.tzutc()).astimezone(tz.tzlocal())
	except:
		return None



# ############# Column sort classes #############

### Sorting columns by numeric
class NumericSortItem(QtWidgets.QTableWidgetItem):
	def __lt__(self, iOther):
		x =  self.data(QtCore.Qt.ItemDataRole.UserRole)
		if x is None:
			x = 0
		y = iOther.data(QtCore.Qt.ItemDataRole.UserRole)
		if y is None:
			y = 0
		return x < y


### Drawing centered icons
class CenteredIconsDelegate(QtWidgets.QStyledItemDelegate):
	def __init__(self, iParent, iColumnList):
		super(CenteredIconsDelegate, self).__init__(iParent)
		self._columnList = iColumnList

	def paint(self, iPainter, iOption, iIndex):
		if iIndex.column() in self._columnList:
			aIcon = iIndex.data(QtCore.Qt.ItemDataRole.DecorationRole)
			if aIcon is not None:
				aIcon.paint(iPainter, iOption.rect)
		else:
			super(CenteredIconsDelegate, self).paint(iPainter, iOption, iIndex)


### Drawing centered icons in QHeaderView
class CenteredIconHeaderView(QtWidgets.QHeaderView):
	def __init__(self, iParent, iColumnList):
		super(CenteredIconHeaderView, self).__init__(QtCore.Qt.Orientation.Horizontal, iParent)
		self._columnList = iColumnList

	def paintSection(self, iPainter, iRect, iIndex):
		if iIndex in self._columnList:
			# If icon, first draw the column's normally - ensure title is an empty string
			iPainter.save()
			super(CenteredIconHeaderView, self).paintSection(iPainter, iRect, iIndex)
			iPainter.restore()

			# Then draw the icon stored in DisplayRole on top
			aIcon = self.model().headerData(iIndex, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)
			if aIcon is not None:
				aIcon.paint(iPainter, iRect)
		else:
			super(CenteredIconHeaderView, self).paintSection(iPainter, iRect, iIndex)



# ############# Display text dialog #############
class TextDialog(QtWidgets.QDialog):
	def __init__(self, iParent = None):
		super(TextDialog, self).__init__(iParent)

		aVbox = QtWidgets.QVBoxLayout(self)

		self._textBox = QtWidgets.QTextEdit()
		self._OKButton = QtWidgets.QPushButton(lx('OK'))
		self._OKButton.clicked.connect(self.accept)
		self._OKButton.setDefault(True)

		aVbox.addWidget(self._textBox, 1)
		aVbox.addWidget(self._OKButton, 0)
	

	def display(self, iTitle, iText, iDoc = None):
		self.setWindowTitle(iTitle)
		if iDoc is None:
			aTextDoc = QtGui.QTextDocument(iText)
			aFont = QtGui.QFont('Courier New', 9)
			aTextDoc.setDefaultFont(aFont)
			self._textBox.setDocument(aTextDoc)
		else:
			self._textBox.setDocument(iDoc)
		self.resize(800, 500)
		self.setModal(True)
		self.show()



# ############# Color picker button #############
# Custom QtWidget to show a chosen color.
# Left-clicking the button shows the color-chooser, while
# right-clicking resets the color to None (no-color).

class ColorButton(QtWidgets.QPushButton):
	_colorChanged = QtCore.pyqtSignal(object)

	def __init__(self, *args, iColor = None, **kwargs):
		super(ColorButton, self).__init__(*args, **kwargs)

		self._color = None
		self._default = iColor
		self.pressed.connect(self.onColorPicker)

		# Set the initial/default state.
		self.setColor(self._default)


	def setColor(self, iColor):
		if iColor != self._color:
			self._color = iColor
			self._colorChanged.emit(iColor)

		if self._color:
			self.setStyleSheet('QPushButton { background-color:%s }' % self._color)
		else:
			self.setStyleSheet('')


	def getColor(self):
		return self._color


	def onColorPicker(self):
		# Show color-picker dialog to select color.
		# Qt will use the native dialog by default.

		aDialog = QtWidgets.QColorDialog()
		if self._color:
			aDialog.setCurrentColor(QtGui.QColor(self._color))

		if aDialog.exec():
			self.setColor(aDialog.currentColor().name())


	def mousePressEvent(self, iEvent):
		if iEvent.button() == QtCore.Qt.MouseButton.RightButton:
			self.setColor(self._default)

		return super(ColorButton, self).mousePressEvent(iEvent)



# ############# Multi lines edit #############
# Custom QtWidget to type a text on multilines without carriage return.
class MultiLinesEdit(QtWidgets.QPlainTextEdit):
	### Prevent carriage return, e.g. in plain text fields
	def keyPressEvent(self, iEvent):
		if iEvent.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
			return
		super().keyPressEvent(iEvent)


	### Set the maximum height to a given nb of lines
	def setLineNumber(self, iLines):
		f = QtGui.QFontMetrics(self.font())
		m = self.contentsMargins()
		d = (int(self.document().documentMargin()) + 1) * 2

		self.setFixedHeight((iLines * f.lineSpacing()) + m.top() + m.bottom() + d)
