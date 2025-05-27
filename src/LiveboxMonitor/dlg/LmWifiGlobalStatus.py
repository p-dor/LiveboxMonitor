### Livebox Monitor Wifi Global Status dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.api.LmWifiApi import WifiKey, WifiStatus
from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, CenteredIconsDelegate
from LiveboxMonitor.lang.LmLanguages import get_wifi_global_label as lx


# ################################ Wifi Global Status dialog ################################
class WifiGlobalStatusDialog(QtWidgets.QDialog):
    def __init__(self, parent, status):
        super(WifiGlobalStatusDialog, self).__init__(parent)

        self._api = parent._api
        self._status = status
        self._status_table = LmTableWidget(objectName='statusTable')
        cols = {}
        icon_cols = []
        cols[0] = [lx('Interfaces'), 200, None]
        for i, s in enumerate(self._status, start=1):
            cols[i] = [s[WifiKey.ACCESS_POINT], 125, None]
            icon_cols.append(i)
        self._status_table.set_columns(cols)
        self._status_table.set_header_resize([0])
        self._status_table.set_standard_setup(parent, allow_sel=False, allow_sort=False)
        self._status_table.setItemDelegate(CenteredIconsDelegate(self, icon_cols))

        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self._status_table, 0)
        vbox.addLayout(hbox, 1)

        i = self.load_status()
        self.resize(550, 56 + LmConfig.dialog_height(i))

        LmConfig.set_tooltips(self, 'wglobal')

        self.setWindowTitle(lx('Wifi Global Status'))
        self.setModal(True)
        self.show()


    def load_status(self):
        i = 0
        i = self.add_status_line(lx('{} Enabled').format('Wifi'), WifiKey.ENABLE, i)
        i = self.add_status_line(lx('{} Active').format('Wifi'), WifiKey.STATUS, i)
        i = self.add_status_line(lx('Wifi Scheduler'), WifiKey.SCHEDULER, i)
        if self._api._intf.has_radio_band_2():
            i = self.add_status_line(lx('{} Enabled').format('Wifi 2.4GHz'), WifiKey.WIFI2_ENABLE, i)
            i = self.add_status_line(lx('{} Active').format('Wifi 2.4GHz'), WifiKey.WIFI2_STATUS, i)
            i = self.add_status_line(lx('{} VAP').format('Wifi 2.4GHz'), WifiKey.WIFI2_VAP, i)
        if self._api._intf.has_radio_band_5():
            i = self.add_status_line(lx('{} Enabled').format('Wifi 5GHz'), WifiKey.WIFI5_ENABLE, i)
            i = self.add_status_line(lx('{} Active').format('Wifi 5GHz'), WifiKey.WIFI5_STATUS, i)
            i = self.add_status_line(lx('{} VAP').format('Wifi 5GHz'), WifiKey.WIFI5_VAP, i)
        if self._api._intf.has_radio_band_6():
            i = self.add_status_line(lx('{} Enabled').format('Wifi 6GHz'), WifiKey.WIFI6_ENABLE, i)
            i = self.add_status_line(lx('{} Active').format('Wifi 6GHz'), WifiKey.WIFI6_STATUS, i)
            i = self.add_status_line(lx('{} VAP').format('Wifi 6GHz'), WifiKey.WIFI6_VAP, i)
        i = self.add_status_line(lx('{} VAP').format(lx('Guest 2.4GHz')), WifiKey.GUEST2_VAP, i)
        i = self.add_status_line(lx('{} VAP').format(lx('Guest 5GHz')), WifiKey.GUEST5_VAP, i)
        return i


    def add_status_line(self, title, key, index):
        self._status_table.insertRow(index)
        self._status_table.setItem(index, 0, QtWidgets.QTableWidgetItem(title))
        for i, s in enumerate(self._status, start=1):
            item = None
            match s.get(key):
                case WifiStatus.ENABLE:
                    item = QtWidgets.QTableWidgetItem()
                    item.setIcon(QtGui.QIcon(LmIcon.TickPixmap))
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, 'ON')
                case WifiStatus.DISABLE:
                    item = QtWidgets.QTableWidgetItem()
                    item.setIcon(QtGui.QIcon(LmIcon.CrossPixmap))
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, 'off')
                case WifiStatus.ERROR:
                    item = QtWidgets.QTableWidgetItem(lx('Error'))
                    item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                case WifiStatus.INACTIVE:
                    item = QtWidgets.QTableWidgetItem(lx('Inactive'))
                    item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                case WifiStatus.UNSIGNED:
                    item = QtWidgets.QTableWidgetItem(lx('Not signed'))
                    item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self._status_table.setItem(index, i, item)

        return index + 1
