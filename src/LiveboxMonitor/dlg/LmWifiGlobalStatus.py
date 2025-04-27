### Livebox Monitor Wifi Global Status dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.api.LmWifiApi import WifiKey, WifiStatus
from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.lang.LmLanguages import GetWifiGlobalDialogLabel as lx


# ################################ Wifi Global Status dialog ################################
class WifiGlobalStatusDialog(QtWidgets.QDialog):
    def __init__(self, parent, status, livebox_model):
        super(WifiGlobalStatusDialog, self).__init__(parent)

        self._status = status
        self._status_table = QtWidgets.QTableWidget(objectName='statusTable')
        self._status_table.setColumnCount(1 + len(status))
        headers = []
        headers.append(lx('Interfaces'))
        for s in self._status:
            headers.append(s[WifiKey.ACCESS_POINT])
        self._status_table.setHorizontalHeaderLabels((*headers,))
        table_header = self._status_table.horizontalHeader()
        table_header.setSectionsMovable(False)
        table_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        table_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self._status_table.setColumnWidth(0, 200)
        i = 1
        while i <= len(self._status):
            self._status_table.setColumnWidth(i, 125)
            i += 1
        self._status_table.verticalHeader().hide()
        self._status_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self._status_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        LmConfig.SetTableStyle(self._status_table)

        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self._status_table, 0)
        vbox.addLayout(hbox, 1)

        i = self.load_status(livebox_model)
        self.resize(550, 56 + LmConfig.DialogHeight(i))

        LmConfig.SetToolTips(self, 'wglobal')

        self.setWindowTitle(lx('Wifi Global Status'))
        self.setModal(True)
        self.show()


    def load_status(self, livebox_model):
        i = 0
        i = self.add_status_line(lx('{} Enabled').format('Wifi'), WifiKey.ENABLE, i)
        i = self.add_status_line(lx('{} Active').format('Wifi'), WifiKey.STATUS, i)
        i = self.add_status_line(lx('Wifi Scheduler'), WifiKey.SCHEDULER, i)
        i = self.add_status_line(lx('{} Enabled').format('Wifi 2.4GHz'), WifiKey.WIFI2_ENABLE, i)
        i = self.add_status_line(lx('{} Active').format('Wifi 2.4GHz'), WifiKey.WIFI2_STATUS, i)
        i = self.add_status_line(lx('{} VAP').format('Wifi 2.4GHz'), WifiKey.WIFI2_VAP, i)
        i = self.add_status_line(lx('{} Enabled').format('Wifi 5GHz'), WifiKey.WIFI5_ENABLE, i)
        i = self.add_status_line(lx('{} Active').format('Wifi 5GHz'), WifiKey.WIFI5_STATUS, i)
        i = self.add_status_line(lx('{} VAP').format('Wifi 5GHz'), WifiKey.WIFI5_VAP, i)
        if livebox_model >= 6:
            i = self.add_status_line(lx('{} Enabled').format('Wifi 6GHz'), WifiKey.WIFI6_ENABLE, i)
            i = self.add_status_line(lx('{} Active').format('Wifi 6GHz'), WifiKey.WIFI6_STATUS, i)
            i = self.add_status_line(lx('{} VAP').format('Wifi 6GHz'), WifiKey.WIFI6_VAP, i)
        i = self.add_status_line(lx('{} VAP').format(lx('Guest 2.4GHz')), WifiKey.GUEST2_VAP, i)
        i = self.add_status_line(lx('{} VAP').format(lx('Guest 5GHz')), WifiKey.GUEST5_VAP, i)
        return i


    def add_status_line(self, title, key, index):
        self._status_table.insertRow(index)

        self._status_table.setItem(index, 0, QtWidgets.QTableWidgetItem(title))

        i = 1
        for s in self._status:
            status = s.get(key)
            if status == WifiStatus.ENABLE:
                icon_item = QtWidgets.QLabel()
                icon_item.setPixmap(LmIcon.TickPixmap)
                icon_item.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self._status_table.setCellWidget(index, i, icon_item)
            elif status == WifiStatus.DISABLE:
                icon_item = QtWidgets.QLabel()
                icon_item.setPixmap(LmIcon.CrossPixmap)
                icon_item.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self._status_table.setCellWidget(index, i, icon_item)
            elif status == WifiStatus.ERROR:
                item = QtWidgets.QTableWidgetItem(lx('Error'))
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self._status_table.setItem(index, i, item)
            elif status == WifiStatus.INACTIVE:
                item = QtWidgets.QTableWidgetItem(lx('Inactive'))
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self._status_table.setItem(index, i, item)
            elif status == WifiStatus.UNSIGNED:
                item = QtWidgets.QTableWidgetItem(lx('Not signed'))
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self._status_table.setItem(index, i, item)
            i += 1

        return index + 1
