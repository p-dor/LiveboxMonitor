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
from email.utils import formatdate

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.lang import LmLanguages
from LiveboxMonitor.lang.LmLanguages import get_tools_label as lx


# ################################ VARS & DEFS ################################

# Debug verbosity
verbosity = 1

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
IPv6Pfix_RS = (r'(?:(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|(?:[0-9A-Fa-f]{1,4}:){1,7}:|(?:[0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}|'
               r'(?:[0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|(?:[0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|'
               r'(?:[0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|(?:[0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|'
               r'[0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6})|:(?:(:[0-9A-Fa-f]{1,4}){1,7}|:)|fe80:(:[0-9A-Fa-f]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
               r'::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|'
               r'([0-9A-Fa-f]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
               r'(?:\/(?:12[0-8]|1[0-1][0-9]|[1-9][0-9]|[0-9]))?')
PORTS_RS = (r'^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})$|'
            r'^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})-(6553[0-5]|'
            r'655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})$')
EMAIL_RS = r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'

# Useful objects
MAC_RE = re.compile(MAC_RS)
IPv4_RE = re.compile('^' + IPv4_RS + '$')
IPv6_RE = re.compile('^' + IPv6_RS + '$')
IPv6Pfix_RE = re.compile('^' + IPv6Pfix_RS + '$')
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

# Table item data roles
class ItemDataRole(IntEnum):
    ExportRole = QtCore.Qt.ItemDataRole.UserRole + 1
    IconRole = QtCore.Qt.ItemDataRole.UserRole + 2


# ################################ Tools ################################

### Set verbosity
def set_verbosity(level):
    global verbosity
    verbosity = level


### Get verbosity
def get_verbosity():
    return verbosity


### Debug logging according to level
def log_debug(level, *args):
    if verbosity >= level:
        sys.stderr.write('###DEBUG-L' + str(level) + ': ' + ' '.join(args) + '\n')


### Output error on stderr
def error(*args, **kwargs):
    print('###ERROR:', *args, file=sys.stderr, **kwargs)


### Display an error popup
def display_error(error_msg, parent=None):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(lx('Error'))
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    msg_box.setText(error_msg)
    msg_box.exec()


### Display a status popup
def display_status(status_msg, parent=None):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(lx('Status'))
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
    msg_box.setText(status_msg)
    msg_box.exec()


### Ask a question and return True if OK clicked
def ask_question(question_msg, parent=None):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(lx('Please confirm'))
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Question)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
    msg_box.setText(question_msg)
    return msg_box.exec() == QtWidgets.QMessageBox.StandardButton.Ok


### Display an info text popup
def display_infos(title, info_msg, info_doc=None, parent=None):
    text_dialog = TextDialog(parent)
    text_dialog.display(title, info_msg, info_doc)
    text_dialog.exec()


### Set mouse cursor to busy - Stack mode
def mouse_cursor_busy():
    QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))


### Restore mouse cursor to previous state - Stack mode
def mouse_cursor_normal():
    QtWidgets.QApplication.restoreOverrideCursor()


### Force mouse cursor to busy
def mouse_cursor_force_busy():
    QtWidgets.QApplication.changeOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))


### Force mouse cursor to normal arrow
def mouse_cursor_force_normal():
    QtWidgets.QApplication.changeOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))


### Extract a valid MAC Addr from any string
def extract_mac_addr_from_string(string):
    match = re.search(MAC_RE, string) 
    if match is None:
        return ''
    return match.group(0)


### Check if valid MAC address
def is_mac_addr(string):
    return re.fullmatch(MAC_RE, string) is not None


### Check if valid IPv4 address
def is_ipv4(string):
    return re.fullmatch(IPv4_RE, string) is not None


### Check if valid IPv6 address
def is_ipv6(string):
    return re.fullmatch(IPv6_RE, string) is not None


### Check if valid IPv6 address or IPv6 prefix
def is_ipv6_pfix(string):
    return re.fullmatch(IPv6Pfix_RE, string) is not None


### Check if valid TCP/UDP port or ports range
def is_tcp_udp_port(string):
    return re.fullmatch(PORTS_RE, string) is not None


### Cleanup URL
def clean_url(url):
    n = len(url)
    if n:
        if not url[n - 1] == '/':
            url += '/'
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
    return url


### Collect error descriptions from Livebox replies
def get_errors_from_livebox_reply(reply):
    d = ''
    if reply is not None:
        errors = reply.get('errors')
        if isinstance(errors, list):
            for e in errors:
                desc = e.get('description', '')
                info = e.get('info', '')
                if len(desc):
                    if len(info):
                        d += desc + ' -> ' + info + '.\n'
                    else:
                        d += desc + '.\n'
                elif len(info):
                    d += info + '.\n'

    return d


### Determine device IPv4 address info from IPv4 list, return the struct, none if nothing found
def determine_ip(device):
    if device is not None:
        # Retrieve the list
        ipv4_list = device.get('IPv4Address', [])

        # If only one, return it
        if len(ipv4_list) == 1:
            return ipv4_list[0]

        # Retrieve the reference IP address, but it can be an IPv6
        ref_ip = device.get('IPAddress')
        if ref_ip is not None:
            if not is_ipv4(ref_ip):
                ref_ip = None

        # If there is no ref, return the first reachable address, otherwise the first
        if ref_ip is None:
            for i in ipv4_list:
                if i.get('Status', '') == 'reachable':
                    return i
            if len(ipv4_list) > 1:
                return ipv4_list[0]

        # If we have a ref, search for it in the list
        else:
            for i in ipv4_list:
                if ref_ip == i.get('Address', ''):
                    return i

            # If nothing found, build artificially a struct
            i = {}
            i['Address'] = ref_ip
            i['Status'] = ''
            i['Reserved'] = False
            return i

    return None


### Send an email, returns true if successful
def send_email(email_setup, subject, message):
    # Create a text/plain message
    m = EmailMessage()
    m['From'] = email_setup['From']
    m['To'] = email_setup['To']
    m['Date'] = formatdate(localtime=True)
    m['Subject'] = email_setup['Prefix'] + subject

    # Message body
    try:
        m.set_content(message)
    except BaseException as e:
        error(f'Cannot set email content. Error: {e}')
        return False

    # Create a session
    s = None
    try:
        if email_setup['TLS']:
            s = smtplib.SMTP(email_setup['Server'], email_setup['Port'], timeout=SMTP_TIMEOUT)
            s.starttls(context=ssl.create_default_context())
        elif email_setup['SSL']:
            s = smtplib.SMTP_SSL(email_setup['Server'], email_setup['Port'], timeout=SMTP_TIMEOUT, context=ssl.create_default_context())
        else:
            s = smtplib.SMTP(email_setup['Server'], email_setup['Port'], timeout=SMTP_TIMEOUT)
    except BaseException as e:
        error(f'Cannot setup email session. Error: {e}')
        if s is not None:
            try:
                s.quit()
            except Exception:
                pass
        return False

    # Authenticate if necessary
    if email_setup['Authentication']:
        try:
            s.login(email_setup['User'], email_setup['Password'])
        except BaseException as e:
            error(f'Authentication to SMTP server failed. Error: {e}')
            try:
                s.quit()
            except Exception:
                pass
            return False

    # Send the message
    try:
        s.send_message(m)
    except BaseException as e:
        error(f'Cannot send email. Error: {e}')
        try:
            s.quit()
        except Exception:
            pass
        return False

    s.quit()
    return True


### Async email sending task
class AsyncEmail(QtCore.QRunnable):
    def __init__(self, email_setup, subject, message):
        super().__init__()
        self._email_setup = email_setup
        self._subject = subject
        self._message = message

    def run(self):
        if not send_email(self._email_setup, self._subject, self._message):
            error('Email send failure. Check your email setup.')


### Send an email asynchronously
def async_send_email(email_setup, subject, message):
    try:
        if not QtCore.QThreadPool.globalInstance().tryStart(AsyncEmail(email_setup, subject, message)):
            error('Cannot send email. No free thread in the pool.')
    except BaseException as e:
        error(f'Cannot send email. Error: {e}')



# ################################ Formatting Tools ################################

### Format number of bytes
def fmt_bytes(bytes_nb, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(bytes_nb) < 1024.0:
            return f'{bytes_nb:3.1f} {unit}{suffix}'
        bytes_nb /= 1024.0
    return f'{bytes_nb:.1f} Y{suffix}'


### Format boolean value
def fmt_bool(bool_val):
    if bool_val is None:
        return ''
    if bool_val:
        return lx('True')
    return lx('False')


### Format integer value
def fmt_int(int_val):
    if int_val is None:
        return ''
    return str(int_val)


### Format a string with capitalize
def fmt_str_capitalize(string):
    if string is None:
        return ''
    return string.capitalize()


### Format a string in upper string
def fmt_str_upper(string):
    if string is None:
        return ''
    return string.upper()


### Format time
def fmt_time(seconds, no_zero=False):
    if seconds is None:
        return ''

    days = seconds // (24 * 3600)
    n = seconds % (24 * 3600)
    hours = n // 3600
    n %= 3600
    minutes = n // 60
    seconds = n % 60

    if no_zero:
        if days:
            return f'{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s'
        elif hours:
            return f'{hours:02d}h {minutes:02d}m {seconds:02d}s'
        elif minutes:
            return f'{minutes:02d}m {seconds:02d}s'
        elif seconds:
            return f'{seconds:02d}s'
        else:
            return ''
    else:
        return f'{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s'


### Format Livebox timestamps
def fmt_livebox_timestamp(timestamp, utc=True):
    if timestamp is None:
        return ''
    date_time = livebox_timestamp(timestamp, utc)
    if date_time is None:
        return ''
    return date_time.strftime('%Y-%m-%d %H:%M:%S')


### Parse Livebox timestamp (UTC time by default)
def livebox_timestamp(timestamp, utc=True):
    try:
        if utc:
            return datetime.datetime.fromisoformat(timestamp.replace('Z','+00:00')).replace(tzinfo = tz.tzutc()).astimezone(tz.tzlocal())
        else:
            return datetime.datetime.fromisoformat(timestamp.replace('Z','+00:00'))
    except:
        return None



# ############# Display text dialog #############
class TextDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TextDialog, self).__init__(parent)

        vbox = QtWidgets.QVBoxLayout(self)

        self._text_box = QtWidgets.QTextEdit()
        self._ok_button = QtWidgets.QPushButton(lx('OK'))
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setDefault(True)

        vbox.addWidget(self._text_box, 1)
        vbox.addWidget(self._ok_button, 0)
    

    def display(self, title, text, doc=None):
        self.setWindowTitle(title)
        if doc is None:
            text_doc = QtGui.QTextDocument(text)
            font = QtGui.QFont('Courier New', 9)
            text_doc.setDefaultFont(font)
            self._text_box.setDocument(text_doc)
        else:
            self._text_box.setDocument(doc)
        self.resize(800, 500)
        self.setModal(True)
        self.show()



# ############# Color picker button #############
# Custom QtWidget to show a chosen color.
# Left-clicking the button shows the color-chooser, while
# right-clicking resets the color to None (no-color).

class ColorButton(QtWidgets.QPushButton):
    _color_changed = QtCore.pyqtSignal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self.pressed.connect(self.on_color_picker)

        # Set the initial/default state.
        self.set_color(self._default)


    def set_color(self, color):
        if color != self._color:
            self._color = color
            self._color_changed.emit(color)

        if self._color:
            self.setStyleSheet('QPushButton { background-color:%s }' % self._color)
        else:
            self.setStyleSheet('')


    def get_color(self):
        return self._color


    def on_color_picker(self):
        # Show color-picker dialog to select color.
        # Qt will use the native dialog by default.

        dialog = QtWidgets.QColorDialog()
        if self._color:
            dialog.setCurrentColor(QtGui.QColor(self._color))

        if dialog.exec():
            self.set_color(dialog.currentColor().name())


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.set_color(self._default)

        return super(ColorButton, self).mousePressEvent(event)



# ############# Multi lines edit #############
# Custom QtWidget to type a text on multilines without carriage return.
class MultiLinesEdit(QtWidgets.QPlainTextEdit):
    ### Prevent carriage return, e.g. in plain text fields
    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            return
        super().keyPressEvent(event)


    ### Set the maximum height to a given nb of lines
    def setLineNumber(self, lines):
        f = QtGui.QFontMetrics(self.font())
        m = self.contentsMargins()
        d = (int(self.document().documentMargin()) + 1) * 2

        self.setFixedHeight((lines * f.lineSpacing()) + m.top() + m.bottom() + d)
