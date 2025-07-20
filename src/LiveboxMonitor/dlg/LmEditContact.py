### Livebox Monitor edit contact dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.lang.LmLanguages import get_phone_contact_label as lx


# ################################ Edit contact dialog ################################
class EditContactDialog(QtWidgets.QDialog):
    def __init__(self, edit_mode, contact=None, parent=None):
        super().__init__(parent)
        self.resize(320, 170)

        self._ready = False

        first_name_edit_label = QtWidgets.QLabel(lx("First name"), objectName="firstNameLabel")
        self._first_name_edit = QtWidgets.QLineEdit(objectName="firstNameEdit")
        self._first_name_edit.textChanged.connect(self.text_changed)

        name_edit_label = QtWidgets.QLabel(lx("Name"), objectName="nameLabel")
        self._name_edit = QtWidgets.QLineEdit(objectName="nameEdit")
        self._name_edit.textChanged.connect(self.text_changed)

        phone_nb_reg_exp = QtCore.QRegularExpression(r"^[0-9+*#]{1}[0-9*#]{19}$")
        phone_nb_validator = QtGui.QRegularExpressionValidator(phone_nb_reg_exp)

        cell_edit_label = QtWidgets.QLabel(lx("Mobile"), objectName="cellLabel")
        self._cell_edit = QtWidgets.QLineEdit(objectName="cellEdit")
        self._cell_edit.setValidator(phone_nb_validator)
        self._cell_edit.textChanged.connect(self.text_changed)

        home_edit_label = QtWidgets.QLabel(lx("Home"), objectName="homeLabel")
        self._home_edit = QtWidgets.QLineEdit(objectName="homeEdit")
        self._home_edit.setValidator(phone_nb_validator)
        self._home_edit.textChanged.connect(self.text_changed)

        work_edit_label = QtWidgets.QLabel(lx("Work"), objectName="workLabel")
        self._work_edit = QtWidgets.QLineEdit(objectName="workEdit")
        self._work_edit.setValidator(phone_nb_validator)
        self._work_edit.textChanged.connect(self.text_changed)

        ring_tone_edit_label = QtWidgets.QLabel(lx("Ring tone"), objectName="ringToneLabel")
        self._ring_tone_combo = QtWidgets.QComboBox(objectName="ringToneCombo")
        for i in range(1, 8):
            self._ring_tone_combo.addItem(str(i))

        edit_grid = QtWidgets.QGridLayout()
        edit_grid.setSpacing(10)
        edit_grid.addWidget(first_name_edit_label, 0, 0)
        edit_grid.addWidget(self._first_name_edit, 0, 1)
        edit_grid.addWidget(name_edit_label, 1, 0)
        edit_grid.addWidget(self._name_edit, 1, 1)
        edit_grid.addWidget(cell_edit_label, 2, 0)
        edit_grid.addWidget(self._cell_edit, 2, 1)
        edit_grid.addWidget(home_edit_label, 3, 0)
        edit_grid.addWidget(self._home_edit, 3, 1)
        edit_grid.addWidget(work_edit_label, 4, 0)
        edit_grid.addWidget(self._work_edit, 4, 1)
        edit_grid.addWidget(ring_tone_edit_label, 5, 0)
        edit_grid.addWidget(self._ring_tone_combo, 5, 1)

        self._ok_button = QtWidgets.QPushButton(lx("OK"), objectName="ok")
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx("Cancel"), objectName="cancel")
        cancel_button.clicked.connect(self.reject)
        button_bar = QtWidgets.QHBoxLayout()
        button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        button_bar.setSpacing(10)
        button_bar.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(edit_grid, 0)
        vbox.addLayout(button_bar, 1)

        self._first_name_edit.setFocus()

        LmConfig.set_tooltips(self, "pcontact")

        self.setWindowTitle(lx("Contact edition") if edit_mode else lx("Contact creation"))

        if contact:
            self._contact = contact
            self._first_name_edit.setText(contact["firstname"])
            self._name_edit.setText(contact["name"])
            self._cell_edit.setText(contact["cell"])
            self._home_edit.setText(contact["home"])
            self._work_edit.setText(contact["work"])
            self._ring_tone_combo.setCurrentIndex(int(contact["ringtone"]) - 1)
        else:
            self._contact = {}

        self.set_ok_button_state()
        self.setModal(True)
        self._ready = True
        self.show()


    def text_changed(self, text):
        if self._ready:
            self.set_ok_button_state()


    def set_ok_button_state(self):
        c = self.get_contact()
        if ((len(c["name"]) == 0) and (len(c["firstname"]) == 0)):
            self._ok_button.setDisabled(True)
            return

        if ((len(c["cell"]) == 0) and (len(c["home"]) == 0) and (len(c["work"]) == 0)):
            self._ok_button.setDisabled(True)
            return

        self._ok_button.setDisabled(False)


    def get_contact(self):
        self._contact["firstname"] = EditContactDialog.cleanup_name(self._first_name_edit.text())
        self._contact["name"] = EditContactDialog.cleanup_name(self._name_edit.text())
        self._contact["formattedName"] = EditContactDialog.compute_formatted_name(self._contact["name"], self._contact["firstname"])
        self._contact["cell"] = EditContactDialog.cleanup_phone_number(self._cell_edit.text())
        self._contact["home"] = EditContactDialog.cleanup_phone_number(self._home_edit.text())
        self._contact["work"] = EditContactDialog.cleanup_phone_number(self._work_edit.text())
        self._contact["ringtone"] = self._ring_tone_combo.currentText()
        return self._contact


    @staticmethod
    def cleanup_name(name):
        return name.replace(";", " ")


    @staticmethod
    def compute_formatted_name(name, firstname):
        if name:
            if firstname:
                return f"{name} {firstname}"
            return name
        return firstname


    @staticmethod
    def cleanup_phone_number(phone_nb):
        if phone_nb and (phone_nb[0] == "+"):
            return f"00{phone_nb[1:]}"
        return phone_nb
