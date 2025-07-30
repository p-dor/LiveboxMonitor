### Livebox Monitor custom QTableWidget ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.dlg.LmExportTable import ExportTableDialog

from LiveboxMonitor.lang.LmLanguages import get_main_label as lx


# ################################ LmTableWidget class ################################
class LmTableWidget(QtWidgets.QTableWidget):
    # Standard column strech setup
    def set_header_resize(self, stretch_headers):
        header = self.horizontalHeader()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        for i in stretch_headers:
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)


    # Setup all columns. Dict of list, #1=Title/#2=Width (0 is hidden)/#3=Tooltip tag if any
    def set_columns(self, columns):
        self.setColumnCount(len(columns))
        model = self.horizontalHeader().model()

        for col in columns:
            col_setup = columns[col]
            self.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(col_setup[0]))
            if col_setup[1]:
                self.setColumnWidth(col, col_setup[1])
            else:
                self.setColumnHidden(col, True)
            if col_setup[2]:
                model.setHeaderData(col, QtCore.Qt.Orientation.Horizontal, col_setup[2], QtCore.Qt.ItemDataRole.UserRole)


    # Apply standard setup
    def set_standard_setup(self, app, allow_sel=True, allow_sort=True):
        self._app = app
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.verticalHeader().hide()
        if allow_sel:
            self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        else:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.setSortingEnabled(allow_sort)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.set_style()
        self.set_context_menu()


    # Apply standard style depending on platform
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


    # Ignore right click to prevent selection
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            return
        super().mousePressEvent(event)


    # Setup context menu
    def set_context_menu(self):
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_table_context_menu)


    # Display context menu
    def show_table_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        export_action = menu.addAction(lx("Export..."))
        action = menu.exec(self.mapToGlobal(pos))
        if action == export_action:
            self.export_table()


    # Export table's content to a file
    def export_table(self):
        d = ExportTableDialog(self, self._app, self)
        if d.exec():
            d.do_export_table()


### Sorting columns by numeric
class NumericSortItem(QtWidgets.QTableWidgetItem):
    def __lt__(self, other):
        x =  self.data(QtCore.Qt.ItemDataRole.UserRole)
        y = other.data(QtCore.Qt.ItemDataRole.UserRole)
        return (x or 0) < (y or 0)


### Drawing centered icons
class CenteredIconsDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent, column_list):
        super().__init__(parent)
        self._column_list = column_list

    def paint(self, painter, option, index):
        if index.column() in self._column_list:
            icon = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
            if icon is not None:
                icon.paint(painter, option.rect)
                return
        super().paint(painter, option, index)


### Drawing centered icons in QHeaderView
class CenteredIconHeaderView(QtWidgets.QHeaderView):
    def __init__(self, parent, column_list):
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self._column_list = column_list

    def paintSection(self, painter, rect, index):
        if index in self._column_list:
            # If icon, first draw the column's normally - ensure title is an empty string during drawing
            model = self.model()
            title = model.headerData(index, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)
            model.setHeaderData(index, QtCore.Qt.Orientation.Horizontal, "", QtCore.Qt.ItemDataRole.DisplayRole)
            painter.save()
            super().paintSection(painter, rect, index)
            painter.restore()
            model.setHeaderData(index, QtCore.Qt.Orientation.Horizontal, title, QtCore.Qt.ItemDataRole.DisplayRole)

            # Then draw the icon stored in DisplayRole on top
            icon = self.model().headerData(index, QtCore.Qt.Orientation.Horizontal, LmTools.ItemDataRole.IconRole)
            if icon is not None:
                icon.paint(painter, rect)
        else:
            super().paintSection(painter, rect, index)
