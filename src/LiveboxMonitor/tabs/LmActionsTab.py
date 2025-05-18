### Livebox Monitor actions tab module ###

import json
import webbrowser

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmGenApiDocumentation
from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmConfig import LmConf, set_application_style
from LiveboxMonitor.dlg.LmPrefs import PrefsDialog
from LiveboxMonitor.dlg.LmEmailSetup import EmailSetupDialog
from LiveboxMonitor.dlg.LmWifiConfig import WifiConfigDialog
from LiveboxMonitor.dlg.LmWifiGlobalStatus import WifiGlobalStatusDialog
from LiveboxMonitor.dlg.LmRebootHistory import RebootHistoryDialog
from LiveboxMonitor.dlg.LmFirewall import FirewallLevelDialog
from LiveboxMonitor.dlg.LmPingResponse import PingResponseDialog
from LiveboxMonitor.dlg.LmDynDns import DynDnsSetupDialog
from LiveboxMonitor.dlg.LmDmz import DmzSetupDialog
from LiveboxMonitor.dlg.LmBackupRestore import BackupRestoreDialog
from LiveboxMonitor.dlg.LmScreen import ScreenDialog
from LiveboxMonitor.lang.LmLanguages import get_actions_label as lx, get_actions_message as mx

from LiveboxMonitor.__init__ import __url__, __copyright__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'actionTab'

# Static Config
BUTTON_WIDTH = 150


# ################################ LmActions class ################################
class LmActions:

    ### Create actions tab
    def create_actions_tab(self):
        self._actions_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Wifi & Misc column
        left_zone = QtWidgets.QVBoxLayout()
        left_zone.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        left_zone.setSpacing(20)

        # Wifi buttons group
        wifi_buttons = QtWidgets.QVBoxLayout()
        wifi_buttons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        wifi_buttons.setSpacing(20)

        wifi_set = QtWidgets.QHBoxLayout()
        wifi_set.setSpacing(20)

        wifi_config_button = QtWidgets.QPushButton(lx('Configuration...'), objectName='wifiConfig')
        wifi_config_button.clicked.connect(self.wifi_config_button_click)
        wifi_config_button.setMinimumWidth(BUTTON_WIDTH)
        wifi_set.addWidget(wifi_config_button)

        wifi_on_button = QtWidgets.QPushButton(lx('Wifi ON'), objectName='wifiOn')
        wifi_on_button.clicked.connect(self.wifi_on_button_click)
        wifi_set.addWidget(wifi_on_button)

        wifi_off_button = QtWidgets.QPushButton(lx('Wifi OFF'), objectName='wifiOff')
        wifi_off_button.clicked.connect(self.wifi_off_button_click)
        wifi_set.addWidget(wifi_off_button)
        wifi_buttons.addLayout(wifi_set, 0)

        guest_wifi_set = QtWidgets.QHBoxLayout()
        guest_wifi_set.setSpacing(20)

        wifi_guest_config_button = QtWidgets.QPushButton(lx('Guest...'), objectName='wifiGuestConfig')
        wifi_guest_config_button.clicked.connect(self.wifi_guest_config_button_click)
        wifi_guest_config_button.setMinimumWidth(BUTTON_WIDTH)
        guest_wifi_set.addWidget(wifi_guest_config_button)

        guest_wifi_on_button = QtWidgets.QPushButton(lx('Guest ON'), objectName='guestWifiOn')
        guest_wifi_on_button.clicked.connect(self.guest_wifi_on_button_click)
        guest_wifi_set.addWidget(guest_wifi_on_button)

        guest_wifi_off_button = QtWidgets.QPushButton(lx('Guest OFF'), objectName='guestWifiOff')
        guest_wifi_off_button.clicked.connect(self.guest_wifi_off_button_click)
        guest_wifi_set.addWidget(guest_wifi_off_button)
        wifi_buttons.addLayout(guest_wifi_set, 0)

        scheduler_set = QtWidgets.QHBoxLayout()
        scheduler_set.setSpacing(20)

        scheduler_on_button = QtWidgets.QPushButton(lx('Wifi Scheduler ON'), objectName='schedulerOn')
        scheduler_on_button.clicked.connect(self.scheduler_on_button_click)
        scheduler_on_button.setMinimumWidth(BUTTON_WIDTH)
        scheduler_set.addWidget(scheduler_on_button)

        scheduler_off_button = QtWidgets.QPushButton(lx('Wifi Scheduler OFF'), objectName='schedulerOff')
        scheduler_off_button.clicked.connect(self.scheduler_off_button_click)
        scheduler_off_button.setMinimumWidth(BUTTON_WIDTH)
        scheduler_set.addWidget(scheduler_off_button)
        wifi_buttons.addLayout(scheduler_set, 0)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        wifi_buttons.addWidget(separator)

        wifi_global_status_button = QtWidgets.QPushButton(lx('Show Global Status...'), objectName='wifiGlobalStatus')
        wifi_global_status_button.clicked.connect(self.wifi_global_status_button_click)
        wifi_buttons.addWidget(wifi_global_status_button)

        wifi_group_box = QtWidgets.QGroupBox(lx('Wifi'), objectName='wifiGroup')
        wifi_group_box.setLayout(wifi_buttons)
        left_zone.addWidget(wifi_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Misc buttons
        misc_buttons = QtWidgets.QVBoxLayout()
        misc_buttons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        misc_buttons.setSpacing(20)

        backup_restore_button = QtWidgets.QPushButton(lx('Backup and Restore...'), objectName='backupRestore')
        backup_restore_button.clicked.connect(self.backup_restore_button_click)
        backup_restore_button.setMinimumWidth(BUTTON_WIDTH)
        misc_buttons.addWidget(backup_restore_button)

        screen_button = QtWidgets.QPushButton(lx('LEDs and Screen...'), objectName='screen')
        screen_button.clicked.connect(self.screen_button_click)
        screen_button.setMinimumWidth(BUTTON_WIDTH)
        misc_buttons.addWidget(screen_button)
        if self._liveboxModel < 6:
            screen_button.setEnabled(False)

        misc_group_box = QtWidgets.QGroupBox(lx('Miscellaneous'), objectName='miscGroup')
        misc_group_box.setLayout(misc_buttons)
        left_zone.addWidget(misc_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Reboot & Firewall column
        middle_zone = QtWidgets.QVBoxLayout()
        middle_zone.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        middle_zone.setSpacing(20)

        # Reboot buttons
        reboot_buttons = QtWidgets.QVBoxLayout()
        reboot_buttons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        reboot_buttons.setSpacing(20)

        reboot_livebox_button = QtWidgets.QPushButton(lx('Reboot Livebox...'), objectName='rebootLivebox')
        reboot_livebox_button.clicked.connect(self.reboot_livebox_button_click)
        reboot_livebox_button.setMinimumWidth(BUTTON_WIDTH)
        reboot_buttons.addWidget(reboot_livebox_button)

        reboot_history_button = QtWidgets.QPushButton(lx('Reboot History...'), objectName='rebootHistory')
        reboot_history_button.clicked.connect(self.reboot_history_button_click)
        reboot_history_button.setMinimumWidth(BUTTON_WIDTH)
        reboot_buttons.addWidget(reboot_history_button)

        reboot_group_box = QtWidgets.QGroupBox(lx('Reboots'), objectName='rebootGroup')
        reboot_group_box.setLayout(reboot_buttons)
        middle_zone.addWidget(reboot_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Network buttons
        network_buttons = QtWidgets.QVBoxLayout()
        network_buttons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        network_buttons.setSpacing(20)

        firewall_level_button = QtWidgets.QPushButton(lx('Firewall Levels...'), objectName='firewallLevel')
        firewall_level_button.clicked.connect(self.firewall_level_button_click)
        firewall_level_button.setMinimumWidth(BUTTON_WIDTH)
        network_buttons.addWidget(firewall_level_button)

        ping_response_button = QtWidgets.QPushButton(lx('Ping Responses...'), objectName='pingResponse')
        ping_response_button.clicked.connect(self.ping_response_button_click)
        ping_response_button.setMinimumWidth(BUTTON_WIDTH)
        network_buttons.addWidget(ping_response_button)

        dyndns_button = QtWidgets.QPushButton(lx('DynDNS...'), objectName='dynDNS')
        dyndns_button.clicked.connect(self.dyndns_button_click)
        dyndns_button.setMinimumWidth(BUTTON_WIDTH)
        network_buttons.addWidget(dyndns_button)

        dmz_button = QtWidgets.QPushButton(lx('DMZ...'), objectName='dmz')
        dmz_button.clicked.connect(self.dmz_button_click)
        dmz_button.setMinimumWidth(BUTTON_WIDTH)
        network_buttons.addWidget(dmz_button)

        network_group_box = QtWidgets.QGroupBox(lx('Network'), objectName='networkGroup')
        network_group_box.setLayout(network_buttons)
        middle_zone.addWidget(network_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # About, preferences, debug and quit column
        right_zone = QtWidgets.QVBoxLayout()

        # About box
        about_widgets = QtWidgets.QVBoxLayout()
        about_widgets.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        about_widgets.setSpacing(15)

        app_icon = QtWidgets.QLabel(objectName='appIcon')
        app_icon.setPixmap(LmIcon.AppIconPixmap)
        app_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        app_icon.setMaximumWidth(64)
        app_icon.setMinimumWidth(64)
        about_widgets.addWidget(app_icon, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        app_name = QtWidgets.QLabel(self._applicationName, objectName='appName')
        app_name.setFont(LmTools.BOLD_FONT)
        about_widgets.addWidget(app_name, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        about_widgets.addWidget(QtWidgets.QLabel(lx('An Open Source project')), 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        open_source_url = QtWidgets.QLabel(__url__, objectName='openSourceURL')
        open_source_url.setStyleSheet('QLabel { color : blue }')
        open_source_url.mousePressEvent = self.open_source_button_click
        about_widgets.addWidget(open_source_url, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        about_widgets.addWidget(QtWidgets.QLabel(__copyright__), 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        about_group_box = QtWidgets.QGroupBox(lx('About'), objectName='aboutGroup')
        about_group_box.setLayout(about_widgets)

        right_zone.addWidget(about_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Setup box
        setup_buttons = QtWidgets.QVBoxLayout()
        setup_buttons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        setup_buttons.setSpacing(15)

        prefs_button = QtWidgets.QPushButton(lx('Preferences...'), objectName='prefs')
        prefs_button.clicked.connect(self.prefs_button_click)
        setup_buttons.addWidget(prefs_button)

        change_profile_button = QtWidgets.QPushButton(lx('Change Profile...'), objectName='changeProfile')
        change_profile_button.clicked.connect(self.change_profile_button_click)
        setup_buttons.addWidget(change_profile_button)

        email_setup_button = QtWidgets.QPushButton(lx('Email Setup...'), objectName='emailSetup')
        email_setup_button.clicked.connect(self.email_setup_button_click)
        setup_buttons.addWidget(email_setup_button)

        setup_group_box = QtWidgets.QGroupBox(lx('Setup'), objectName='setupGroup')
        setup_group_box.setLayout(setup_buttons)

        right_zone.addWidget(setup_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Debug box
        debug_buttons = QtWidgets.QVBoxLayout()
        debug_buttons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        debug_buttons.setSpacing(10)

        show_raw_device_list_button = QtWidgets.QPushButton(lx('Raw Device List...'), objectName='showRawDeviceList')
        show_raw_device_list_button.clicked.connect(self.show_raw_device_list_button_click)
        debug_buttons.addWidget(show_raw_device_list_button)
        show_raw_topology_button = QtWidgets.QPushButton(lx('Raw Topology...'), objectName='showRawTopology')
        show_raw_topology_button.clicked.connect(self.show_raw_topology_button_click)
        debug_buttons.addWidget(show_raw_topology_button)
        set_log_level_button = QtWidgets.QPushButton(lx('Set Log Level...'), objectName='setLogLevel')
        set_log_level_button.clicked.connect(self.set_log_level_button_click)
        debug_buttons.addWidget(set_log_level_button)
        gen_doc_button = QtWidgets.QPushButton(lx('Generate API Documentation...'), objectName='getApiDoc')
        gen_doc_button.clicked.connect(self.get_doc_button_click)
        debug_buttons.addWidget(gen_doc_button)
        if self._liveboxModel > 7:      # API doc generation is blocked since LB W7
            gen_doc_button.setEnabled(False)

        debug_group_box = QtWidgets.QGroupBox(lx('Debug'), objectName='debugGroup')
        debug_group_box.setLayout(debug_buttons)

        right_zone.addWidget(debug_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Quit button
        quit_button = QtWidgets.QPushButton(lx('Quit Application'), objectName='quit')
        quit_button.clicked.connect(self.quit_button_click)
        quit_button.setMinimumWidth(BUTTON_WIDTH)
        right_zone.addWidget(quit_button, 1, QtCore.Qt.AlignmentFlag.AlignBottom)

        # Layout
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        hbox.setSpacing(40)
        hbox.addLayout(left_zone, 1)
        hbox.addLayout(middle_zone, 1)
        hbox.addLayout(right_zone, 1)
        self._actions_tab.setLayout(hbox)

        LmConfig.set_tooltips(self._actions_tab, 'actions')
        self._tabWidget.addTab(self._actions_tab, lx('Actions'))


    ### Click on Wifi config button
    def wifi_config_button_click(self):
        self._task.start(lx('Getting Wifi Configuration...'))
        c = self._api._wifi.get_config()
        self._task.end()
        if (c is None) or (not len(c['Intf'])):
            self.display_error(mx('Something failed while trying to get wifi configuration.', 'wifiGetConfErr'))
        else:
            wifi_config_dialog = WifiConfigDialog(self, c, False)
            if wifi_config_dialog.exec():
                self._task.start(lx('Setting Wifi Configuration...'))
                n = wifi_config_dialog.get_config()
                if not self._api._wifi.set_config(c, n):
                    self.display_error(mx('Something failed while trying to set wifi configuration.', 'wifiSetConfErr'))
                self._task.end()


    ### Click on Wifi guest config button
    def wifi_guest_config_button_click(self):
        self._task.start(lx('Getting Guest Wifi Configuration...'))
        c = self._api._wifi.get_guest_config()
        self._task.end()
        if (c is None) or (not len(c['Intf'])):
            self.display_error(mx('Something failed while trying to get wifi configuration.', 'wifiGetConfErr'))
        else:
            wifi_config_dialog = WifiConfigDialog(self, c, True)
            if wifi_config_dialog.exec():
                self._task.start(lx('Setting Guest Wifi Configuration...'))
                n = wifi_config_dialog.get_config()
                if not self._api._wifi.set_guest_config(c, n):
                    self.display_error(mx('Something failed while trying to set wifi configuration.', 'wifiSetConfErr'))
                self._task.end()


    ### Click on Wifi ON button
    def wifi_on_button_click(self):
        self._task.start(lx('Activating Wifi...'))
        try:
            self._api._wifi.set_enable(True)
        except BaseException as e:
            self.display_error(str(e))
        else:
            self.display_status(mx('Wifi activated.', 'wifiOn'))
        self._task.end()


    ### Click on Wifi OFF button
    def wifi_off_button_click(self):
        self._task.start(lx('Deactivating Wifi...'))
        try:
            self._api._wifi.set_enable(False)
        except BaseException as e:
            self.display_error(str(e))
        else:
            self.display_status(mx('Wifi deactivated.', 'wifiOff'))
        self._task.end()


    ### Click on guest Wifi ON button
    def guest_wifi_on_button_click(self):
        self._task.start(lx('Activating Guest Wifi...'))
        try:
            self._api._wifi.set_guest_enable(True)
        except BaseException as e:
            self.display_error(str(e))
        else:
            self.display_status(mx('Guest Wifi activated. Reactivate Scheduler if required.', 'gwifiOn'))
        self._task.end()


    ### Click on guest Wifi OFF button
    def guest_wifi_off_button_click(self):
        self._task.start(lx('Deactivating Guest Wifi...'))
        try:
            self._api._wifi.set_guest_enable(False)
        except BaseException as e:
            self.display_error(str(e))
        else:
            self.display_status(mx('Guest Wifi deactivated.', 'gwifiOff'))
        self._task.end()


    ### Click on Scheduler ON button
    def scheduler_on_button_click(self):
        self._task.start(lx('Activating Wifi Scheduler...'))
        try:
            self._api._wifi.set_scheduler_enable(True)
        except BaseException as e:
            self.display_error(str(e))
        else:
            self.display_status(mx('Scheduler activated.', 'schedOn'))
        self._task.end()


    ### Click on Scheduler OFF button
    def scheduler_off_button_click(self):
        self._task.start(lx('Deactivating Wifi Scheduler...'))
        try:
            self._api._wifi.set_scheduler_enable(False)
        except BaseException as e:
            self.display_error(str(e))
        else:
            self.display_status(mx('Scheduler deactivated.', 'schedOff'))
        self._task.end()


    ### Click on Global Wifi Status button
    def wifi_global_status_button_click(self):
        self._task.start(lx('Getting Wifi Global Status...'))

        # Getting Livebox status
        livebox_status = self._api._wifi.get_global_wifi_status()

        # Getting Repeater statuses
        global_status = self.getRepeatersWifiStatus()
        global_status.insert(0, livebox_status)

        self._task.end()

        status_dialog = WifiGlobalStatusDialog(self, global_status, self._liveboxModel)
        status_dialog.exec()


    ### Click on the Backup & Restore button
    def backup_restore_button_click(self):
        backup_restore_dialog = BackupRestoreDialog(self)
        backup_restore_dialog.exec()


    ### Click on LEDs & Screen setup button
    def screen_button_click(self):
        try:
            orange_led_level = self._api._screen.get_orange_led_level()
            show_wifi_password = self._api._screen.get_show_wifi_password()
        except BaseException as e:
            self.display_error(str(e))
            return

        screen_dialog = ScreenDialog(orange_led_level, show_wifi_password, self)
        if screen_dialog.exec():
            self._task.start(lx('Setting LEDs & Screen Setup...'))

            # Set orange LED level if changed
            new_orange_led_level = screen_dialog.get_orange_led_level()
            if new_orange_led_level != orange_led_level:
                try:
                    self._api._screen.set_orange_led_level(new_orange_led_level)
                except BaseException as e:
                    self.display_error(str(e))

            # Set show wifi password if changed
            new_show_wifi_password = screen_dialog.get_show_wifi_password()
            if new_show_wifi_password != show_wifi_password:
                try:
                    self._api._screen.set_show_wifi_password(new_show_wifi_password)
                except BaseException as e:
                    self.display_error(str(e))

            self._task.end()


    ### Click on Reboot Livebox button
    def reboot_livebox_button_click(self):
        if self.ask_question(mx('Are you sure you want to reboot the Livebox?', 'lbReboot')):
            self._task.start(lx('Rebooting Livebox...'))
            try:
                self._api._reboot.reboot_livebox()
            except BaseException as e:
                self._task.end()
                self.display_error(str(e))
                return

            self._task.end()
            self.display_status(mx('Application will now quit.', 'appQuit'))
            self.close()


    ### Click on Reboot History button
    def reboot_history_button_click(self):
        self._task.start(lx('Getting Reboot History...'))

        try:
            d = self._api._reboot.get_reboot_history()
        except BaseException as e:
            self._task.end()
            self.display_error(str(e))
            return

        self._task.end()

        history_dialog = RebootHistoryDialog('Livebox', self)
        history_dialog.load_history(d)
        history_dialog.exec()


    ### Click on Firewall Level button
    def firewall_level_button_click(self):
        try:
            firewall_ipv4_level = self._api._firewall.get_ipv4_firewall_level()
            firewall_ipv6_level = self._api._firewall.get_ipv6_firewall_level()
        except BaseException as e:
            self.display_error(str(e))
            return

        firewall_level_dialog = FirewallLevelDialog(firewall_ipv4_level, firewall_ipv6_level, self)
        if firewall_level_dialog.exec():
            self._task.start(lx('Setting Firewall Levels...'))

            # Set new IPv4 firewall level if changed
            new_firewall_ipv4_level = firewall_level_dialog.get_ipv4_level()
            if new_firewall_ipv4_level != firewall_ipv4_level:
                try:
                    self._api._firewall.set_ipv4_firewall_level(new_firewall_ipv4_level)
                except BaseException as e:
                    self.display_error(str(e))

            # Set new IPv6 firewall level if changed
            new_firewall_ipv6_level = firewall_level_dialog.get_ipv6_level()
            if new_firewall_ipv6_level != firewall_ipv6_level:
                try:
                    self._api._firewall.set_ipv6_firewall_level(new_firewall_ipv6_level)
                except BaseException as e:
                    self.display_error(str(e))

            self._task.end()


    ### Click on Ping Response button
    def ping_response_button_click(self):
        # Get current ping reponses
        try:
            d = self._api._firewall.get_respond_to_ping()
        except BaseException as e:
            self.display_error(str(e))
            return
        ipv4_ping = d.get('enableIPv4')
        ipv6_ping = d.get('enableIPv6')
        if (ipv4_ping is None) or (ipv6_ping is None):
            LmTools.error('Cannot get respond to ping setup')

        ping_response_dialog = PingResponseDialog(ipv4_ping, ipv6_ping, self)
        if ping_response_dialog.exec():
            # Set new ping responses level if changed
            new_ipv4_ping = ping_response_dialog.get_ipv4()
            new_ipv6_ping = ping_response_dialog.get_ipv6()
            if (new_ipv4_ping != ipv4_ping) or (new_ipv6_ping != ipv6_ping):
                self._task.start(lx('Set Ping Responses...'))
                p = {}
                p['enableIPv4'] = new_ipv4_ping
                p['enableIPv6'] = new_ipv6_ping
                try:
                    self._api._firewall.set_respond_to_ping(p)
                except BaseException as e:
                    self.display_error(str(e))
                self._task.end()


    ### Click on DynDNS button
    def dyndns_button_click(self):
        dyndns_setup_dialog = DynDnsSetupDialog(self)
        dyndns_setup_dialog.exec()


    ### Click on DMZ button
    def dmz_button_click(self):
        dmz_setup_dialog = DmzSetupDialog(self)
        dmz_setup_dialog.exec()


    ### Open Source project web button
    def open_source_button_click(self, event):
        webbrowser.open_new_tab(__url__)


    ### Click on preferences button
    def prefs_button_click(self):
        prefs_dialog = PrefsDialog(self)
        if prefs_dialog.exec():
            LmConf.assign_profile()
            LmConf.save()
            LmConf.apply()
            set_application_style()
            self.resetUI()


    ### Change the current profile in use
    def change_profile_button_click(self):
        r = LmConf.ask_profile()
        if r == 1:
            LmConf.assign_profile()
            self.resetUI()
        elif r == 2:
            self.prefs_button_click()


    ### Click on email setup button
    def email_setup_button_click(self):
        email_setup_dialog = EmailSetupDialog(self)
        if email_setup_dialog.exec():
            LmConf.set_email_setup(email_setup_dialog.get_setup())
            LmConf.save()


    ### Click on show raw device list button
    def show_raw_device_list_button_click(self):
        self.display_infos(lx('Raw Device List'), json.dumps(self._liveboxDevices, indent=2))


    ### Click on show raw topology button
    def show_raw_topology_button_click(self):
        self.display_infos(lx('Raw Topology'), json.dumps(self._liveboxTopology, indent=2))


    ### Click on set log level button
    def set_log_level_button_click(self):
        levels = ['0', '1', '2']
        level, ok = QtWidgets.QInputDialog.getItem(None, lx('Log level selection'),
                                                   lx('Please select a log level:'),
                                                   levels, LmConf.LogLevel, False)
        if ok:
            LmConf.set_log_level(int(level))


    ### Click on generate API documentation button
    def get_doc_button_click(self):
        # Check Ctlr key to switch to filtering mode
        modifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
        filter_values = modifiers == QtCore.Qt.KeyboardModifier.ControlModifier

        folder = QtWidgets.QFileDialog.getExistingDirectory(self, lx('Select Export Folder'))
        if len(folder):
            folder = QtCore.QDir.toNativeSeparators(folder)

            # Check Ctlr key again to possibly switch to filtering mode
            if not filter_values:
                modifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
                filter_values = modifiers == QtCore.Qt.KeyboardModifier.ControlModifier

            self._task.start(lx('Generating API document files...'))
            g = LmGenApiDocumentation.LmGenApiDoc(self, folder, filter_values)
            g.gen_module_files()
            g.gen_full_file()
            g.gen_process_list_file()
            self._task.end()


    ### Click on Quit Application button
    def quit_button_click(self):
        self.close()
