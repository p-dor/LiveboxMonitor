### Livebox Monitor phone tab module ###

import os
import webbrowser
import requests

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, NumericSortItem, CenteredIconsDelegate
from LiveboxMonitor.dlg.LmEditContact import EditContactDialog
from LiveboxMonitor.lang.LmLanguages import get_phone_label as lx, get_phone_message as mx
from LiveboxMonitor.util import LmUtils


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = "phoneTab"

# List columns
class CallCol(IntEnum):
    Key = 0
    Type = 1
    Time = 2
    Number = 3
    ContactSource = 4   # N=None, L=Livebox, P=Program dynamic guess, S=Spam
    Contact = 5
    Duration = 6
ICON_COLUMNS = [CallCol.Type]

class ContactCol(IntEnum):
    Key = 0
    Name = 1
    Cell = 2
    Home = 3
    Work = 4
    Ring = 5

# Contact sources
class Source:
    NoSource = "N"
    Livebox = "L"
    Program = "P"
    Spam = "S"

# Call types
class CallType(IntEnum):
    Missed = 1
    Emitted = 2
    Received = 3
    Failed = 4

# Check spam URLs
CHECK_SPAM_URL1 = "https://www.numeroinconnu.fr/numero/{}"
CHECK_SPAM_URL2 = "https://callfilter.app/{}"

# CallFilter URL
CALLFILTER_URL = "https://api.callfilter.app/apis/{0}/1/{1}"

# Spam indicator in call list
SPAM_CONTACT_NAME = "# SPAM #"



# ################################ LmPhone class ################################
class LmPhone:

    ### Create phone tab
    def create_phone_tab(self):
        self._phone_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Call list
        self._call_list = LmTableWidget(objectName="callList")
        self._call_list.set_columns({CallCol.Key: ["Key", 0, None],
                                     CallCol.Type: [lx("T"), 30, "calist_Type"],
                                     CallCol.Time: [lx("Time"), 130, "calist_Time"],
                                     CallCol.Number: [lx("Number"), 110, "calist_Number"],
                                     CallCol.ContactSource: ["CS", 0, None],
                                     CallCol.Contact: [lx("Contact"), 250, "calist_Contact"],
                                     CallCol.Duration: [lx("Duration"), 80, "calist_Duration"]})
        self._call_list.set_header_resize([CallCol.Contact])
        self._call_list.set_standard_setup(self)
        self._call_list.itemSelectionChanged.connect(self.call_list_click)
        self._call_list.doubleClicked.connect(self.edit_contact_from_call_list_click)
        self._call_list.setMinimumWidth(480)
        self._call_list.setMaximumWidth(540)
        self._call_list.setItemDelegate(CenteredIconsDelegate(self, ICON_COLUMNS))

        # Call button bar
        call_buttons_box = QtWidgets.QHBoxLayout()
        call_buttons_box.setSpacing(30)
        refresh_call_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refreshCall")
        refresh_call_button.clicked.connect(self.refresh_call_button_click)
        call_buttons_box.addWidget(refresh_call_button)
        self._delete_call_button = QtWidgets.QPushButton(lx("Delete"), objectName="deleteCall")
        self._delete_call_button.clicked.connect(self.delete_call_button_click)
        call_buttons_box.addWidget(self._delete_call_button)
        delete_all_calls_button = QtWidgets.QPushButton(lx("Delete All..."), objectName="deleteAllCalls")
        delete_all_calls_button.clicked.connect(self.delete_all_calls_button_click)
        call_buttons_box.addWidget(delete_all_calls_button)

        # Spam tools button bar
        spam_buttons_box = QtWidgets.QHBoxLayout()
        spam_buttons_box.setSpacing(30)
        spam_call_scan_button = QtWidgets.QPushButton(lx("Spams scan"), objectName="spamCallScan")
        spam_call_scan_button.clicked.connect(self.spam_call_scan_button_click)
        spam_buttons_box.addWidget(spam_call_scan_button)
        self._spam_call_sites_button = QtWidgets.QPushButton(lx("Spam sites"), objectName="spamCallSites")
        self._spam_call_sites_button.clicked.connect(self.spam_call_sites_button_click)
        spam_buttons_box.addWidget(self._spam_call_sites_button)
        self._set_spam_call_button = QtWidgets.QPushButton(lx("Set as spam"), objectName="setSpamCall")
        self._set_spam_call_button.clicked.connect(self.set_spam_call_button_click)
        spam_buttons_box.addWidget(self._set_spam_call_button)

        # Call layout
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        call_box = QtWidgets.QVBoxLayout()
        call_box.setSpacing(13)
        call_box.addWidget(self._call_list, 1)
        call_box.addLayout(call_buttons_box, 0)
        call_box.insertSpacing(-1, 2)
        call_box.addWidget(separator)
        call_box.insertSpacing(-1, 2)
        call_box.addLayout(spam_buttons_box, 0)

        # Contact list
        self._contact_list = LmTableWidget(objectName="contactList")
        self._contact_list.set_columns({ContactCol.Key: ["Key", 0, None],
                                        ContactCol.Name: [lx("Name"), 250, "colist_Name"],
                                        ContactCol.Cell: [lx("Mobile"), 110, "colist_Cell"],
                                        ContactCol.Home: [lx("Home"), 110, "colist_Home"],
                                        ContactCol.Work: [lx("Work"), 110, "colist_Work"],
                                        ContactCol.Ring: [lx("Ring"), 60, "colist_Ring"]})
        self._contact_list.set_header_resize([ContactCol.Name])
        self._contact_list.set_standard_setup(self)
        self._contact_list.itemSelectionChanged.connect(self.contact_list_click)
        self._contact_list.doubleClicked.connect(self.edit_contact_button_click)

        # Contact button bar
        contact_buttons_box = QtWidgets.QHBoxLayout()
        contact_buttons_box.setSpacing(10)
        refresh_contact_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refreshContact")
        refresh_contact_button.clicked.connect(self.refresh_contact_button_click)
        contact_buttons_box.addWidget(refresh_contact_button)
        add_contact_button = QtWidgets.QPushButton(lx("Add..."), objectName="addContact")
        add_contact_button.clicked.connect(self.add_contact_button_click)
        contact_buttons_box.addWidget(add_contact_button)
        self._edit_contact_button = QtWidgets.QPushButton(lx("Edit..."), objectName="editContact")
        self._edit_contact_button.clicked.connect(self.edit_contact_button_click)
        contact_buttons_box.addWidget(self._edit_contact_button)
        self._delete_contact_button = QtWidgets.QPushButton(lx("Delete"), objectName="deleteContact")
        self._delete_contact_button.clicked.connect(self.delete_contact_button_click)
        contact_buttons_box.addWidget(self._delete_contact_button)
        delete_all_contacts_button = QtWidgets.QPushButton(lx("Delete All..."), objectName="deleteAllContacts")
        delete_all_contacts_button.clicked.connect(self.delete_all_contacts_button_click)
        contact_buttons_box.addWidget(delete_all_contacts_button)

        # Tool button bar
        tool_buttons_box = QtWidgets.QHBoxLayout()
        tool_buttons_box.setSpacing(30)

        phone_ring_set = QtWidgets.QHBoxLayout()
        phone_ring_set.setSpacing(2)
        self._ringtone_combo = QtWidgets.QComboBox(objectName="ringToneCombo")
        self._ringtone_combo.addItem("-")
        for i in range(1, 8):
            self._ringtone_combo.addItem(str(i))
        self._ringtone_combo.setMaximumWidth(55)
        phone_ring_set.addWidget(self._ringtone_combo)
        phone_ring_button = QtWidgets.QPushButton(lx("Phone Ring"), objectName="phoneRing")
        phone_ring_button.clicked.connect(self.phone_ring_button_click)
        phone_ring_set.addWidget(phone_ring_button)
        tool_buttons_box.addLayout(phone_ring_set, 0)

        export_contacts_button = QtWidgets.QPushButton(lx("Export..."), objectName="exportContacts")
        export_contacts_button.clicked.connect(self.export_contacts_button_click)
        tool_buttons_box.addWidget(export_contacts_button)
        import_contacts_button = QtWidgets.QPushButton(lx("Import..."), objectName="importContacts")
        import_contacts_button.clicked.connect(self.import_contacts_button_click)
        tool_buttons_box.addWidget(import_contacts_button)

        # Contact layout
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        contact_box = QtWidgets.QVBoxLayout()
        contact_box.setSpacing(13)
        contact_box.addWidget(self._contact_list, 1)
        contact_box.addLayout(contact_buttons_box, 0)
        contact_box.insertSpacing(-1, 2)
        contact_box.addWidget(separator)
        contact_box.insertSpacing(-1, 2)
        contact_box.addLayout(tool_buttons_box, 0)

        # Layout
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addLayout(call_box, 1)
        hbox.addWidget(separator)
        hbox.addLayout(contact_box, 1)
        self._phone_tab.setLayout(hbox)

        LmConfig.set_tooltips(self._phone_tab, "phone")
        self._tab_widget.addTab(self._phone_tab, lx("Phone"))

        # Init context
        self.phone_tab_init()


    ### Init phone tab context
    def phone_tab_init(self):
        self._phone_data_loaded = False
        self._contact_matching = {}


    ### Reset phone tab (not used)
    def phone_tab_reset(self):
        self._call_list.clearContents()
        self._call_list.setRowCount(0)
        self._contact_list.clearContents()
        self._contact_list.setRowCount(0)
        self.phone_tab_init()


    ### Click on phone tab
    def phone_tab_click(self):
        if not self._phone_data_loaded:
            self._phone_data_loaded = True    # Must be first to avoid reentrency during tab drag&drop
            self.load_contact_list()          # Load it first for dynamic contact matching in call list
            self.load_call_list()


    ### Click on call list item
    def call_list_click(self):
        i = self._call_list.currentRow()
        if i >= 0:
            self._delete_call_button.setEnabled(True)
            self._spam_call_sites_button.setEnabled(True)

            # Activate & set Set Spam button title according to call type
            call_type = self._call_list.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
            if (call_type == CallType.Missed) or (call_type == CallType.Received):
                contact_source = self._call_list.item(i, CallCol.ContactSource).text()
                if (contact_source == Source.NoSource) or (contact_source == Source.Spam):
                    self._set_spam_call_button.setEnabled(True)
                    if contact_source == Source.Spam:
                        self._set_spam_call_button.setText(lx("Unset as spam"))
                    else:
                        self._set_spam_call_button.setText(lx("Set as spam"))
                else:
                    self._set_spam_call_button.setEnabled(False)
            else:
                self._set_spam_call_button.setEnabled(False)
        else:
            self._delete_call_button.setEnabled(False)
            self._spam_call_sites_button.setEnabled(False)
            self._set_spam_call_button.setEnabled(False)


    ### Click on contact list item
    def contact_list_click(self):
        if self._contact_list.currentRow() >= 0:
            self._edit_contact_button.setEnabled(True)
            self._delete_contact_button.setEnabled(True)
        else:
            self._edit_contact_button.setEnabled(False)
            self._delete_contact_button.setEnabled(False)


    ### Click on call list refresh button
    def refresh_call_button_click(self):
        self._call_list.clearContents()
        self._call_list.setRowCount(0)
        self.load_call_list()


    ### Click on spam calls scan button
    def spam_call_scan_button_click(self):
        if LmConf.CallFilterApiKey:
            self.scan_spams()
        else:
            self.display_error(mx("You must configure a CallFilter API Key in the preferences first.", "callFilterAPIKeyErr"))


    ### Click on spam call sites button
    def spam_call_sites_button_click(self):
        i = self._call_list.currentRow()
        if i >= 0:
            phone_nb = LmPhone.intl_phone_number(self._call_list.item(i, CallCol.Number).text(), False)
            webbrowser.open_new_tab(CHECK_SPAM_URL1.format(phone_nb))
            webbrowser.open_new_tab(CHECK_SPAM_URL2.format(phone_nb))
        else:
            self.display_error(mx("Please select a phone call.", "callSelect"))


    ### Click on set/unset spam call button
    def set_spam_call_button_click(self):
        i = self._call_list.currentRow()
        if i >= 0:
            call_type = self._call_list.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
            if (call_type == CallType.Missed) or (call_type == CallType.Received):
                phone_nb = LmPhone.intl_phone_number(self._call_list.item(i, CallCol.Number).text())
                source = self._call_list.item(i, CallCol.ContactSource).text()
                if source == Source.Spam:
                    LmConf.unset_spam_call(phone_nb)
                    set_as_spam = False
                else:
                    LmConf.set_spam_call(phone_nb)
                    set_as_spam = True
        else:
            self.display_error(mx("Please select a phone call.", "callSelect"))
            return

        # Update all lines with same number
        self._call_list.setSortingEnabled(False)
        for i in range(self._call_list.rowCount()):
            call_type = self._call_list.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
            if (call_type == CallType.Missed) or (call_type == CallType.Received):
                line_phone_nb = LmPhone.intl_phone_number(self._call_list.item(i, CallCol.Number).text())
                if line_phone_nb == phone_nb:
                    self.display_spam_call(i, set_as_spam)
        self._call_list.setSortingEnabled(True)

        self.call_list_click()


    ### Click on delete call button
    def delete_call_button_click(self):
        current_selection = self._call_list.currentRow()
        if current_selection >= 0:
            key = self._call_list.item(current_selection, CallCol.Key).text()
            try:
                self._api._voip.delete_call(key)
            except Exception as e:
                self.display_error(str(e))
                return

            self._call_list.removeRow(current_selection)
        else:
            self.display_error(mx("Please select a phone call.", "callSelect"))


    ### Click on delete all calls button
    def delete_all_calls_button_click(self):
        if self.ask_question(mx("Are you sure you want to delete all phone calls?", "delAllCalls")):
            self._task.start(lx("Deleting phone call list..."))
            try:
                self._api._voip.delete_call()
            except Exception as e:
                self.display_error(str(e))
                return
            finally:
                self._task.end()

            self.refresh_call_button_click()


    ### Double click on a call to add/edit corresponding contact
    def edit_contact_from_call_list_click(self):
        current_selection = self._call_list.currentRow()
        if current_selection >= 0:
            name = self._call_list.item(current_selection, CallCol.Contact).text()
            n = self._contact_list.rowCount()

            # Try first to find the contact by phone number
            raw_phone_nb = self._call_list.item(current_selection, CallCol.Number).text()
            phone_nb  = LmPhone.intl_phone_number(raw_phone_nb)
            if phone_nb:
                for i in range(n):
                    if ((LmPhone.intl_phone_number(self._contact_list.item(i, ContactCol.Cell).text()) == phone_nb) or
                        (LmPhone.intl_phone_number(self._contact_list.item(i, ContactCol.Home).text()) == phone_nb) or
                        (LmPhone.intl_phone_number(self._contact_list.item(i, ContactCol.Work).text()) == phone_nb)):
                        self.edit_contact_dialog(i)
                        return

            # Then try to find the contact by name
            if name:
                for i in range(n):
                    if self._contact_list.item(i, ContactCol.Name).text() == name:
                        self.edit_contact_dialog(i)
                        return

            # If not found then propose to create a contact from phone call data
            contact = {}
            sep = name.find(" ")
            if sep > 0:
                contact["name"] = name[0:sep]
                contact["firstname"] = name[sep + 1:]
            else:
                contact["name"] = name
                contact["firstname"] = ""
            contact["cell"] = raw_phone_nb
            contact["home"] = ""
            contact["work"] = ""
            contact["ringtone"] = "1"
            self.add_contact_dialog(contact)


    ### Load phone call list
    def load_call_list(self):
        self._task.start(lx("Loading phone call list..."))

        self._call_list.setSortingEnabled(False)

        try:
            call_list = self._api._voip.get_call_list()
        except Exception as e:
            LmUtils.error(str(e))
            self.display_error(mx("Error getting phone call list.", "callLoad"))
        else:
            for i, c in enumerate(call_list):
                self._call_list.insertRow(i)

                key = QtWidgets.QTableWidgetItem(c.get("callId", ""))

                call_type_icon = NumericSortItem()
                status = c.get("callType", "")
                origin = c.get("callOrigin", "")
                if status == "succeeded":
                    if origin == "local":
                        call_type_icon.setIcon(QtGui.QIcon(LmIcon.CallOutPixmap))
                        call_type_icon.setData(QtCore.Qt.ItemDataRole.UserRole, CallType.Emitted)
                        missed_call = False
                    else:
                        call_type_icon.setIcon(QtGui.QIcon(LmIcon.CallInPixmap))
                        call_type_icon.setData(QtCore.Qt.ItemDataRole.UserRole, CallType.Received)
                        missed_call = False
                else:
                    if origin == "local":
                        call_type_icon.setIcon(QtGui.QIcon(LmIcon.CallFailedPixmap))
                        call_type_icon.setData(QtCore.Qt.ItemDataRole.UserRole, CallType.Failed)
                        missed_call = False
                    else:
                        call_type_icon.setIcon(QtGui.QIcon(LmIcon.CallMissedPixmap))
                        call_type_icon.setData(QtCore.Qt.ItemDataRole.UserRole, CallType.Missed)
                        missed_call = True

                time = QtWidgets.QTableWidgetItem(LmUtils.fmt_livebox_timestamp(c.get("startTime")))
                time.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                number = QtWidgets.QTableWidgetItem(c.get("remoteNumber"))
                number.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                contact_str = c.get("remoteName")
                contact_source = QtWidgets.QTableWidgetItem(Source.Livebox if contact_str else Source.NoSource)
                contact = QtWidgets.QTableWidgetItem(contact_str)

                seconds = c.get("duration")
                duration = NumericSortItem(LmUtils.fmt_time(seconds, True))
                duration.setData(QtCore.Qt.ItemDataRole.UserRole, seconds)
                duration.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

                if missed_call:
                    time.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    number.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    contact.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    duration.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))

                self._call_list.setItem(i, CallCol.Key, key)
                self._call_list.setItem(i, CallCol.Type, call_type_icon)
                self._call_list.setItem(i, CallCol.Time, time)
                self._call_list.setItem(i, CallCol.Number, number)
                self._call_list.setItem(i, CallCol.ContactSource, contact_source)
                self._call_list.setItem(i, CallCol.Contact, contact)
                self._call_list.setItem(i, CallCol.Duration, duration)

            self.assign_contact_to_calls()
            self.indicate_spam_calls()
        finally:
            self._call_list.sortItems(CallCol.Time, QtCore.Qt.SortOrder.DescendingOrder)

            self._call_list.setSortingEnabled(True)
            self.call_list_click()

            self._task.end()


    ### Assign contacts to calls via matching context
    def assign_contact_to_calls(self):
        self._call_list.setSortingEnabled(False)

        try:
            for i in range(self._call_list.rowCount()):
                if self._call_list.item(i, CallCol.ContactSource).text() != Source.Livebox:
                    phone_nb = LmPhone.intl_phone_number(self._call_list.item(i, CallCol.Number).text())
                    contact_name = self.find_matching_contact(phone_nb)
                    if contact_name is not None:
                        contact_source = QtWidgets.QTableWidgetItem(Source.Program)
                        foreground = self._call_list.item(i, CallCol.Contact).foreground()
                        contact = QtWidgets.QTableWidgetItem(contact_name)
                        contact.setForeground(foreground)
                        self._call_list.setItem(i, CallCol.ContactSource, contact_source)
                        self._call_list.setItem(i, CallCol.Contact, contact)
        finally:
            self._call_list.setSortingEnabled(True)


    ### Assign spam contact name to all calls in the spam table
    def indicate_spam_calls(self):
        self._call_list.setSortingEnabled(False)

        try:
            for i in range(self._call_list.rowCount()):
                call_type = self._call_list.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
                if (((call_type == CallType.Missed) or (call_type == CallType.Received)) and
                    self._call_list.item(i, CallCol.ContactSource).text() == Source.NoSource):
                    phone_nb = LmPhone.intl_phone_number(self._call_list.item(i, CallCol.Number).text())
                    if phone_nb in LmConf.SpamCallsTable:
                        self.display_spam_call(i)
        finally:
            self._call_list.setSortingEnabled(True)


    ### Scan call list to detect spams via CallFilter API
    def scan_spams(self):
        self._call_list.setSortingEnabled(False)

        try:
            spam_count = 0
            already_checked = []
            for i in range(self._call_list.rowCount()):
                call_type = self._call_list.item(i, CallCol.Type).data(QtCore.Qt.ItemDataRole.UserRole)
                if (((call_type == CallType.Missed) or (call_type == CallType.Received)) and
                    self._call_list.item(i, CallCol.ContactSource).text() == Source.NoSource):
                    raw_phone_nb = self._call_list.item(i, CallCol.Number).text()
                    full_phone_nb = LmPhone.intl_phone_number(raw_phone_nb)
                    if full_phone_nb not in already_checked:
                        already_checked.append(full_phone_nb)
                        phone_nb = LmPhone.intl_phone_number(raw_phone_nb, False)
                        if LmPhone.is_spam(phone_nb):
                            LmConf.set_spam_call(full_phone_nb)
                            spam_count += 1
        finally:
            self._call_list.setSortingEnabled(True)

        if spam_count:
            self.indicate_spam_calls()
        self.display_status(mx("Number of detected spam numbers: {}.", "spamCount").format(spam_count))


    ### Assign spam contact name to calls in the spam table
    def display_spam_call(self, index, spam=True):
        if spam:
            source = Source.Spam
            name = SPAM_CONTACT_NAME
        else:
            source = Source.NoSource
            name = ""
        contact_source = QtWidgets.QTableWidgetItem(source)
        foreground = self._call_list.item(index, CallCol.Contact).foreground()
        contact = QtWidgets.QTableWidgetItem(name)
        contact.setForeground(foreground)
        self._call_list.setItem(index, CallCol.ContactSource, contact_source)
        self._call_list.setItem(index, CallCol.Contact, contact)


    ### Check if number is spam via CallFilter API
    @staticmethod
    def is_spam(phone_number):
        if LmConf.CallFilterApiKey and phone_number:
            try:
                resp = requests.get(CALLFILTER_URL.format(LmConf.CallFilterApiKey, phone_number), timeout=2)
                resp.raise_for_status()     # Check HTTP status code
                data = resp.json()
                spam = data.get("blocked")
                if spam is not None:
                    return spam != 0
                LmUtils.error("CallFilter response error: no blocked field")
            except Exception as e:
                LmUtils.error(f"CallFilter error: {e}")
        return False


    ### Click on contact list refresh button
    def refresh_contact_button_click(self):
        self._contact_list.clearContents()
        self._contact_list.setRowCount(0)
        self.load_contact_list()


    ### Click on add contact button
    def add_contact_button_click(self):
        self.add_contact_dialog(None)


    ### Click on edit contact button
    def edit_contact_button_click(self):
        current_selection = self._contact_list.currentRow()
        if current_selection >= 0:
            self.edit_contact_dialog(current_selection)
        else:
            self.display_error(mx("Please select a contact.", "contactSelect"))


    ### Click on delete contact button
    def delete_contact_button_click(self):
        current_selection = self._contact_list.currentRow()
        if current_selection >= 0:
            key = self._contact_list.item(current_selection, ContactCol.Key).text()
            try:
                self._api._voip.delete_contact(key)
            except Exception as e:
                self.display_error(str(e))
                return

            contact = self.get_contact_row(current_selection)
            self.rmv_contact_from_matching_index(contact)
            self._contact_list.removeRow(current_selection)
            self.assign_contact_to_calls()
        else:
            self.display_error(mx("Please select a contact.", "contactSelect"))


    ### Click on delete all contacts button
    def delete_all_contacts_button_click(self):
        if self.ask_question(mx("Are you sure you want to delete all contacts?", "delAllContacts")):
            self._task.start(lx("Deleting contact list..."))
            try:
                self._api._voip.delete_contact()
            except Exception as e:
                self.display_error(str(e))
                return
            finally:
                self._task.end()

            self.refresh_contact_button_click()


    ### Click on Phone Ring button
    def phone_ring_button_click(self):
        ringtone = self._ringtone_combo.currentText()
        if ringtone == "-":
            ringtone = None

        self._task.start()
        try:
            self._api._voip.ring(ringtone)
            self.display_status(mx("Phone should be ringing.", "ring"))
        except Exception as e:
            self.display_error(str(e))
        finally:
            self._task.end()


    ### Click on export contacts button
    def export_contacts_button_click(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, lx("Export File"), lx("Livebox Contacts") + ".vcf", "*.vcf")[0]
        if not file_name:
            return

        try:
            export_file = open(file_name, "w", encoding="utf-8")  # VCF standard charset is UTF-8
        except Exception as e:
            LmUtils.error(str(e))
            self.display_error(mx("Cannot create the file.", "createFileErr"))
            return

        self._task.start(lx("Exporting all contacts..."))
        try:
            contact_list = self._api._voip.get_contact_list()
        except Exception as e:
            LmUtils.error(str(e))
            self.display_error(mx("Error getting contact list.", "contactLoad"))
        else:
            for c in contact_list:
                contact = self.decode_livebox_contact(c)
                export_file.write("BEGIN:VCARD\n")
                export_file.write("VERSION:3.0\n")
                export_file.write(f"PRODID:{self._application_name}\n")
                export_file.write(f"FN:{contact['formattedName']}\n")
                export_file.write(f"N:{contact['name']};{contact['firstname']};;;\n")
                export_file.write(f"TEL;TYPE=CELL:{contact['cell']}\n")
                export_file.write(f"TEL;TYPE=HOME:{contact['home']}\n")
                export_file.write(f"TEL;TYPE=WORK:{contact['work']}\n")
                export_file.write(f"RINGTONE:{contact['ringtone']}\n")
                export_file.write("END:VCARD\n")
        finally:
            self._task.end()

        try:
            export_file.close()
        except Exception as e:
            LmUtils.error(str(e))
            self.display_error(mx("Cannot save the file.", "saveFileErr"))


    ### Click on import contacts button
    def import_contacts_button_click(self):
        files = QtWidgets.QFileDialog.getOpenFileNames(self, lx("Select files to import"), "", "*.vcf")[0]

        self._task.start(lx("Importing contacts..."))
        self._contact_list.setSortingEnabled(False)

        try:
            file_error = []
            for f in files:
                result = self.import_vcf_file(f)
                if result == 0:
                    file_error.append(os.path.basename(f))
                elif result < 0:
                    break
            self.assign_contact_to_calls()
        finally:
            self._contact_list.setSortingEnabled(True)
            self._task.end()

        if file_error:
            self.display_error(f"{lx('Cannot import file(s):')} {', '.join(file_error)}.")


    ### VCF file import, returns: 1=Success, 0=File error, -1=Stop all error
    def import_vcf_file(self, file):
        try:
            f = open(file, "r", encoding="utf-8")    # VCF standard charset is UTF-8
        except Exception:
            return 0

        c = None
        try:
            for l in f:
                # Get tag structure
                i = l.find(":")
                if i < 1:
                    continue
                tag_struct = l[:i].upper()
                l = l[i + 1:].rstrip("\n")

                # Some tags are build like "item1.TEL;...", remove to ease parsing
                if tag_struct.startswith("ITEM"):
                    i = tag_struct.find(".")
                    if i >= 0:
                        tag_struct = tag_struct[i + 1:]

                # Decode tag structure to get tag name and its parameters
                tag_elems = tag_struct.split(";")
                tag = None
                tag_params = {}
                for e in tag_elems:
                    if tag is None:
                        tag = e
                    else:
                        i = e.find("=")
                        if i >= 0:
                            tag_params[e[:i]] = e[i + 1:]
                        else:
                            tag_params[e] = ""

                match tag:
                    case "BEGIN":
                        # Create a blank contact
                        if l.upper() == "VCARD":
                            c = {"firstname": "",
                                 "name": "",
                                 "formattedName": "",
                                 "cell": "",
                                 "home": "",
                                 "work": "",
                                 "ringtone": "1"}
                    case "END":
                        # Import the decoded contact
                        if (l.upper() == "VCARD") and (c is not None):
                            if self.add_livebox_contact(c):
                                self._contact_list.insertRow(0)
                                self.set_contact_row(0, c)
                                self.add_contact_to_matching_index(c)
                                QtCore.QCoreApplication.processEvents()
                            else:
                                f.close()
                                return -1
                            c = None
                    case _:
                        LmPhone.import_vcf_tag(c, tag, tag_params, l)
        except Exception as e:
            LmUtils.error(str(e))
            f.close()
            return 0

        f.close()
        return 1


    ### VCF tag import
    @staticmethod
    def import_vcf_tag(contact, tag, params, val):
        if contact is None:
            return

        # Name tag
        match tag:
            case "N":
                # Replace semicolon escape sequences by spaces
                val = val.replace(r"\;", " ")

                # Get name & firstname
                s = val.split(";")
                if len(s) > 1:
                    contact["name"]  = s[0].strip()
                    contact["firstname"] = s[1].strip()
                else:
                    contact["name"]  = s[0].strip()
                    contact["firstname"] = ""
                contact["formattedName"] = EditContactDialog.compute_formatted_name(contact["name"], contact["firstname"])

            # Phone number tag
            case "TEL":
                # Get type, use cell if none specified
                number_type = params.get("TYPE", "CELL")

                # Assign the phone number according to its type
                match number_type:
                    case "HOME":
                        contact["home"] = LmPhone.vcf_phone_number_cleanup(val)
                    case "WORK":
                        contact["work"] = LmPhone.vcf_phone_number_cleanup(val)
                    case _:
                        contact["cell"] = LmPhone.vcf_phone_number_cleanup(val)

            # Ring tone tag (not standard)
            case "RINGTONE":
                if (len(val) == 1) and (val in "1234567"):
                    contact["ringtone"] = val


    ### VCF phone number cleanup
    @staticmethod
    def vcf_phone_number_cleanup(phone_number):
        if phone_number and (phone_number[0] == "+"):
            n = "00"
            phone_number = phone_number[1:]
        else:
            n = ""

        for c in phone_number:
            if c in r"0123456789*#":
                n += c

        return n


    ### Convert phone numbers to intl format if local
    @staticmethod
    def intl_phone_number(phone_number, full=True):
        if ((len(phone_number) < 2) or
            phone_number.startswith("00") or
            (phone_number[0] != "0")):
            return phone_number

        if full:
            return f"00{LmConf.PhoneCode}{phone_number[1:]}"
        return f"{LmConf.PhoneCode}{phone_number[1:]}"


    ### Load contact list
    def load_contact_list(self):
        self._task.start(lx("Loading contact list..."))
        self._contact_list.setSortingEnabled(False)
        self._contact_matching = {}
        try:
            contact_list = self._api._voip.get_contact_list()
        except Exception as e:
            LmUtils.error(str(e))
            self.display_error(mx("Error getting contact list.", "contactLoad"))
        else:
            for i, c in enumerate(contact_list):
                self._contact_list.insertRow(i)
                contact = self.decode_livebox_contact(c)
                self.set_contact_row(i, contact)
                self.add_contact_to_matching_index(contact)

            self._contact_list.sortItems(ContactCol.Name, QtCore.Qt.SortOrder.AscendingOrder)

            self.assign_contact_to_calls()
            self.contact_list_click()
        finally:
            self._contact_list.setSortingEnabled(True)
            self._task.end()


    ### Get contact from Livebox contact structure
    def decode_livebox_contact(self, livebox_contact):
        contact = {}
        contact["key"] = livebox_contact.get("uniqueID", "")

        name = livebox_contact.get("name", "")
        s = name.split(";")
        if len(s) > 1:
            contact["name"] = s[0][2:]
            contact["firstname"] = s[1]
        else:
            contact["name"]  = ""
            contact["firstname"] = ""

        contact["formattedName"] = livebox_contact.get("formattedName", "")

        contact["cell"] = ""
        contact["home"] = ""
        contact["work"] = ""
        numbers = livebox_contact.get("telephoneNumbers")
        if isinstance(numbers, list):
            for n in numbers:
                number_type = n.get("type", "")
                match number_type:
                    case "CELL":
                        contact["cell"] = n.get("name", "")
                    case "HOME":
                        contact["home"] = n.get("name", "")
                    case "WORK":
                        contact["work"] = n.get("name", "")

        contact["ringtone"] = livebox_contact.get("ringtone", "1")

        return contact


    ### Set contact row
    def set_contact_row(self, line, contact):
        key = QtWidgets.QTableWidgetItem(contact["key"])

        contact_name = QtWidgets.QTableWidgetItem(contact["formattedName"])

        cell_nb = QtWidgets.QTableWidgetItem(contact["cell"])
        cell_nb.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        home_nb = QtWidgets.QTableWidgetItem(contact["home"])
        home_nb.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        work_nb = QtWidgets.QTableWidgetItem(contact["work"])
        work_nb.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        ringtone = QtWidgets.QTableWidgetItem(contact["ringtone"])
        ringtone.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self._contact_list.setItem(line, ContactCol.Key, key)
        self._contact_list.setItem(line, ContactCol.Name, contact_name)
        self._contact_list.setItem(line, ContactCol.Cell, cell_nb)
        self._contact_list.setItem(line, ContactCol.Home, home_nb)
        self._contact_list.setItem(line, ContactCol.Work, work_nb)
        self._contact_list.setItem(line, ContactCol.Ring, ringtone)


    ### Get contact from row
    def get_contact_row(self, line):
        return {"key": self._contact_list.item(line, ContactCol.Key).text(),
                "formattedName": self._contact_list.item(line, ContactCol.Name).text(),
                "cell": self._contact_list.item(line, ContactCol.Cell).text(),
                "home": self._contact_list.item(line, ContactCol.Home).text(),
                "work": self._contact_list.item(line, ContactCol.Work).text(),
                "ringtone": self._contact_list.item(line, ContactCol.Ring).text()}


    ### Add contact dialog
    def add_contact_dialog(self, default_contact_data):
        dialog = EditContactDialog(False, default_contact_data, self)
        if dialog.exec():
            contact = dialog.get_contact()
            if self.add_livebox_contact(contact):
                self._contact_list.setSortingEnabled(False)
                self._contact_list.insertRow(0)
                self.set_contact_row(0, contact)
                self._contact_list.setSortingEnabled(True)
                self.add_contact_to_matching_index(contact)
                self.assign_contact_to_calls()


    ### Add a contact in Livebox, returns False if failed
    def add_livebox_contact(self, contact):
        livebox_contact = {
            "name": f"N:{contact['name']};{contact['firstname']};",
            "formattedName": contact["formattedName"],
            "ringtone": contact["ringtone"],
            "telephoneNumbers": [
                {
                    "name": contact["cell"],
                    "type": "CELL",
                    "preferred": False
                },
                {
                    "name": contact["work"],
                    "type": "WORK",
                    "preferred": False
                },
                {
                    "name": contact["home"],
                    "type": "HOME",
                    "preferred": False
                }
            ]
        }

        try:
            key = self._api._voip.add_contact(livebox_contact)
        except Exception as e:
            self.display_error(str(e))
            return False

        if key is None:
            self.display_error(mx("Max number of contacts reached.", "contactMax"))
            return False

        contact["key"] = key
        return True


    ### Edit contact dialog
    def edit_contact_dialog(self, line):
        key = self._contact_list.item(line, ContactCol.Key).text()

        # First retrieve a fresh copy of the contact
        try:
            livebox_contact = self._api._voip.get_contact(key)
        except Exception as e:
            self.display_error(str(e))
            return
        if not livebox_contact:
            self.display_error(mx("Cannot retrieve contact.", "contactGet"))
            return
        contact = self.decode_livebox_contact(livebox_contact)

        # Edit dialog
        dialog = EditContactDialog(True, contact, self)
        if dialog.exec():
            contact = dialog.get_contact()
            livebox_contact = {
                "name": f"N:{contact['name']};{contact['firstname']};",
                "n": f"N:{contact['name']};{contact['firstname']};;;;;;;",
                "formattedName": contact["formattedName"],
                "ringtone": contact["ringtone"],
                "telephoneNumbers": [
                    {
                        "name": contact["cell"],
                        "type": "CELL",
                        "preferred": False
                    },
                    {
                        "name": contact["work"],
                        "type": "WORK",
                        "preferred": False
                    },
                    {
                        "name": contact["home"],
                        "type": "HOME",
                        "preferred": False
                    }
                ]
            }

            # Perform updates
            try:
                self._api._voip.change_contact(key,livebox_contact )
            except Exception as e:
                self.display_error(str(e))
                return

            current_contact = self.get_contact_row(line)
            self.rmv_contact_from_matching_index(current_contact)
            self._contact_list.setSortingEnabled(False)
            self.set_contact_row(line, contact)
            self._contact_list.setSortingEnabled(True)
            self.add_contact_to_matching_index(contact)
            self.assign_contact_to_calls()


    ### Add contact to matching index
    def add_contact_to_matching_index(self, contact):
        contact_entry = { "key": contact["key"], "name": contact["formattedName"] }
        self.add_number_to_matching_index(LmPhone.intl_phone_number(contact["cell"]), contact_entry)
        self.add_number_to_matching_index(LmPhone.intl_phone_number(contact["work"]), contact_entry)
        self.add_number_to_matching_index(LmPhone.intl_phone_number(contact["home"]), contact_entry)


    ### Remove contact from matching index
    def rmv_contact_from_matching_index(self, contact):
        contact_entry = { "key": contact["key"], "name": contact["formattedName"] }
        self.rmv_number_from_matching_index(LmPhone.intl_phone_number(contact["cell"]), contact_entry)
        self.rmv_number_from_matching_index(LmPhone.intl_phone_number(contact["work"]), contact_entry)
        self.rmv_number_from_matching_index(LmPhone.intl_phone_number(contact["home"]), contact_entry)


    ### Add a phone number to matching index
    def add_number_to_matching_index(self, phone_number, contact_entry):
        if phone_number:
            phone_entry = self._contact_matching.get(phone_number)
            if phone_entry is None:
                self._contact_matching[phone_number] = [contact_entry]
            else:
                self._contact_matching[phone_number].append(contact_entry)


    ### Remove a phone number from matching index
    def rmv_number_from_matching_index(self, phone_number, contact_entry):
        if phone_number:
            phone_entry = self._contact_matching.get(phone_number)
            if phone_entry is not None:
                try:
                    self._contact_matching[phone_number].remove(contact_entry)
                except Exception:
                    pass


    ### Find a contact name matching a phone number
    def find_matching_contact(self, phone_number):
        if phone_number:
            phone_entry = self._contact_matching.get(phone_number)
            if phone_entry is not None:
                n = len(phone_entry)
                if n:
                    return phone_entry[n - 1]["name"]
        return None
