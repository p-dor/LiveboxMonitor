#!/usr/bin/env python3
### Python program to monitor & administrate a Livebox 4, 5, 6, 7, W7 or S ###

import sys
import re
import traceback
import locale
import argparse

from PyQt6 import QtCore, QtGui, QtWidgets
from wakepy import keep, ActivationResult

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmTask import LmTask
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmConfig import LmConf, set_application_style, set_livebox_model, release_check
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.api.LmApiRegistry import ApiRegistry
from LiveboxMonitor.tabs import (LmDeviceListTab, LmInfoTab, LmGraphTab, LmDeviceInfoTab, LmEventsTab,
                                 LmDhcpTab, LmNatPatTab, LmPhoneTab, LmActionsTab, LmRepeaterTab)
from LiveboxMonitor.dlg.LmLiveboxCnx import LiveboxCnxDialog
from LiveboxMonitor.dlg.LmLiveboxSignin import LiveboxSigninDialog
from LiveboxMonitor.lang.LmLanguages import LANGUAGES_LOCALE, get_main_label as lx, get_main_message as mx

from LiveboxMonitor.__init__ import __version__


# ################################ VARS & DEFS ################################

# Static Config
NO_THREAD = False   # Use only to speed up testing while developping
TAB_ORDER = [
    LmDeviceListTab.TAB_NAME,
    LmInfoTab.TAB_NAME,
    LmGraphTab.TAB_NAME,
    LmDeviceInfoTab.TAB_NAME,
    LmEventsTab.TAB_NAME,
    LmDhcpTab.TAB_NAME,
    LmNatPatTab.TAB_NAME,
    LmPhoneTab.TAB_NAME,
    LmActionsTab.TAB_NAME
]


# ################################ APPLICATION ################################

# ############# Main window class #############
class LiveboxMonitorUI(QtWidgets.QMainWindow, LmDeviceListTab.LmDeviceList,
                                              LmInfoTab.LmInfo,
                                              LmGraphTab.LmGraph,
                                              LmDeviceInfoTab.LmDeviceInfo,
                                              LmEventsTab.LmEvents,
                                              LmDhcpTab.LmDhcp,
                                              LmNatPatTab.LmNatPat,
                                              LmPhoneTab.LmPhone,
                                              LmActionsTab.LmActions,
                                              LmRepeaterTab.LmRepeater):

    ### Initialize the application
    def __init__(self):
        super(LiveboxMonitorUI, self).__init__()
        self._task = LmTask(self)
        self._reset_flag = False
        self._app_ready = False
        self._status_bar = None
        self._repeaters = []
        if not NO_THREAD:
            self.initEventLoop()
            self.initWifiStatsLoop()
            self.initStatsLoop()
            self.initRepeaterStatsLoop()
        self._application_name = 'Livebox Monitor v' + __version__
        self.setWindowIcon(QtGui.QIcon(LmIcon.AppIconPixmap))
        self.setGeometry(100, 100, 1300, 102 + LmConfig.window_height(21))
        self.show()
        QtCore.QCoreApplication.processEvents()
        if self.signin():
            self._api = ApiRegistry(self._session)
            if not self._api._intf.build_list():
                LmTools.error('Failed to build interface list.')
            self.adjust_to_livebox_model()
            self.init_ui()
            self.setWindowTitle(self.app_window_title())
            LmConf.load_mac_addr_table()
            LmConf.load_spam_calls_table()
            QtCore.QCoreApplication.processEvents()
            self.loadDeviceList()
            self.initRepeaters()
            LmConfig.set_tooltips(self, 'main')
            self._app_ready = True
            if not NO_THREAD:
                self.startEventLoop()
                self.startWifiStatsLoop()

            # Force tag change tasks once app is ready
            self.tab_changed_event(self._tab_widget.currentIndex())

            # Propose to assign local names as LB name if no name base setup yet
            self.proposeToAssignNamesToUnkownDevices()


    ### Create main window
    def init_ui(self):
        # Status bar
        self._status_bar = QtWidgets.QStatusBar()
        self._status_bar_profile = QtWidgets.QLabel('[' + LmConf.CurrProfile['Name'] + ']')
        self._status_bar_profile.mousePressEvent = self.status_bar_profile_click
        self._status_bar.addPermanentWidget(self._status_bar_profile)
        self.setStatusBar(self._status_bar)
        QtCore.QCoreApplication.processEvents()

        # Tab Widgets
        self._tab_widget = QtWidgets.QTabWidget(self, objectName='tabWidget')
        self._tab_widget.setMovable(True)
        self._tab_widget.currentChanged.connect(self.tab_changed_event)
        self._tab_widget.tabBar().tabMoved.connect(self.tab_moved_event)

        tab_order = self.get_tabs_order()
        for t in tab_order:
            match t:
                case LmDeviceListTab.TAB_NAME:
                    self.createDeviceListTab()
                case LmInfoTab.TAB_NAME:
                    self.createLiveboxInfoTab()
                case LmGraphTab.TAB_NAME:
                    self.createGraphTab()
                case LmDeviceInfoTab.TAB_NAME:
                    self.create_device_info_tab()
                case LmEventsTab.TAB_NAME:
                    self.createEventsTab()
                case LmDhcpTab.TAB_NAME:
                    self.createDhcpTab()
                case LmNatPatTab.TAB_NAME:
                    self.createNatPatTab()
                case LmPhoneTab.TAB_NAME:
                    self.createPhoneTab()
                case LmActionsTab.TAB_NAME:
                    self.create_actions_tab()

        self.setCentralWidget(self._tab_widget)


    ### Reset the UI, e.g. after a change of profile
    def reset_ui(self):
        self._reset_flag = True
        self.close()


    ### Click on the profile indication in the status bar
    def status_bar_profile_click(self, event):
        self.change_profile_button_click()


    ### Handle change of tab event
    def tab_changed_event(self, new_tab_index):
        if self._app_ready:
            tab_name = self._tab_widget.widget(new_tab_index).objectName()
            match tab_name:
                case LmDeviceListTab.TAB_NAME:
                    if not NO_THREAD:
                        self.resumeWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                case LmInfoTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.resumeStatsLoop()
                        self.suspendRepeaterStatsLoop()
                case LmGraphTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                    self.graphTabClick()
                case LmDeviceInfoTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                case LmEventsTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                case LmDhcpTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                    self.dhcpTabClick()
                case LmNatPatTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                    self.natPatTabClick()
                case LmPhoneTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                    self.phoneTabClick()
                case LmActionsTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.suspendRepeaterStatsLoop()
                case LmRepeaterTab.TAB_NAME:
                    if not NO_THREAD:
                        self.suspendWifiStatsLoop()
                        self.suspendStatsLoop()
                        self.resumeRepeaterStatsLoop()


    ### Handle move of tab event
    def tab_moved_event(self, from_index, to_index):
        self.save_tabs_order()


    ### Get tabs order
    def get_tabs_order(self):
        # If nothing in config return the standard order
        if LmConf.Tabs is None:
            return TAB_ORDER
        else:
            # Rebuild the list by checking in case it would be corrupted / incomplete
            o = []
            for t in LmConf.Tabs:
                if t in TAB_ORDER:
                    o.append(t)
            for t in TAB_ORDER:
                if t not in LmConf.Tabs:
                    o.append(t)
            return o


    ### Save tabs order in configuration
    def save_tabs_order(self):
        LmConf.Tabs = []    # Reset
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            key = tab.property('Key')
            if key is not None:
                LmConf.Tabs.append(tab.objectName() + '_' + key)
            else:
                LmConf.Tabs.append(tab.objectName())
        LmConf.save()


    ### Get tab index from name & key, key can be None, returns -1 of not found
    def get_tab_index(self, name, key):
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            key = tab.property('Key')
            if (name == tab.objectName()) and (key == tab.property('Key')):
                return i
        return -1


    ### Window close event - called by PyQT
    def closeEvent(self, event):
        if not NO_THREAD:
            self._task.start(lx('Terminating threads...'))
            self.stopEventLoop()
            self.stopStatsLoop()
            self.stopWifiStatsLoop()
            self.stopRepeaterStatsLoop()
            self._task.end()
        event.accept()


    ### Last chance to release resources
    def app_terminate(self):
        self.signoutRepeaters()
        self.signout()
        self._app_ready = False


    ### Sign in to Livebox
    def signin(self):
        while True:
            self._task.start(lx('Signing in...'))
            self._session = LmSession(LmConf.LiveboxURL, 'LiveboxMonitor_' + LmConf.CurrProfile['Name'])
            try:
                r = self._session.signin(LmConf.LiveboxUser, LmConf.LiveboxPassword, not LmConf.SavePasswords)
            except BaseException as e:
                LmTools.error(str(e))
                r = -1
            self._task.end()
            if r > 0:
                return True
            self._session = None
            self.close()

            if r < 0:
                dialog = LiveboxCnxDialog(LmConf.LiveboxURL, self)
                if dialog.exec():
                    url = dialog.get_url()
                    # Remove unwanted characters (can be set via Paste action) + cleanup
                    url = LmTools.clean_url(re.sub('[\n\t]', '', url))
                    LmConf.set_livebox_url(url)
                    self.show()
                    continue
                else:
                    self.display_error(mx('Cannot connect to the Livebox.', 'cnx'))
                    return False

            dialog = LiveboxSigninDialog(LmConf.LiveboxUser, LmConf.LiveboxPassword, LmConf.SavePasswords, self)
            if dialog.exec():
                # Remove unwanted characters (can be set via Paste action)
                user = re.sub('[\n\t]', '', dialog.get_user())
                password = re.sub('[\n\t]', '', dialog.get_password())
                LmConf.SavePasswords = dialog.get_save_passwords()
                LmConf.set_livebox_user_password(user, password)
                self.show()
            else:
                self.display_error(mx('Livebox authentication failed.', 'auth'))
                return False


    ### Check if signed to Livebox
    def is_signed(self):
        return self._session is not None


    ### Sign out from Livebox
    def signout(self):
        if self.is_signed():
            self._session.close()
            self._session = None


    ### Adjust configuration to Livebox model
    def adjust_to_livebox_model(self):
        LmConf.set_livebox_mac(self._api._info.get_livebox_mac())

        LmTools.log_debug(1, f'Identified Livebox model: {self._api._info.get_livebox_model()} ({self._api._info.get_livebox_model_name()})')

        self.determine_fiber_link()
        self.determine_livebox_pro()
        set_livebox_model(self._api._info.get_livebox_model())


    ### Determine link type and if fiber or not
    def determine_fiber_link(self):
        # Determine link type
        try:
            d = self._api._info.get_wan_status()
        except BaseException as e:
            LmTools.error(str(e))
            self._linkType = 'UNKNOWN'
        else:
            self._linkType = d.get('LinkType', 'UNKNOWN').upper()

        # Determine fiber link
        model = self._api._info.get_livebox_model()
        if model >= 5:
            self._fiberLink = True
        elif model <= 3:
            self._fiberLink = False
        else:
            # Check link type for Livebox 4
            self._fiberLink = (self._linkType == 'SFP')

        LmTools.log_debug(1, f'Identified link type: {self._linkType}')
        LmTools.log_debug(1, f'Identified fiber link: {self._fiberLink}')


    ### Determine if Pro or Residential subscription
    def determine_livebox_pro(self):
        try:
            d = self._api._info.get_connection_status()
        except BaseException as e:
            LmTools.error(str(e))
            self._liveboxPro = False
        else:
            offer_type = d.get('OfferType')
            if offer_type is None:
                LmTools.error('Missing offer type in NMC:get, cannot determine Livebox Pro model')
                self._liveboxPro = False
            else:
                self._liveboxPro = 'PRO' in offer_type.upper()

        LmTools.log_debug(1, f'Identified Livebox Pro: {self._liveboxPro}')


    ### Exit with escape
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key.Key_Escape:
            self.close()


    ### Return window base title to use
    def app_window_title(self):
        if (self._status_bar is None) and (len(LmConf.Profiles) > 1):
            return self._application_name + ' [' + LmConf.CurrProfile['Name'] + ']'
        return self._application_name


    # Display an error popup
    def display_error(self, error_msg):
        self._task.suspend()
        LmTools.display_error(error_msg, self)
        self._task.resume()


    # Display a status popup
    def display_status(self, status_msg):
        self._task.suspend()
        LmTools.display_status(status_msg, self)
        self._task.resume()


    # Ask a question and return True if OK clicked
    def ask_question(self, question_msg):
        self._task.suspend()
        aAnswer = LmTools.ask_question(question_msg, self)
        self._task.resume()
        return aAnswer


    # Display an info text popup
    def display_infos(self, title, info_msg, info_doc=None):
        self._task.suspend()
        LmTools.display_infos(title, info_msg, info_doc, self)
        self._task.resume()


    ### Switch to device list tab
    def switch_to_device_list_tab(self):
        self._tab_widget.setCurrentWidget(self._deviceListTab)


    ### Switch to Livebox infos tab
    def switch_to_livebox_infos_tab(self):
        self._tab_widget.setCurrentWidget(self._liveboxInfoTab)


    ### Switch to graph tab
    def switch_to_graph_tab(self):
        self._tab_widget.setCurrentWidget(self._graphTab)


    ### Switch to device infos tab
    def switch_to_device_infos_tab(self):
        self._tab_widget.setCurrentWidget(self._device_info_tab)


    ### Switch to device events tab
    def switch_to_device_events_tab(self):
        self._tab_widget.setCurrentWidget(self._eventsTab)


    ### Switch to DHCP tab
    def switch_to_dhcp_tab(self):
        self._tab_widget.setCurrentWidget(self._dhcpTab)


    ### Switch to NAT/PAT tab
    def switch_to_nat_pat_tab(self):
        self._tab_widget.setCurrentWidget(self._natPatTab)


    ### Switch to phone tab
    def switch_to_phone_tab(self):
        self._tab_widget.setCurrentWidget(self._phoneTab)


    ### Switch to actions tab
    def switch_to_actions_tab(self):
        self._tab_widget.setCurrentWidget(self._actions_tab)


# ### wakepy error handler
def wake_py_failure(result):
    LmTools.error(f'Failed to keep system awake mode={result.mode_name} active={result.active_method} success={result.success} err={result.get_failure_text()}')


# ### Fatal error handler
def except_hook(type, value, trace_back):
    trace_back = ''.join(traceback.format_exception(type, value, trace_back))

    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle(lx('Fatal Error'))
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    msg_box.setText(trace_back + '\nApplication will now quit.')
    msg_box.exec()

    QtWidgets.QApplication.quit()


# ############# Main #############
def main(native_run=False):
    # Prevent logging to fail if running without console
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')

    LmConf.set_native_run(native_run)

    app = QtWidgets.QApplication(sys.argv)
    sys.excepthook = except_hook
    if LmConf.load():
        LmIcon.load()
        LmConf.load_custom_device_icons()
        release_check()

        # Command line parameters
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--redir', '-r', help='add a url redirection, REDIR format must be "url1=url2"', action='append')
        args = arg_parser.parse_args()
        if args.redir:
            LmSession.load_url_redirections(args.redir)

        while True:
            set_application_style()

            # Apply decoupled saved preferences
            LmConf.apply_saved_prefs()

            # Assign Python locale to selected preference (useful e.g. for pyqtgraph time axis localization)
            try:
                locale.setlocale(locale.LC_ALL, (LANGUAGES_LOCALE[LmConf.Language], 'UTF-8'))
            except BaseException as e:
                LmTools.error(f'setlocale() error: {e}')

            # Set Qt language to selected preference
            translator = QtCore.QTranslator()
            trans_path = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.TranslationsPath)
            translator.load("qtbase_" + LmConf.Language.lower(), trans_path)
            app.installTranslator(translator)

            # Start UI
            ui = LiveboxMonitorUI()
            app.aboutToQuit.connect(ui.app_terminate)
            if ui.is_signed():
                if LmConf.PreventSleep:
                    with keep.running(on_fail=wake_py_failure):
                        app.exec()
                else:
                    app.exec()
                if not ui._reset_flag:
                    break
            else:
                break


if __name__ == '__main__':
    main(True)
