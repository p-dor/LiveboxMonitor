### Livebox Monitor graph tab module ###

import os
import time
import csv
from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.dlg.LmAddGraph import AddGraphDialog, GraphType
from LiveboxMonitor.lang.LmLanguages import get_graph_label as lx, get_graph_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'graphTab'

# Config default
DCFG_WINDOW = 24    # 1 day
DCFG_BACKGROUND_COLOR = '#000000'       # (0, 0, 0)
DCFG_STAT_FREQUENCY = 30    # In case the service doesn't work, 30 secs is the normal value

# Constants
UNIT_DIVIDER = 1048576      # To convert bytes in megabytes
WIND_UPDATE_FREQ = 60000    # 1mn - frequency of the window update task, cutting old values

# List columns
class GraphCol(IntEnum):
    Key = 0     # type constant + '_' + ID
    Name = 1
    Type = 2
    ID = 3
    Color = 4


# ################################ LmGraph class ################################
class LmGraph:

    ### Create Graph tab
    def create_graph_tab(self):
        self._graph_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Graph list box
        graph_list_layout = QtWidgets.QVBoxLayout()
        graph_list_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        graph_list_layout.setSpacing(5)

        select_label = QtWidgets.QLabel(lx('Interfaces and devices to display'), objectName='selectLabel')
        graph_list_layout.addWidget(select_label, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Interface / device graph list
        self._graph_list = LmTableWidget(objectName='graphList')
        self._graph_list.set_columns({GraphCol.Key: ['Key', 0, None],
                                      GraphCol.Name: [lx('Name'), 150, 'graphList_Name'],
                                      GraphCol.Type: [lx('Type'), 55, 'graphList_Type'],
                                      GraphCol.ID: [lx('ID'), 120, 'graphList_ID'],
                                      GraphCol.Color: [lx('Color'), 55, 'graphList_Color']})
        self._graph_list.set_header_resize([GraphCol.Name])
        self._graph_list.set_standard_setup(self)

        graph_list_size = LmConfig.table_height(8)
        self._graph_list.setMinimumHeight(graph_list_size)
        self._graph_list.setMaximumHeight(graph_list_size)
        self._graph_list.setMinimumWidth(380)
        graph_list_layout.addWidget(self._graph_list, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Interface / device graph list button bar
        graph_list_button_box = QtWidgets.QHBoxLayout()
        graph_list_button_box.setSpacing(5)
        add_graph_button = QtWidgets.QPushButton(lx('Add...'), objectName='addGraph')
        add_graph_button.clicked.connect(self.add_graph_button_click)
        graph_list_button_box.addWidget(add_graph_button)
        del_graph_button = QtWidgets.QPushButton(lx('Delete'), objectName='delGraph')
        del_graph_button.clicked.connect(self.del_graph_button_click)
        graph_list_button_box.addWidget(del_graph_button)
        graph_list_layout.addLayout(graph_list_button_box, 0)

        # Setup grid
        window_label = QtWidgets.QLabel(lx('Window:'), objectName='windowLabel')
        int_validator = QtGui.QIntValidator()
        int_validator.setRange(0, 99)
        self._graph_window_edit = QtWidgets.QLineEdit(objectName='windowEdit')
        self._graph_window_edit.setValidator(int_validator)
        window_unit = QtWidgets.QLabel(lx('hours (0 = max)'), objectName='windowUnit')

        back_color_label = QtWidgets.QLabel(lx('Background color:'), objectName='backColorLabel')
        self._graph_back_color_edit = LmTools.ColorButton(objectName='backColor')

        setup_grid = QtWidgets.QGridLayout()
        setup_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        setup_grid.setSpacing(10)
        setup_grid.addWidget(window_label, 0, 0)
        setup_grid.addWidget(self._graph_window_edit, 0, 1)
        setup_grid.addWidget(window_unit, 0, 2)
        setup_grid.addWidget(back_color_label, 1, 0)
        setup_grid.addWidget(self._graph_back_color_edit, 1, 1)
        setup_grid.setColumnStretch(2, 1)

        # Apply button
        apply_button = QtWidgets.QPushButton(lx('Apply'), objectName='apply')
        apply_button.clicked.connect(self.apply_graph_button_click)

        # Export button
        export_button = QtWidgets.QPushButton(lx('Export...'), objectName='export')
        export_button.clicked.connect(self.export_graph_button_click)

        # Control box
        control_box = QtWidgets.QVBoxLayout()
        control_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        control_box.setSpacing(20)
        control_box.addLayout(graph_list_layout, 0)
        control_box.addLayout(setup_grid, 0)
        control_box.addWidget(apply_button, QtCore.Qt.AlignmentFlag.AlignTop)
        control_box.addWidget(export_button, QtCore.Qt.AlignmentFlag.AlignTop)

        # Graph box
        graph_box = QtWidgets.QVBoxLayout()
        styles = {'color': '#FF0000', 'font-size': '11px'}

        self._down_graph = pg.PlotWidget()   # Setting objectName on input doesn't work
        self._down_graph.setObjectName('downGraph')
        self._down_graph.setTitle(lx('Download'))
        self._down_graph.setLabel('left', lx('Traffic (MB)'), **styles)
        self._down_graph.setLabel('bottom', lx('Time'), **styles)
        down_axis = pg.DateAxisItem()
        self._down_graph.setAxisItems({'bottom':down_axis})

        self._up_graph = pg.PlotWidget()     # Setting objectName on input doesn't work
        self._up_graph.setObjectName('upGraph')
        self._up_graph.setTitle(lx('Upload'))
        self._up_graph.setLabel('left', lx('Traffic (MB)'), **styles)
        self._up_graph.setLabel('bottom', lx('Time'), **styles)
        up_axis = pg.DateAxisItem()
        self._up_graph.setAxisItems({'bottom':up_axis})

        # To inhibit useless "skipping QEventPoint" logs on MacOS when moving the mouse on graphs
        # -> https://stackoverflow.com/questions/75746637/how-to-suppress-qt-pointer-dispatch-warning
        self._down_graph.viewport().setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self._up_graph.viewport().setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

        graph_box.addWidget(self._down_graph)
        graph_box.addWidget(self._up_graph)

        # Layout
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addLayout(control_box, 0)
        hbox.addWidget(separator)
        hbox.addLayout(graph_box, 1)
        self._graph_tab.setLayout(hbox)

        LmConfig.set_tooltips(self._graph_tab, 'graph')
        self._tab_widget.addTab(self._graph_tab, lx('Graph'))

        # Init context
        self.graph_tab_init()


    ### Init graph tab context
    def graph_tab_init(self):
        self._graph_data_loaded = False
        self._stat_frequency_interfaces = DCFG_STAT_FREQUENCY
        self._stat_frequency_devices = DCFG_STAT_FREQUENCY
        self._graph_valid_interfaces = []     # Array of [Key, MeasureNb, ID] - ID is the FriendlyName
        self._graph_valid_devices = []        # Arrray of [Key, MeasureNb, ID] - ID is the Key
        self._graph_data = []
        self._graph_window_timer = None


    ### Click on graph tab
    def graph_tab_click(self):
        if not self._graph_data_loaded:
            self._graph_data_loaded = True    # Must be first to avoid reentrency during tab drag&drop

            # Load config & data
            self._task.start(lx('Loading configuration...'))
            self.load_stat_params()
            self.load_home_lan_interfaces()
            self.load_home_lan_devices()
            self.load_graph_config()
            self._task.end()

            # Plot data
            self._task.start(lx('Plotting graphes...'))
            self.plot_graph()
            self._task.end()

            # Start graph time window update timer, to cut regularly old values
            self._graph_window_timer = QtCore.QTimer()
            self._graph_window_timer.timeout.connect(self.graph_window_update)
            self._graph_window_timer.start(WIND_UPDATE_FREQ)


    ### Click on add graph button
    def add_graph_button_click(self):
        dialog = AddGraphDialog(self)
        if dialog.exec():
            self.add_graph_object(dialog.get_type(),
                                  dialog.get_object_key(),
                                  dialog.get_object_name(),
                                  dialog.get_object_id(),
                                  dialog.get_color())


    ### Add a graph object in the list
    def add_graph_object(self, type, key, name, object_id, color):
        key = type + '_' + key

        i = self._graph_list.rowCount()
        self._graph_list.insertRow(i)
        self._graph_list.setItem(i, GraphCol.Key, QtWidgets.QTableWidgetItem(key))
        self._graph_list.setItem(i, GraphCol.Name, QtWidgets.QTableWidgetItem(name))

        type = lx('Interface') if type == GraphType.INTERFACE else lx('Device')
        self._graph_list.setItem(i, GraphCol.Type, QtWidgets.QTableWidgetItem(type))

        self._graph_list.setItem(i, GraphCol.ID, QtWidgets.QTableWidgetItem(object_id))

        color_item = QtWidgets.QTableWidgetItem()
        color_item.setBackground(QtGui.QColor(color))
        color_item.setData(QtCore.Qt.ItemDataRole.UserRole, color)
        self._graph_list.setItem(i, GraphCol.Color, color_item)


    ### Click on delete graph button
    def del_graph_button_click(self):
        current_selection = self._graph_list.currentRow()
        if current_selection >= 0:
            self._graph_list.removeRow(current_selection)
        else:
            self.display_error(mx('Please select a line.', 'lineSelect'))


    ### Click on apply button
    def apply_graph_button_click(self):
        # Load current setup
        self._graph_window = int(self._graph_window_edit.text())
        if self._graph_window < 0:
            self._graph_window = 0
        elif self._graph_window > 99:
            self._graph_window = 99
        self._graph_back_color = self._graph_back_color_edit.get_color()

        # Save setup
        self.save_graph_config()

        # Refresh interface & device lists
        self._task.start(lx('Plotting graphes...'))
        self.load_home_lan_interfaces()
        self.load_home_lan_devices()

        # Plot the graphs
        self.plot_graph()
        self._task.end()


    ### Click on export button
    def export_graph_button_click(self):
        if len(self._graph_data):
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, lx('Select Export Folder'))
            if len(folder):
                folder = QtCore.QDir.toNativeSeparators(folder)
                for o in self._graph_data:
                    self.export_graph_object(folder, o)
        else:
            self.display_error(mx('No graph to export.', 'noGraph'))


    ### Export a graph object to a file
    def export_graph_object(self, folder, graph_object):
        suffix = ''
        n = 0

        while True:
            file_path = os.path.join(folder, 'StatExport_' + graph_object['Name'] + suffix + '.csv')
            try:
                export_file = open(file_path, 'x', newline='')
            except FileExistsError:
                n += 1
                suffix = '_' + str(n)
                continue
            except Exception as e:
                LmTools.error(str(e))
                self.display_error(mx('Cannot create the file.', 'createFileErr'))
                return
            break

        self._task.start(lx('Exporting statistics...'))

        # Write header line
        csv_writer = csv.writer(export_file, dialect='excel', delimiter=LmConf.CsvDelimiter)
        csv_writer.writerow(['Download Timestamp', 'Download Bytes', 'Upload Timestamp', 'Upload Bytes'])

        dt = graph_object['DownTime']
        d = graph_object['Down']
        ut = graph_object['UpTime']
        u = graph_object['Up']

        for i in range(min(len(dt), len(ut))):
            csv_writer.writerow([str(dt[i]), str(int(d[i] * UNIT_DIVIDER)),
                                 str(ut[i]), str(int(u[i] * UNIT_DIVIDER))])

        self._task.end()

        try:
            export_file.close()
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx('Cannot save the file.', 'saveFileErr'))


    ### Load stats parameters
    def load_stat_params(self):
        try:
            self._stat_frequency_interfaces = self._api._stats.get_intf_frequency()
        except Exception as e:
            self.display_error(str(e))

        try:
            self._stat_frequency_devices = self._api._stats.get_device_frequency()
        except Exception as e:
            self.display_error(str(e))


    ### Load configuration
    def load_graph_config(self):
        self._graph_window = DCFG_WINDOW
        self._graph_back_color = DCFG_BACKGROUND_COLOR
        if LmConf.Graph is not None:
            c = LmConf.Graph
            p = c.get('Window')
            if p is not None:
                self._graph_window = int(p)
            p = c.get('BackColor')
            if p is not None:
                self._graph_back_color = p

            t = c['Objects']
            for o in t:
                p = o.get('Type')
                if p is None:
                    continue
                else:
                    type = p
                p = o.get('Key')
                if p is None:
                    continue
                else:
                    key = p
                p = o.get('Color')
                if p is None:
                    continue
                else:
                    color = p
                match type:
                    case GraphType.INTERFACE:
                        e = next((e for e in self._graph_valid_interfaces if e[0] == key), None)
                        if e is None:
                            continue
                        i = next((i for i in self._api._intf.get_list() if i['Key'] == key), None)
                        if i is None:
                            continue
                        self.add_graph_object(type, key, i['Name'], e[2], color)
                    case GraphType.DEVICE:
                        e = next((e for e in self._graph_valid_devices if e[0] == key), None)
                        if e is None:
                            continue
                        try:
                            name = LmConf.MacAddrTable[key]
                        except KeyError:
                            name = key
                        self.add_graph_object(type, key, name, e[2], color)
                    case _:
                        continue

        self._graph_window_edit.setText(str(self._graph_window))
        self._graph_back_color_edit.set_color(self._graph_back_color)


    ### Save configuration
    def save_graph_config(self):
        c = {'Window': self._graph_window,
             'BackColor': self._graph_back_color}

        t = []
        for i in range(self._graph_list.rowCount()):
            key = self._graph_list.item(i, GraphCol.Key).text()
            o = {'Type': key[0:3],
                  'Key': key[4:],
                  'Color': self._graph_list.item(i, GraphCol.Color).background().color().name()}
            t.append(o)
        c['Objects'] = t

        LmConf.Graph = c
        LmConf.save()


    ### Plot the graphs
    def plot_graph(self):
        # Apply current setup
        self._down_graph.setBackground(self._graph_back_color)
        self._down_graph.showGrid(x=True, y=True, alpha=0.4)
        self._up_graph.setBackground(self._graph_back_color)
        self._up_graph.showGrid(x=True, y=True, alpha=0.4)

        # Reset
        self._graph_data = []
        self._down_graph.clear()
        self._up_graph.clear()

        # Loop over the selected objects
        for i in range(self._graph_list.rowCount()):
            key = self._graph_list.item(i, GraphCol.Key).text()
            name = self._graph_list.item(i, GraphCol.Name).text()
            object_id = self._graph_list.item(i, GraphCol.ID).text()
            color = self._graph_list.item(i, GraphCol.Color).background().color()
            self.plot_object(key[0:3], key[4:], name, object_id, color)


    ### Plot an object
    def plot_object(self, type, key, name, object_id, color):
        o = {'Type': type,
              'Key': key,
              'Name': name,
              'ID': object_id}

        # Set time window
        if self._graph_window:
            end_time = int(time.time())
            start_time = end_time - (self._graph_window * 3600)
        else:
            start_time = 0
            end_time = 0

        swap_stats = False
        if type == GraphType.INTERFACE:
            stats_data = self.load_stats_interface(object_id, start_time, end_time)
            intf = next((i for i in self._api._intf.get_list() if i['Key'] == key), None)
            if intf is not None:
                swap_stats = intf['SwapStats']
        else:
            stats_data = self.load_stats_device(object_id, start_time, end_time)

        dt = [] # Download time data
        d = []  # Download data
        ut = [] # Upload time data
        u = []  # Upload data

        for e in reversed(stats_data):
            timestamp = e.get('Timestamp')
            if timestamp is not None:
                dt.append(timestamp)
                ut.append(timestamp)

                if swap_stats:
                    down_bits = e.get('Tx_Counter')
                else:
                    down_bits = e.get('Rx_Counter')
                if down_bits is None:
                    down_bits = 0
                d.append((down_bits / 8) / UNIT_DIVIDER)    # Convert bits to MBytes

                if swap_stats:
                    up_bits = e.get('Rx_Counter')
                else:
                    up_bits = e.get('Tx_Counter')
                if up_bits is None:
                    up_bits = 0
                u.append((up_bits / 8) / UNIT_DIVIDER)      # Convert bits to MBytes

        o['DownTime'] = dt
        o['Down'] = d
        o['UpTime'] = ut
        o['Up'] = u

        pen = pg.mkPen(color=color, width=1)
        o['DownLine'] = self._down_graph.plot(dt, d, name=object_id, pen=pen)
        o['UpLine'] = self._up_graph.plot(ut, u, name=object_id, pen=pen)

        self._graph_data.append(o)


    ### Update graph according to interface stats event
    def graph_update_interface_event(self, intf_key, timestamp, down_bytes, up_bytes):
        # Lookup for a stat object matching interface
        o = next((o for o in self._graph_data if (o['Type'] == GraphType.INTERFACE) and (o['Key'] == intf_key)), None)
        if o is not None:
            self.graph_update_object_event(o, timestamp, down_bytes, up_bytes)


    ### Update graph according to device stats event
    def graph_update_device_event(self, device_key, timestamp, down_bytes, up_bytes):
        # Lookup for a stat object matching interface
        o = next((o for o in self._graph_data if (o['Type'] == GraphType.DEVICE) and (o['Key'] == device_key)), None)
        if o is not None:
            self.graph_update_object_event(o, timestamp, down_bytes, up_bytes)


    ### Update graph according to stats event
    def graph_update_object_event(self, graph_object, timestamp, down_bytes, up_bytes):
        # Update download part
        if down_bytes is not None:
            # Update timestamp array
            dt = graph_object['DownTime']
            dt.append(timestamp)

            # Update data
            d = graph_object['Down']
            d.append(down_bytes / UNIT_DIVIDER)     # Convert to MBs

            # Update graph
            graph_object['DownLine'].setData(dt, d)

        # Update upload part
        if up_bytes is not None:
            # Update timestamp array
            ut = graph_object['UpTime']
            ut.append(timestamp)

            # Update data
            u = graph_object['Up']
            u.append(up_bytes / UNIT_DIVIDER)       # Convert to MBs

            # Update graph
            graph_object['UpLine'].setData(ut, u)


    # Cut old values to match graph time window
    def graph_window_update(self):
        # Determine older allowed timestamp
        if self._graph_window:
            window = self._graph_window
        else:
            # If no window cut after 5 days
            window = 5 * 24
        max_older_value = int(time.time()) - (window * 3600)

        # Loop on each drawn object
        for o in self._graph_data:
            self.graph_window_update_line(o['DownLine'], o['DownTime'], o['Down'], max_older_value)
            self.graph_window_update_line(o['UpLine'], o['UpTime'], o['Up'], max_older_value)


    # Cut old values to match graph time window
    def graph_window_update_line(self, line, time_array, data_array, max_older_value):
        need_refresh = False

        while(len(time_array) and (time_array[0] <= max_older_value)):
            need_refresh = True
            time_array.pop(0)
            data_array.pop(0)

        if need_refresh:
            line.setData(time_array, data_array)


    ### Update graph list with new device name
    def graph_update_device_name(self, device_key):
        i = self.find_graph_object_line(GraphType.DEVICE, device_key)
        if i > -1:
            try:
                name = LmConf.MacAddrTable[device_key]
            except KeyError:
                name = device_key
            self._graph_list.setItem(i, GraphCol.Name, QtWidgets.QTableWidgetItem(name))


    ### Load the current valid interfaces
    def load_home_lan_interfaces(self):
        try:
            interfaces = self._api._stats.get_intf_list()
        except Exception as e:
            self.display_error(str(e))
            return

        # Reset
        self._graph_valid_interfaces = []

        # Iterate over all valid interfaces
        for i in self._api._intf.get_list():
            # Check if key exists in the returned interfaces
            k = i['Key']
            intf_data = interfaces.get(k)
            if intf_data:
                m = int(intf_data.get('NumberOfStoredMeasures', 0))
                intf_id = intf_data.get('FriendlyName', k)
                self._graph_valid_interfaces.append([k, m, intf_id])


    ### Load the current valid devices
    def load_home_lan_devices(self):
        try:
            devices = self._api._stats.get_device_list()
        except Exception as e:
            self.display_error(str(e))
            return

        # Reset
        self._graph_valid_devices = []

        for d in devices:
            d = devices[d]
            device_id = d.get('MacAddress')
            if (device_id is not None) and len(device_id):
                m = int(d.get('NumberOfStoredMeasures', 0))
                self._graph_valid_devices.append([device_id, m, device_id])


    ### Load the stats for the given interface ID
    def load_stats_interface(self, intf_id, start, end):
        try:
            return self._api._stats.get_intf_results(intf_id, start, end)
        except Exception as e:
            self.display_error(str(e))
            return []


    ### Load the stats for the given device ID
    def load_stats_device(self, device_id, start, end):
        try:
            return self._api._stats.get_device_results(device_id, start, end)                
        except Exception as e:
            self.display_error(str(e))
            return []


    ### Find object line in graph list from object type & key, return -1 if not found
    def find_graph_object_line(self, type, key):
        key = type + '_' + key
        for i in range(self._graph_list.rowCount()):
            if self._graph_list.item(i, GraphCol.Key).text() == key:
                return i
        return -1
