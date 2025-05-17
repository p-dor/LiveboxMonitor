### Livebox Monitor Profile selection dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.api.LmLiveboxInfoApi import LiveboxInfoApi
from LiveboxMonitor.lang.LmLanguages import get_select_profile_label as lx


# ################################ Profile selection dialog ################################
class SelectProfileDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SelectProfileDialog, self).__init__(parent)
        self.resize(350, 130)

        main_label = QtWidgets.QLabel(lx('Please select a profile to use:'), objectName='mainLabel')
        self._profile_combo = QtWidgets.QComboBox(objectName='profileCombo')
        current_index = 0
        for i, p in enumerate(LmConf.Profiles):
            name = p['Name']
            self._profile_combo.addItem(name)
            if (LmConf.CurrProfile is not None) and (LmConf.CurrProfile['Name'] == name):
                current_index = i
        self._profile_combo.currentIndexChanged.connect(self.profile_selected)

        associated_mac_label = QtWidgets.QLabel(lx('Associated Livebox MAC:'), objectName='assMacLabel')
        self._ass_mac = QtWidgets.QLabel(objectName='assMacValue')
        self._ass_mac.setFont(LmTools.BOLD_FONT)

        detected_mac_label = QtWidgets.QLabel(lx('Detected Livebox MAC:'), objectName='detMacLabel')
        self._det_mac = QtWidgets.QLabel(objectName='detMacValue')
        self._det_mac.setFont(LmTools.BOLD_FONT)

        self._warning = QtWidgets.QLabel('', objectName='warnLabel')

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(main_label, 0, 0)
        grid.addWidget(self._profile_combo, 1, 0, 1, 2)
        grid.addWidget(associated_mac_label, 2, 0)
        grid.addWidget(self._ass_mac, 2, 1)
        grid.addWidget(detected_mac_label, 3, 0)
        grid.addWidget(self._det_mac, 3, 1)
        grid.addWidget(self._warning, 4, 0, 1, 2)

        create_profile_button = QtWidgets.QPushButton(lx('New Profile...'), objectName='createProfile')
        create_profile_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 3px; padding-bottom: 3px;')
        create_profile_button.clicked.connect(self.create_profile)
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
        cancel_button.clicked.connect(self.reject)
        button_bar = QtWidgets.QHBoxLayout()
        button_bar.setSpacing(10)
        button_bar.addWidget(create_profile_button, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        ok_button_bar = QtWidgets.QHBoxLayout()
        ok_button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        ok_button_bar.setSpacing(10)
        ok_button_bar.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        ok_button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        button_bar.addLayout(ok_button_bar)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(20)
        vbox.addLayout(grid, 0)
        vbox.addLayout(button_bar, 1)

        LmConfig.set_tooltips(self, 'sprofile')

        self.setWindowTitle(lx('Profile selection'))

        if current_index:
            self._profile_combo.setCurrentIndex(current_index)
        else:
            self.profile_selected(0)

        self._create_profile = False

        self.setModal(True)
        self.show()


    def profile_selected(self, index):
        p = LmConf.Profiles[index]
        associated_livebox_mac = p.get('Livebox MacAddr')
        if associated_livebox_mac is None:
            self._ass_mac.setText(lx('<None>'))
            self._ass_mac.setStyleSheet('QLabel { color : green }')
        else:
            self._ass_mac.setText(associated_livebox_mac)
            self._ass_mac.setStyleSheet('QLabel { color : black }')

        LmTools.mouse_cursor_busy()
        detected_livebox_mac = LiveboxInfoApi.get_livebox_mac_nosign(p.get('Livebox URL'))
        LmTools.mouse_cursor_normal()
        if detected_livebox_mac is None:
            self._det_mac.setText(lx('<None>'))
            self._det_mac.setStyleSheet('QLabel { color : red }')
            self._warning.setText(lx('No Livebox detected at profile\'s URL.'))
            self._warning.setStyleSheet('QLabel { color : red }')
        else:
            self._det_mac.setText(detected_livebox_mac)
            if associated_livebox_mac is None:
                self._det_mac.setStyleSheet('QLabel { color : green }')
                self._warning.setText(lx('Detected MAC will be associated to this profile.'))
                self._warning.setStyleSheet('QLabel { color : green }')
            elif detected_livebox_mac == associated_livebox_mac:
                self._det_mac.setStyleSheet('QLabel { color : green }')
                self._warning.setText('')
                self._warning.setStyleSheet('QLabel { color : black }')
            else:
                self._det_mac.setStyleSheet('QLabel { color : red }')
                self._warning.setText(lx('Warning: another Livebox is associated to this profile.'))
                self._warning.setStyleSheet('QLabel { color : red }')


    def profile_index(self):
        return self._profile_combo.currentIndex()


    def do_create_profile(self):
        return self._create_profile


    def create_profile(self):
        self._create_profile = True
        self.accept()
