### Livebox Monitor add Graph dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang.LmLanguages import get_add_graph_label as lx


# ################################ VARS & DEFS ################################

# Config default
DCFG_OBJECT_COLOR = [ '#E26043',		# (226, 96, 67)
					  '#626DF4',		# (98, 109, 244)
					  '#65F4B4',		# (101, 244, 180)
					  '#EDF465',		# (237, 244, 101)
					  '#B474F4',		# (180, 116, 244)
					  '#42F4F4',		# (66, 244, 244)
					  '#FF0000',		# (255, 0, 0)
					  '#00FF00',		# (0, 255, 0)
					  '#0000FF',		# (0, 0, 255)
					  '#FFFF00',		# (255, 255, 0)
					  '#FF00FF' ]		# (255, 0, 255)

# Graph type
class GraphType:
	INTERFACE = 'inf'		# Must be 3 chars
	DEVICE = 'dvc'			# Must be 3 chars


# ################################ Add Graph dialog ################################
class AddGraphDialog(QtWidgets.QDialog):
	def __init__(self, parent):
		super(AddGraphDialog, self).__init__(parent)
		self.resize(250, 150)

		self._app = parent

		type_label = QtWidgets.QLabel(lx('Type'), objectName='typeLabel')
		self._type_combo = QtWidgets.QComboBox(objectName='typeCombo')
		self._type_combo.addItem(lx('Interface'))
		self._type_combo.addItem(lx('Device'))
		self._type_combo.activated.connect(self.type_selected)

		object_label = QtWidgets.QLabel(lx('Object'), objectName='objectLabel')
		self._object_combo = QtWidgets.QComboBox(objectName='objectCombo')
		self._object_combo.activated.connect(self.object_selected)
		self.load_object_list()

		color_label = QtWidgets.QLabel(lx('Color'), objectName='colorLabel')
		self._color_edit = LmTools.ColorButton(objectName='colorEdit')
		self._color_edit.set_color(DCFG_OBJECT_COLOR[self._app._graphList.rowCount() % len(DCFG_OBJECT_COLOR)])
		self._color_edit._color_changed.connect(self.color_selected)

		grid = QtWidgets.QGridLayout()
		grid.setSpacing(10)
		grid.addWidget(type_label, 0, 0)
		grid.addWidget(self._type_combo, 0, 1)
		grid.addWidget(object_label, 1, 0)
		grid.addWidget(self._object_combo, 1, 1)
		grid.addWidget(color_label, 2, 0)
		grid.addWidget(self._color_edit, 2, 1)
		grid.setColumnStretch(1, 1)

		separator = QtWidgets.QFrame()
		separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		id_label = QtWidgets.QLabel(lx('ID:'), objectName='IDLabel')
		self._id = QtWidgets.QLabel(objectName='IDValue')
		measure_nb_label = QtWidgets.QLabel(lx('Measures number:'), objectName='measureLabel')
		self._measure_nb = QtWidgets.QLabel(objectName='measureValue')
		history_label = QtWidgets.QLabel(lx('History:'), objectName='historyLabel')
		self._history = QtWidgets.QLabel(objectName='historyValue')

		info_grid = QtWidgets.QGridLayout()
		info_grid.setSpacing(8)
		info_grid.addWidget(id_label, 0, 0)
		info_grid.addWidget(self._id, 0, 1)
		info_grid.addWidget(measure_nb_label, 1, 0)
		info_grid.addWidget(self._measure_nb, 1, 1)
		info_grid.addWidget(history_label, 2, 0)
		info_grid.addWidget(self._history, 2, 1)
		info_grid.setColumnStretch(1, 1)

		self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
		self._ok_button.clicked.connect(self.accept)
		self._ok_button.setDefault(True)
		cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
		cancel_button.clicked.connect(self.reject)
		hbox = QtWidgets.QHBoxLayout()
		hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		hbox.setSpacing(10)
		hbox.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		hbox.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		vbox = QtWidgets.QVBoxLayout(self)
		vbox.setSpacing(18)
		vbox.addLayout(grid, 0)
		vbox.addWidget(separator)
		vbox.addLayout(info_grid, 0)
		vbox.addLayout(hbox, 1)

		LmConfig.set_tooltips(self, 'addgraph')

		self.setWindowTitle(lx('Add a graph'))
		self.udpdate_infos()
		self.set_ok_button_state()
		self.setModal(True)
		self.show()


	def load_object_list(self):
		self._object_combo.clear()

		if self.get_type() == GraphType.DEVICE:
			self.load_device_list()
		else:
			self.load_interface_list()


	def load_interface_list(self):
		for i in self._app._graphValidInterfaces:
			k = i[0]
			# Look if not already in the graph list
			if self._app.findGraphObjectLine(GraphType.INTERFACE, k) == -1:
				intf = next((j for j in self._app._api._intf.get_list() if j['Key'] == k), None)
				if intf is not None:
					self._object_combo.addItem(intf['Name'], userData=k)


	def load_device_list(self):
		for d in self._app._graphValidDevices:
			k = d[0]
			# Look if not already in the graph list
			if self._app.findGraphObjectLine(GraphType.DEVICE, k) == -1:
				try:
					name = LmConf.MacAddrTable[k]
				except Exception:
					name = k
				self._object_combo.addItem(name, userData=k)


	def type_selected(self, index):
		self.load_object_list()
		self.udpdate_infos()
		self.set_ok_button_state()


	def object_selected(self, index):
		self.udpdate_infos()


	def color_selected(self, color):
		self.set_ok_button_state()


	def udpdate_infos(self):
		# Update infos according to selected object
		type = self.get_type()
		key = self.get_object_key()
		if type == GraphType.INTERFACE:
			table = self._app._graphValidInterfaces
			frequency = self._app._statFrequencyInterfaces
		else:
			table = self._app._graphValidDevices
			frequency = self._app._statFrequencyDevices

		# Search key in the table
		entry = next((o for o in table if o[0] == key), ['', 0, ''])
		measure_nb = entry[1]
		history = measure_nb / ( 60 / frequency) / 60

		# Update infos
		self._id.setText(entry[2])
		self._measure_nb.setText(str(measure_nb))
		self._history.setText(lx('{:.1f} hours').format(history))


	def set_ok_button_state(self):
		self._ok_button.setDisabled((self._object_combo.count() == 0) or (self.get_color() is None))


	def get_type(self):
		if self._type_combo.currentIndex():
			return GraphType.DEVICE
		return GraphType.INTERFACE


	def get_object_key(self):
		return self._object_combo.currentData()


	def get_object_id(self):
		return self._id.text()


	def get_object_name(self):
		return self._object_combo.currentText()


	def get_color(self):
		return self._color_edit.get_color()
