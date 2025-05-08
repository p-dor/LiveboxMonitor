### Livebox Monitor screen & LEDs setup dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import get_screen_label as lx


# ################################ Screen setup dialog ################################
class ScreenDialog(QtWidgets.QDialog):
    def __init__(self, orange_led_level, show_wifi_password, parent=None):
        super(ScreenDialog, self).__init__(parent)
        self.setMinimumWidth(300)
        self.resize(350, 150)

        orange_label = QtWidgets.QLabel(lx('LED Brightness'), objectName='orangeLabel')
        self._orange_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, objectName='orangeSlider')
        self._orange_slider.setRange(0, 255)
        self._orange_slider.setValue(orange_led_level)
        self._orange_slider.setSingleStep(5)
        self._orange_slider.setPageStep(50)
        self._orange_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksAbove)
        self._orange_slider.setTickInterval(15)
        self._orange_slider.valueChanged.connect(self.orange_level_changed)
        self._orange_value = QtWidgets.QLabel(str(orange_led_level), objectName='orangeValue')
        self._orange_value.setMinimumWidth(20)

        self._show_wifi_password_checkbox = QtWidgets.QCheckBox(lx('Show Wifi Password'), objectName='showWifiPasswordCheckbox')
        if show_wifi_password:
            self._show_wifi_password_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self._show_wifi_password_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(orange_label, 0, 0)
        grid.addWidget(self._orange_slider, 0, 1)
        grid.addWidget(self._orange_value, 0, 2)
        grid.addWidget(self._show_wifi_password_checkbox, 1, 0, 1, 3)

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
        vbox.addLayout(grid, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.SetToolTips(self, 'screen')

        self.setWindowTitle(lx('LEDs & Screen Setup'))

        self.setModal(True)
        self.show()


    def orange_level_changed(self, value):
        self._orange_value.setText(str(value))


    def get_orange_led_level(self):
        return self._orange_slider.value()


    def get_show_wifi_password(self):
        return self._show_wifi_password_checkbox.checkState() == QtCore.Qt.CheckState.Checked
