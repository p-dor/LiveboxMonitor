### Livebox Monitor custom QTableWidget ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.dlg.LmExportTable import ExportTableDialog

from LiveboxMonitor.lang.LmLanguages import GetMainLabel as lx


# ################################ LmTableWidget class ################################
class LmTableWidget(QtWidgets.QTableWidget):
    def set_header_resize(self, stretch_headers):
        header = self.horizontalHeader()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        for i in stretch_headers:
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_header_tags(self, header_tags):
        model = self.horizontalHeader().model()
        for i in header_tags:
            model.setHeaderData(i, QtCore.Qt.Orientation.Horizontal, header_tags[i], QtCore.Qt.ItemDataRole.UserRole)

    def set_style(self):
        self.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
        self.setStyleSheet(LmConfig.LIST_STYLESHEET)
        self.setFont(LmConfig.LIST_LINE_FONT)

        header = self.horizontalHeader()
        header.setStyleSheet(LmConfig.LIST_HEADER_STYLESHEET)
        header.setFont(LmConfig.LIST_HEADER_FONT)
        header.setFixedHeight(LmConf.ListHeaderHeight)

        header = self.verticalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(LmConf.ListLineHeight)

    def mousePressEvent(self, event):
        # Ignore right click to prevent selection
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            return
        super().mousePressEvent(event)

    def set_context_menu(self):
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_table_context_menu)

    def show_table_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        export_action = menu.addAction(lx('Export...'))
        action = menu.exec(self.mapToGlobal(pos))
        if action == export_action:
            self.export_table()

    def export_table(self):
        d = ExportTableDialog(self, self)
        if d.exec():
            d.do_export_table()
