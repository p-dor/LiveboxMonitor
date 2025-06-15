### Livebox Monitor device type dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import get_device_type_label as lx


# ################################ Set device type dialog ################################
class SetDeviceTypeDialog(QtWidgets.QDialog):
    def __init__(self, device_key, device_type_key, parent=None):
        super().__init__(parent)
        self.resize(320, 170)

        self._ignore_signal = False

        label = QtWidgets.QLabel(lx('Type for [{}] device:').format(device_key), objectName='mainLabel')

        self._type_name_combo = QtWidgets.QComboBox(objectName='typeNameCombo')
        self._type_name_combo.setIconSize(QtCore.QSize(45, 45))

        for i, d in enumerate(LmConfig.DEVICE_TYPES):
            self._type_name_combo.addItem(d['Name'])
            self._type_name_combo.setItemIcon(i, QtGui.QIcon(d['PixMap']))
        self._type_name_combo.activated.connect(self.type_name_selected)

        self._type_key_edit = QtWidgets.QLineEdit(objectName='typeKeyEdit')
        self._type_key_edit.textChanged.connect(self.type_key_typed)
        self._type_key_edit.setText(device_type_key)

        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
        cancel_button.clicked.connect(self.reject)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.setSpacing(10)
        hbox.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(label, 0)
        vbox.addWidget(self._type_name_combo, 0)
        vbox.addWidget(self._type_key_edit, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, 'dtype')

        self.setWindowTitle(lx('Assign a device type'))
        self.setModal(True)
        self.show()


    def get_type_key(self):
        return self._type_key_edit.text()


    def type_name_selected(self, index):
        if not self._ignore_signal:
            self._ignore_signal = True
            self._type_key_edit.setText(LmConfig.DEVICE_TYPES[index]['Key'])
            self._ignore_signal = False


    def type_key_typed(self, type_key):
        if not self._ignore_signal:
            self._ignore_signal = True

            # Find the index where 'Key' matches type_key, default to 0 if not found
            i = next((idx for idx, d in enumerate(LmConfig.DEVICE_TYPES) if d['Key'] == type_key), 0)

            self._type_name_combo.setCurrentIndex(i)
            self._ignore_signal = False
