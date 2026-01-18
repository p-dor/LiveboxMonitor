### Livebox Monitor TV Decoder tab module ###

import os
import json
import requests

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmThread import LmThread
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.api.LmSession import DEFAULT_TIMEOUT
from LiveboxMonitor.api import LmTvDecoderApi
from LiveboxMonitor.api.LmTvDecoderApi import TvDecoderApi
from LiveboxMonitor.lang.LmLanguages import get_tvdecoder_label as lx, get_tvdecoder_message as mx
from LiveboxMonitor.util import LmUtils

###TODO###
# Reset cache button (channels + icons)
# Preferred channels buttons + ability to set them
# Nice remote control button icons


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = "tvdecoderTab"    # 'Key' dynamic property indicates the MAC addr

# Static Config
DEFAULT_TVDECODER_NAME = "TV #"
TVDECODER_STATUS_FREQ = 3000      # status polling frequency in milliseconds
LIVEBOX_TV_CACHE_DIR = "tv"
LIVEBOX_TV_CHANNELS_CACHE_FILE = "channels.json"

# UI column block widths
COL1_WIDTH = 250
COL2_WIDTH = 230
RC_WIDTH = 242


RC_BUTTON_STYLE = """
    QPushButton {
        color: #ffffff;
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0   #707070,
            stop:0.4 #505050,
            stop:0.6 #202020,
            stop:1   #000000
        );
        border: 2px solid qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0   #808080,
            stop:1   #606060
        );
        border-radius: 16px;
        padding: 8px 8px;
        font-size:12px;
        font-weight:bold;
    }

    QPushButton:hover {
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0   #707070,
            stop:0.4 #606060,
            stop:0.6 #505050,
            stop:1   #303030
        );
        border: 2px solid qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0   #909090,
            stop:1   #707070
        );
    }

    QPushButton:pressed {
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0   #505050,
            stop:0.4 #404040,
            stop:0.6 #303030,
            stop:1   #202020
        );
        border: 2px solid qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0   #606060,
            stop:1   #404040
        );
    }

    QPushButton:disabled {
        color: #888888;
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #454545,
            stop:1 #353535
        );
        border: 2px solid #555555;
    }
    """



# ################################ LmTvDecoder class ################################
class LmTvDecoder:

    ### Create TvDecoder tab
    def create_tvdecoder_tab(self, tvdecoder):
        tvdecoder._tab = QtWidgets.QWidget(objectName=TAB_NAME)
        tvdecoder._tab.setProperty("Key", tvdecoder._key)

        # Status
        status_label = QtWidgets.QLabel(lx("Status:"), objectName="statusLabel")
        tvdecoder._status = QtWidgets.QLabel(objectName="statusValue")
        media_type_label = QtWidgets.QLabel(lx("Type:"), objectName="mediaTypeLabel")
        tvdecoder._media_type = QtWidgets.QLabel(objectName="mediaTypeValue")
        media_state_label = QtWidgets.QLabel(lx("State:"), objectName="mediaStateLabel")
        tvdecoder._media_state = QtWidgets.QLabel(objectName="mediaStateValue")

        status_grid = QtWidgets.QGridLayout()
        status_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        status_grid.setSpacing(10)
        status_grid.addWidget(status_label, 0, 0)
        status_grid.addWidget(tvdecoder._status, 0, 1)
        status_grid.addWidget(media_type_label, 1, 0)
        status_grid.addWidget(tvdecoder._media_type, 1, 1)
        status_grid.addWidget(media_state_label, 2, 0)
        status_grid.addWidget(tvdecoder._media_state, 2, 1)
        status_grid.setColumnStretch(1, 1)

        status_group_box = QtWidgets.QGroupBox(lx("Status"), objectName="statusGroup")
        status_group_box.setLayout(status_grid)
        status_group_box.setFixedWidth(COL1_WIDTH)

        # Device infos
        vendor_label = QtWidgets.QLabel(lx("Vendor:"), objectName="vendorLabel")
        tvdecoder._vendor_ui = QtWidgets.QLabel(tvdecoder._vendor, objectName="vendorValue")
        model_label = QtWidgets.QLabel(lx("Model:"), objectName="modelLabel")
        tvdecoder._model_ui = QtWidgets.QLabel(tvdecoder._model, objectName="modelValue")
        mac_label = QtWidgets.QLabel(lx("MAC:"), objectName="macLabel")
        tvdecoder._mac_ui = QtWidgets.QLabel(tvdecoder._mac_addr, objectName="macValue")
        ip_label = QtWidgets.QLabel(lx("IP:"), objectName="ipLabel")
        tvdecoder._ip_ui = QtWidgets.QLabel(tvdecoder._ip_addr, objectName="ipValue")

        infos_grid = QtWidgets.QGridLayout()
        infos_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        infos_grid.setSpacing(10)
        infos_grid.addWidget(vendor_label, 0, 0)
        infos_grid.addWidget(tvdecoder._vendor_ui, 0, 1)
        infos_grid.addWidget(model_label, 1, 0)
        infos_grid.addWidget(tvdecoder._model_ui, 1, 1)
        infos_grid.addWidget(mac_label, 2, 0)
        infos_grid.addWidget(tvdecoder._mac_ui, 2, 1)
        infos_grid.addWidget(ip_label, 3, 0)
        infos_grid.addWidget(tvdecoder._ip_ui, 3, 1)
        infos_grid.setColumnStretch(1, 1)

        infos_group_box = QtWidgets.QGroupBox(lx("Infos"), objectName="infoGroup")
        infos_group_box.setLayout(infos_grid)
        infos_group_box.setFixedWidth(COL1_WIDTH)

        # Description
        name_label = QtWidgets.QLabel(lx("Name:"), objectName="nameLabel")
        tvdecoder._name_ui = QtWidgets.QLabel(objectName="nameValue")
        manufacturer_label = QtWidgets.QLabel(lx("Maker:"), objectName="manufacturerLabel")
        tvdecoder._manufacturer = QtWidgets.QLabel(objectName="manufacturerValue")
        model_name_label = QtWidgets.QLabel(lx("Model:"), objectName="modelNameLabel")
        tvdecoder._model_name = QtWidgets.QLabel(objectName="modelNameValue")
        unique_id_label = QtWidgets.QLabel(lx("ID:"), objectName="uniqueIdLabel")
        tvdecoder._unique_id = QtWidgets.QLabel(objectName="uniqueIdValue")

        desc_grid = QtWidgets.QGridLayout()
        desc_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        desc_grid.setSpacing(10)
        desc_grid.addWidget(name_label, 0, 0)
        desc_grid.addWidget(tvdecoder._name_ui, 0, 1)
        desc_grid.addWidget(manufacturer_label, 1, 0)
        desc_grid.addWidget(tvdecoder._manufacturer, 1, 1)
        desc_grid.addWidget(model_name_label, 2, 0)
        desc_grid.addWidget(tvdecoder._model_name, 2, 1)
        desc_grid.addWidget(unique_id_label, 3, 0)
        desc_grid.addWidget(tvdecoder._unique_id, 3, 1)
        desc_grid.setColumnStretch(1, 1)

        desc_group_box = QtWidgets.QGroupBox(lx("Description"), objectName="descGroup")
        desc_group_box.setLayout(desc_grid)
        desc_group_box.setFixedWidth(COL1_WIDTH)

        # Column 1 box
        col1_box = QtWidgets.QVBoxLayout()
        col1_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        col1_box.setSpacing(40)
        col1_box.addWidget(status_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        col1_box.addWidget(infos_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        col1_box.addWidget(desc_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Channel infos
        channel_label = QtWidgets.QLabel(lx("Number:"), objectName="channelLabel")
        tvdecoder._channel = QtWidgets.QLabel(objectName="channelValue")
        channel_name_label = QtWidgets.QLabel(lx("Name:"), objectName="channelNameLabel")
        tvdecoder._channel_name = QtWidgets.QLabel(objectName="channelNameValue")
        media_id_label = QtWidgets.QLabel(lx("EPG:"), objectName="mediaIdLabel")
        tvdecoder._media_id = QtWidgets.QLabel(objectName="mediaIdValue")

        channel_grid = QtWidgets.QGridLayout()
        channel_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        channel_grid.setSpacing(10)
        channel_grid.addWidget(channel_label, 0, 0)
        channel_grid.addWidget(tvdecoder._channel, 0, 1)
        channel_grid.addWidget(channel_name_label, 1, 0)
        channel_grid.addWidget(tvdecoder._channel_name, 1, 1)
        channel_grid.addWidget(media_id_label, 2, 0)
        channel_grid.addWidget(tvdecoder._media_id, 2, 1)
        channel_grid.setColumnStretch(1, 1)

        tvdecoder._channel_icon = QtWidgets.QLabel(objectName="channelIcon")
        tvdecoder._channel_icon.setFixedWidth(150)
        tvdecoder._channel_icon.setFixedHeight(150)
        tvdecoder._channel_desc = LmTools.AutoHeightLabel(objectName="channelDesc")
        tvdecoder._channel_desc.setText("")

        channel_layout = QtWidgets.QVBoxLayout()
        channel_layout.addLayout(channel_grid, 0)
        channel_layout.addWidget(tvdecoder._channel_icon, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        channel_layout.addWidget(tvdecoder._channel_desc, 1, QtCore.Qt.AlignmentFlag.AlignCenter)

        channel_group_box = QtWidgets.QGroupBox(lx("Channel"), objectName="channelGroup")
        channel_group_box.setLayout(channel_layout)
        channel_group_box.setFixedWidth(COL2_WIDTH)

        # Channel set
        tvdecoder._channel_edit = QtWidgets.QLineEdit(objectName="channelEdit")
        tvdecoder._channel_set = QtWidgets.QPushButton(lx("Go"), objectName="channelSet")
        tvdecoder._channel_set.setDefault(True)
        tvdecoder._channel_set.clicked.connect(tvdecoder.channel_set_button_click)

        channel_set_layout = QtWidgets.QVBoxLayout()
        channel_set_layout.addWidget(tvdecoder._channel_edit, 1)
        channel_set_layout.addWidget(tvdecoder._channel_set, 1)

        channel_set_group_box = QtWidgets.QGroupBox(lx("Set Channel"), objectName="setChannelGroup")
        channel_set_group_box.setLayout(channel_set_layout)
        channel_set_group_box.setFixedWidth(COL2_WIDTH)

        # Column 2 box
        col2_box = QtWidgets.QVBoxLayout()
        col2_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        col2_box.setSpacing(40)
        col2_box.addWidget(channel_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        col2_box.addWidget(channel_set_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Remote control
        tvdecoder._power_button = LmTvDecoder.create_rcbutton("On/Off", "power", tvdecoder.power_button_click)
        tvdecoder._mic_button = LmTvDecoder.create_rcbutton("MIC", "mic", tvdecoder.mic_button_click)
        tvdecoder._up_button = LmTvDecoder.create_rcbutton("UP", "up", tvdecoder.up_button_click)
        tvdecoder._left_button = LmTvDecoder.create_rcbutton("<", "left", tvdecoder.left_button_click)
        tvdecoder._ok_button = LmTvDecoder.create_rcbutton("OK", "ok", tvdecoder.ok_button_click)
        tvdecoder._right_button = LmTvDecoder.create_rcbutton(">", "right", tvdecoder.right_button_click)
        tvdecoder._down_button = LmTvDecoder.create_rcbutton("DOWN", "down", tvdecoder.down_button_click)
        tvdecoder._back_button = LmTvDecoder.create_rcbutton("Back", "back", tvdecoder.back_button_click)
        tvdecoder._menu_button = LmTvDecoder.create_rcbutton("Menu", "menu", tvdecoder.menu_button_click)
        tvdecoder._vol_up_button = LmTvDecoder.create_rcbutton("Vol+", "vol_up", tvdecoder.vol_up_button_click)
        tvdecoder._chan_up_button = LmTvDecoder.create_rcbutton("Chan+", "chan_up", tvdecoder.chan_up_button_click)
        tvdecoder._vol_down_button = LmTvDecoder.create_rcbutton("Vol-", "vol_down", tvdecoder.vol_down_button_click)
        tvdecoder._chan_down_button = LmTvDecoder.create_rcbutton("Chan-", "chan_down", tvdecoder.chan_down_button_click)
        tvdecoder._mute_button = LmTvDecoder.create_rcbutton("Mute", "mute", tvdecoder.mute_button_click)
        tvdecoder._prog_button = LmTvDecoder.create_rcbutton("Prog", "prog", tvdecoder.prog_button_click)
        tvdecoder._one_button = LmTvDecoder.create_rcbutton("1", "one", tvdecoder.one_button_click)
        tvdecoder._two_button = LmTvDecoder.create_rcbutton("2", "two", tvdecoder.two_button_click)
        tvdecoder._three_button = LmTvDecoder.create_rcbutton("3", "three", tvdecoder.three_button_click)
        tvdecoder._four_button = LmTvDecoder.create_rcbutton("4", "four", tvdecoder.four_button_click)
        tvdecoder._five_button = LmTvDecoder.create_rcbutton("5", "five", tvdecoder.five_button_click)
        tvdecoder._six_button = LmTvDecoder.create_rcbutton("6", "six", tvdecoder.six_button_click)
        tvdecoder._seven_button = LmTvDecoder.create_rcbutton("7", "seven", tvdecoder.seven_button_click)
        tvdecoder._eight_button = LmTvDecoder.create_rcbutton("8", "eight", tvdecoder.eight_button_click)
        tvdecoder._nine_button = LmTvDecoder.create_rcbutton("9", "nine", tvdecoder.nine_button_click)
        tvdecoder._c_button = LmTvDecoder.create_rcbutton("C", "c", tvdecoder.c_button_click)
        tvdecoder._zero_button = LmTvDecoder.create_rcbutton("0", "zero", tvdecoder.zero_button_click)
        tvdecoder._vod_button = LmTvDecoder.create_rcbutton("VOD", "vod", tvdecoder.vod_button_click)
        tvdecoder._fbwd_button = LmTvDecoder.create_rcbutton("<<", "fbwd", tvdecoder.fbwd_button_click)
        tvdecoder._play_button = LmTvDecoder.create_rcbutton(">||", "play", tvdecoder.play_button_click)
        tvdecoder._ffwd_button = LmTvDecoder.create_rcbutton(">>", "ffwd", tvdecoder.ffwd_button_click)
        tvdecoder._admin_button = LmTvDecoder.create_rcbutton("Admin", "admin", tvdecoder.admin_button_click)
        tvdecoder._record_button = LmTvDecoder.create_rcbutton("REC", "record", tvdecoder.record_button_click)

        rc_grid = QtWidgets.QGridLayout()
        rc_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        rc_grid.setSpacing(5)
        rc_grid.addWidget(tvdecoder._power_button, 0, 0)
        rc_grid.addWidget(tvdecoder._mic_button, 0, 2)
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(3)
        rc_grid.addWidget(spacer, 1, 0, 1, 3)
        rc_grid.addWidget(tvdecoder._up_button, 2, 1)
        rc_grid.addWidget(tvdecoder._left_button, 3, 0)
        rc_grid.addWidget(tvdecoder._ok_button, 3, 1)
        rc_grid.addWidget(tvdecoder._right_button, 3, 2)
        rc_grid.addWidget(tvdecoder._down_button, 4, 1)
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(3)
        rc_grid.addWidget(spacer, 5, 0, 1, 3)
        rc_grid.addWidget(tvdecoder._back_button, 6, 0)
        rc_grid.addWidget(tvdecoder._menu_button, 6, 2)
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(10)
        rc_grid.addWidget(spacer, 7, 0, 1, 3)
        rc_grid.addWidget(tvdecoder._vol_up_button, 8, 0)
        rc_grid.addWidget(tvdecoder._chan_up_button, 8, 2)
        rc_grid.addWidget(tvdecoder._vol_down_button, 9, 0)
        rc_grid.addWidget(tvdecoder._chan_down_button, 9, 2)
        rc_grid.addWidget(tvdecoder._mute_button, 10, 0)
        rc_grid.addWidget(tvdecoder._prog_button, 10, 2)
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(10)
        rc_grid.addWidget(spacer, 11, 0, 1, 3)
        rc_grid.addWidget(tvdecoder._one_button, 12, 0)
        rc_grid.addWidget(tvdecoder._two_button, 12, 1)
        rc_grid.addWidget(tvdecoder._three_button, 12, 2)
        rc_grid.addWidget(tvdecoder._four_button, 13, 0)
        rc_grid.addWidget(tvdecoder._five_button, 13, 1)
        rc_grid.addWidget(tvdecoder._six_button, 13, 2)
        rc_grid.addWidget(tvdecoder._seven_button, 14, 0)
        rc_grid.addWidget(tvdecoder._eight_button, 14, 1)
        rc_grid.addWidget(tvdecoder._nine_button, 14, 2)
        rc_grid.addWidget(tvdecoder._c_button, 15, 0)
        rc_grid.addWidget(tvdecoder._zero_button, 15, 1)
        rc_grid.addWidget(tvdecoder._vod_button, 15, 2)
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(10)
        rc_grid.addWidget(spacer, 16, 0, 1, 3)
        rc_grid.addWidget(tvdecoder._fbwd_button, 17, 0)
        rc_grid.addWidget(tvdecoder._play_button, 17, 1)
        rc_grid.addWidget(tvdecoder._ffwd_button, 17, 2)
        rc_grid.addWidget(tvdecoder._admin_button, 18, 0)
        rc_grid.addWidget(tvdecoder._record_button, 18, 2)

        rc_group_box = QtWidgets.QGroupBox(lx("Remote Control"), objectName="rcGroup")
        rc_group_box.setLayout(rc_grid)
        rc_group_box.setFixedWidth(RC_WIDTH)

        # Remote control box
        rc_box = QtWidgets.QVBoxLayout()
        rc_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        rc_box.setSpacing(20)
        rc_box.addWidget(rc_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Layout
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        hbox.setSpacing(40)
        hbox.addLayout(col1_box, 0)
        hbox.addLayout(col2_box, 0)
        hbox.addLayout(rc_box, 0)
        tvdecoder._tab.setLayout(hbox)

        LmConfig.set_tooltips(tvdecoder._tab, "tvdecoder")
        self._tab_widget.insertTab(tvdecoder.tab_index_from_config(), tvdecoder._tab, tvdecoder._name)
        tvdecoder.set_item_state()


    ### Create a remote control button
    @staticmethod
    def create_rcbutton(title, name, connect):
        button = QtWidgets.QPushButton(title, objectName=name)
        button.setFixedWidth(70)
        button.setFixedHeight(37)
        button.setStyleSheet(RC_BUTTON_STYLE)
        button.clicked.connect(connect)
        return button


    ### Identify potential TV Decoder device & add it to the list
    def identify_tvdecoder(self, device):
        if "stb" in device.get("Tags", "").split(" "):
            key = device.get("Key", "")

            # Check if not already there
            for t in self._tvdecoders:
                if t._key == key:
                    return None

            index = len(self._tvdecoders)

            mac_addr = device.get("PhysAddress", "")
            try:
                name = LmConf.MacAddrTable[mac_addr]
            except KeyError:
                name = DEFAULT_TVDECODER_NAME + str(index + 1)

            # Determine vendor & model
            vendor = device.get("VendorClassID")
            model = device.get("UserClassID")

            ip_struct = LmUtils.determine_ip(device)
            ip_address = ip_struct.get("Address") if ip_struct else None

            active = device.get("Active", False)

            tvdecoder = LmTvHandler(self, index, key, mac_addr, name, vendor, model, ip_address, active)
            self._tvdecoders.append(tvdecoder)

            return tvdecoder

        return None


    ### Add and setup a potential new TV Decoder device
    def add_potential_tvdecoder(self, device):
        tvdecoder = self.identify_tvdecoder(device)
        if tvdecoder:
            self.create_tvdecoder_tab(tvdecoder)


    ### Find a tvdecoder in the list from device key
    def find_tvdecoder(self, device_key):
        return next((r for r in self._tvdecoders if r._key == device_key), None)


    ### Remove a potential TV Decoder device - not really remove, rather desactivate
    def remove_potential_tvdecoder(self, device_key):
        tvdecoder = self.find_tvdecoder(device_key)
        if tvdecoder:
            tvdecoder.process_active_event(False)


    ### Init TV Decoder tabs & sessions
    def init_tvdecoders(self):
        for r in self._tvdecoders:
            self.create_tvdecoder_tab(r)


    ### Click on TV decoder tab
    def tvdecoder_tab_click(self, device_key):
        tvdecoder = self.find_tvdecoder(device_key)
        if tvdecoder:
            tvdecoder.handle_tab_click()


    ### React to a device name update
    def tvdecoder_update_device_name(self, device_key):
        tvdecoder = self.find_tvdecoder(device_key)
        if tvdecoder:
            tvdecoder.process_update_device_name()


    ### React to device updated event
    def tvdecoder_device_updated_event(self, device_key, event):
        tvdecoder = self.find_tvdecoder(device_key)
        if tvdecoder:
            tvdecoder.process_device_updated_event(event)


    ### React to active status change event
    def tvdecoder_active_event(self, device_key, is_active):
        tvdecoder = self.find_tvdecoder(device_key)
        if tvdecoder:
            tvdecoder.process_active_event(is_active)


    ### React to IP Address change event
    def tvdecoder_ip_address_event(self, device_key, ipv4):
        tvdecoder = self.find_tvdecoder(device_key)
        if tvdecoder:
            tvdecoder.process_ip_address_event(ipv4)


    ### Init the TV Decoder status collector thread
    def init_tvdecoder_status_loop(self):
        self._tvdecoder_status_loop = None


    ### Start the TV Decoder status collector thread
    def start_tvdecoder_status_loop(self):
        self._tvdecoder_status_loop = TvDecoderStatusThread(self._tvdecoders)
        self._tvdecoder_status_loop.connect_processor(self.process_tvdecoder_status)


    ### Suspend the TV Decoder status collector thread
    def suspend_tvdecoder_status_loop(self):
        if self._tvdecoder_status_loop:
            self._tvdecoder_status_loop.stop()


    ### Resume the TV Decoder stats collector thread
    def resume_tvdecoder_status_loop(self):
        if self._tvdecoder_status_loop:
            self._tvdecoder_status_loop._resume.emit()
        else:
            self.start_tvdecoder_status_loop()


    ### Stop the TV Decoder status collector thread
    def stop_tvdecoder_status_loop(self):
        if self._tvdecoder_status_loop:
            self._tvdecoder_status_loop.quit()
            self._tvdecoder_status_loop = None


    ### Process a new TV Decoder status
    def process_tvdecoder_status(self, status):
        status["tvdecoder"].set_status(status)



# ################################ LmTvHandler class ################################
class LmTvHandler:

    ### Init handler
    def __init__(self, app, index, key, mac_addr, name, vendor, model, ip_address, active):
        self._app = app
        self._key = key
        self._mac_addr = mac_addr
        self._name = name
        self._vendor = vendor
        self._model = model
        self._ip_addr = ip_address
        self._active = active
        self._tab = None
        self._index = index
        self._api = TvDecoderApi(ip_address)
        self._current_epg_id = "-"

        # UI widgets
        self._status = None
        self._media_type = None
        self._media_state = None
        self._vendor_ui = None
        self._model_ui = None
        self._mac_ui = None
        self._ip_ui = None
        self._name_ui = None
        self._manufacturer = None
        self._model_name = None
        self._unique_id = None
        self._channel = None
        self._channel_name = None
        self._media_id = None
        self._channel_icon = None
        self._channel_desc = None
        self._channel_edit = None
        self._channel_set = None        
        self._power_button = None
        self._mic_button = None
        self._up_button = None
        self._left_button = None
        self._ok_button = None
        self._right_button = None
        self._down_button = None
        self._back_button = None
        self._menu_button = None
        self._vol_up_button = None
        self._chan_up_button = None
        self._vol_down_button = None
        self._chan_down_button = None
        self._mute_button = None
        self._prog_button = None
        self._one_button = None
        self._two_button = None
        self._three_button = None
        self._four_button = None
        self._five_button = None
        self._six_button = None
        self._seven_button = None
        self._eight_button = None
        self._nine_button = None
        self._c_button = None
        self._zero_button = None
        self._vod_button = None
        self._fbwd_button = None
        self._play_button = None
        self._ffwd_button = None
        self._admin_button = None
        self._record_button = None


    ### Handle tab click
    def handle_tab_click(self):
        self.load_channels()


    ### Check if active
    def is_active(self):
        return (self._ip_addr is not None) and self._active


    ### Get tab index from configuration at creation time
    def tab_index_from_config(self):
        # If no config, append
        n = self._app._tab_widget.count()
        if LmConf.Tabs is None:
            return n

        # If not in config, append
        entry_name = f"{TAB_NAME}_{self._key}"
        try:
            i = LmConf.Tabs.index(entry_name)
        except ValueError:
            return n

        # Try to find the tab immediately on the left
        for j in range(i - 1, -1, -1):
            t = LmConf.Tabs[j]
            if t.startswith(f"{TAB_NAME}_"):
                k = t[len(TAB_NAME) + 1:]
                t = TAB_NAME
            else:
                k = None

            left_tab_index = self._app.get_tab_index(t, k)
            if left_tab_index != -1:
                return left_tab_index + 1

        # No left tab found, must be the first
        return 0


    ### Get tab index
    def tab_index(self):
        if self._tab:
            return self._app._tab_widget.indexOf(self._tab)
        return -1


    ### Set item state according to current context
    def set_item_state(self):
        self.set_tab_icon()

        if self._tab:
            active = self.is_active()
            self._channel_set.setEnabled(active)
            self._power_button.setEnabled(active)
            self._mic_button.setEnabled(active)
            self._up_button.setEnabled(active)
            self._left_button.setEnabled(active)
            self._ok_button.setEnabled(active)
            self._right_button.setEnabled(active)
            self._down_button.setEnabled(active)
            self._back_button.setEnabled(active)
            self._menu_button.setEnabled(active)
            self._vol_up_button.setEnabled(active)
            self._chan_up_button.setEnabled(active)
            self._vol_down_button.setEnabled(active)
            self._chan_down_button.setEnabled(active)
            self._mute_button.setEnabled(active)
            self._prog_button.setEnabled(active)
            self._one_button.setEnabled(active)
            self._two_button.setEnabled(active)
            self._three_button.setEnabled(active)
            self._four_button.setEnabled(active)
            self._five_button.setEnabled(active)
            self._six_button.setEnabled(active)
            self._seven_button.setEnabled(active)
            self._eight_button.setEnabled(active)
            self._nine_button.setEnabled(active)
            self._c_button.setEnabled(active)
            self._zero_button.setEnabled(active)
            self._vod_button.setEnabled(active)
            self._fbwd_button.setEnabled(active)
            self._play_button.setEnabled(active)
            self._ffwd_button.setEnabled(active)
            self._admin_button.setEnabled(active)
            self._record_button.setEnabled(active)


    ### Set tab icon according to connection status
    def set_tab_icon(self):
        if self._tab:
            icon = LmIcon.TickPixmap if self.is_active() else LmIcon.CrossPixmap
            self._app._tab_widget.setTabIcon(self.tab_index(), QtGui.QIcon(icon))


    ### Load channels information with cache management
    def load_channels(self):
        # Check if already loaded
        if TvDecoderApi.get_channels():
            return

        # First check if data are in cache
        channels = None
        tv_cache_path = os.path.join(LmConf.get_cache_directory(), LIVEBOX_TV_CACHE_DIR)
        channels_file_path = os.path.join(tv_cache_path, LIVEBOX_TV_CHANNELS_CACHE_FILE)
        if os.path.isfile(channels_file_path):
            LmUtils.log_debug(1, "Loading TV channels cache in", channels_file_path)
            channels_file = None
            try:
                channels_file = open(channels_file_path)
                channels = json.load(channels_file)
            except Exception as e:
                LmUtils.error(str(e))
                # Wrong file format, ignore
                if channels_file:
                    channels_file.close()

        # Set channels infos if were cached
        if channels:
            TvDecoderApi.set_channels(channels)
            return

        # Load from Orange server
        TvDecoderApi.load_channels()

        # Set in cache
        channels = TvDecoderApi.get_channels()
        if channels:
            # Create tv cache directory if doesn't exist
            if not os.path.isdir(tv_cache_path):
                try:
                    os.makedirs(tv_cache_path)
                except Exception as e:
                    LmUtils.error(f"Cannot create tv cache folder {tv_cache_path}. Error: {e}")
                    return

            LmUtils.log_debug(1, "Saving tv channels cache in", channels_file_path)
            try:
                with open(channels_file_path, "w") as channels_file:
                    json.dump(channels, channels_file, indent=4)
            except Exception as e:
                LmUtils.error(f"Cannot save tv channels cache file. Error: {e}")


    ### Get current status
    def get_status(self):
        infos = {}
        if self.is_active():
            infos["name"] = None
            infos["manufacturer"] = None
            infos["model"] = None
            infos["id"] = None
            infos["status"] = None
            infos["mediatype"] = None
            infos["mediastate"] = None
            infos["mediaid"] = None

            # Get description
            try:
                desc = self._api.get_basic_description()
                infos["name"] = desc.get("friendlyName")
                infos["manufacturer"] = desc.get("manufacturer")
                infos["model"] = desc.get("modelName")
                model_id = desc.get("UDN")
                if model_id and model_id.startswith('uuid:'):
                    model_id = model_id[5:]
                infos["id"] = model_id
            except Exception as e:
                LmUtils.error(str(e))

            # Get status
            try:
                status = self._api.get_status()
                infos["status"] = status["osdContext"]
                infos["mediatype"] = status["playedMediaType"]
                infos["mediastate"] = status["playedMediaState"]
                infos["mediaid"] = status["playedMediaId"]
            except Exception as e:
                LmUtils.error(str(e))
        else:
            infos["name"] = "-"
            infos["manufacturer"] = "-"
            infos["model"] = "-"
            infos["id"] = "-"
            infos["status"] = "-"
            infos["mediatype"] = "-"
            infos["mediastate"] = "-"
            infos["mediaid"] = "-"

        return infos


    ### Update UI with given status
    def set_status(self, status):
        self.set_status_field(self._name_ui, status["name"])
        self.set_status_field(self._manufacturer, status["manufacturer"])
        self.set_status_field(self._model_name, status["model"])
        self.set_status_field(self._unique_id, status["id"])
        self.set_status_field(self._status, self._api.decode_status(status["status"]))
        self.set_status_field(self._media_type, self._api.decode_type(status["mediatype"]))
        self.set_status_field(self._media_state, self._api.decode_state(status["mediastate"]))
        epg = self._api.decode_epg(status["mediaid"])
        if epg != self._current_epg_id:
            self._current_epg_id = epg
            self.handle_channel_change()


    ### Update UI if TV channel changed
    def handle_channel_change(self):
        self.set_status_field(self._media_id, self._current_epg_id)
        channel = self._api.get_channel_infos(self._current_epg_id)
        self.set_status_field(self._channel, channel["number"])
        self.set_status_field(self._channel_name, channel["name"])
        self.set_channel_icon(channel["icon"])
        self._channel_desc.setText(channel["desc"])
        self._channel_desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


    ### Get a channel icon from cache file
    @staticmethod
    def get_channel_icon_cache(epg_id):
        icon_pixmap = None
        icon_dir_path = os.path.join(LmConf.get_cache_directory(), LIVEBOX_TV_CACHE_DIR)
        icon_file_path = os.path.join(icon_dir_path, f"{epg_id}.png")
        if os.path.isfile(icon_file_path):
            icon_pixmap = QtGui.QPixmap()
            if not icon_pixmap.load(icon_file_path):
                icon_pixmap = None
                LmUtils.error(f"Cannot load channel icon cache file {icon_file_path}. Cache file will be recreated.")
        return icon_pixmap


    ### Set a channel icon to cache file
    @staticmethod
    def set_channel_icon_cache(epg_id, content):
        icon_dir_path = os.path.join(LmConf.get_cache_directory(), LIVEBOX_TV_CACHE_DIR)
        icon_file_path = os.path.join(icon_dir_path, f"{epg_id}.png")

        # Create icon cache directory if doesn't exist
        if not os.path.isdir(icon_dir_path):
            try:
                os.makedirs(icon_dir_path)
            except Exception as e:
                LmUtils.error(f"Cannot create channel icon cache folder {icon_dir_path}. Error: {e}")
                return

        # Create and save icon cache file
        try:
            with open(icon_file_path, "wb") as icon_file:
                icon_file.write(content)
        except Exception as e:
            LmUtils.error(f"Cannot save channel icon cache file {icon_file_path}. Error: {e}")


    ### Update the channel icon
    def set_channel_icon(self, icon_url):
        icon_pixmap = None

        if icon_url:
            # First check if icon is in cache
            icon_pixmap = LmTvHandler.get_channel_icon_cache(self._current_epg_id)

            # Otherwise load icon from Orange server
            if icon_pixmap is None:
                icon_pixmap = QtGui.QPixmap()
                try:
                    icon_data = requests.get(icon_url,
                                             timeout=DEFAULT_TIMEOUT + LmConf.TimeoutMargin)
                                             # verify=icon_url.startswith("http://"))
                    if not icon_pixmap.loadFromData(icon_data.content):
                        LmUtils.error(f"Cannot load channel icon for EPG {self._current_epg_id}.")
                        icon_pixmap = None
                except requests.exceptions.Timeout as e:
                    LmUtils.error(f"Channel icon for EPG {self._current_epg_id} request timeout error: {e}.")
                    icon_pixmap = None
                except Exception as e:
                    LmUtils.error(f"{e}. Cannot request channel icon for EPG {self._current_epg_id}.")
                    icon_pixmap = None

                # If successfully loaded, try to store in local cache file for faster further loads
                if icon_pixmap:
                    LmTvHandler.set_channel_icon_cache(self._current_epg_id, icon_data.content)

        # Set the icon
        if icon_pixmap:
            self._channel_icon.setStyleSheet("QLabel {background-color:#404040}")
            self._channel_icon.setPixmap(icon_pixmap)
            self._channel_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        else:
            self._channel_icon.setPixmap(QtGui.QPixmap())
            self._channel_icon.setStyleSheet(None)


    ### Update UI status field with given value
    def set_status_field(self, field, value):
        if value is None:
            field.setText(lx("Error"))
            field.setStyleSheet("QLabel {color:red}")
        else:
            field.setText(value)
            field.setStyleSheet("QLabel {color:black}")


    ### Process an update of the device name
    def process_update_device_name(self):
        new_name = LmConf.MacAddrTable.get(self._key, None)
        if new_name is None:
            new_name = DEFAULT_TVDECODER_NAME + str(self._index + 1)
        self._name = new_name
        self._app._tab_widget.setTabText(self.tab_index(), self._name)


    ### Process a device updated event
    def process_device_updated_event(self, event):
        ipv4_struct = LmUtils.determine_ip(event)
        ipv4 = ipv4_struct.get("Address") if ipv4_struct else None
        if self._ip_addr != ipv4:
            self.process_ip_address_event(ipv4)

        self.process_active_event(event.get("Active", False))


    ### Process an active status change event
    def process_active_event(self, is_active):
        if self._active != is_active:
            self._active = is_active
            self.set_item_state()


    ### Process a IP Address change event
    def process_ip_address_event(self, ipv4):
        self._ip_addr = ipv4
        self._api.set_ip(ipv4)
        self._ip_ui.setText(ipv4)


    ### Click on the channel set button
    def channel_set_button_click(self):
        epg = None
        text = self._channel_edit.text()
        if text:
            if text.startswith("epg"):
                text = text[3:]
                try:
                    epg = int(text)
                except:
                    epg = None
            else:
                try:
                    number = int(text)
                    epg = self._api.get_epg_from_number(number)
                except:
                    epg = self._api.get_epg_from_name(text)
        if epg:
            try:
                self._api.change_channel(epg)
            except Exception as e:
                LmUtils.error(str(e))
                self._app.display_error(mx("Change channel failed. Error: {}", "changeChannelErr").format(str(e)))
        else:
            QtWidgets.QApplication.instance().beep()


    ### Press a remote control key
    def key_press(self, key, mode=LmTvDecoderApi.KeyMode.PRESS_ONCE):
        try:
            self._api.key_press(key, mode)
        except Exception as e:
            LmUtils.error(str(e))
            self._app.display_error(mx("Key press failed. Error: {}", "keyPressErr").format(str(e)))


    ### Click on POWER button
    def power_button_click(self):
        self.key_press(LmTvDecoderApi.Key.POWER)


    ### Click on MIC button
    def mic_button_click(self):
        self.key_press(LmTvDecoderApi.Key.MIC)


    ### Click on UP button
    def up_button_click(self):
        self.key_press(LmTvDecoderApi.Key.UP)


    ### Click on LEFT button
    def left_button_click(self):
        self.key_press(LmTvDecoderApi.Key.LEFT)


    ### Click on OK button
    def ok_button_click(self):
        self.key_press(LmTvDecoderApi.Key.OK)


    ### Click on RIGHT button
    def right_button_click(self):
        self.key_press(LmTvDecoderApi.Key.RIGHT)


    ### Click on DOWN button
    def down_button_click(self):
        self.key_press(LmTvDecoderApi.Key.DOWN)


    ### Click on BACK button
    def back_button_click(self):
        self.key_press(LmTvDecoderApi.Key.BACK)


    ### Click on MENU button
    def menu_button_click(self):
        self.key_press(LmTvDecoderApi.Key.MENU)


    ### Click on VOL_UP button
    def vol_up_button_click(self):
        self.key_press(LmTvDecoderApi.Key.VOL_UP)


    ### Click on CHAN_UP button
    def chan_up_button_click(self):
        self.key_press(LmTvDecoderApi.Key.CHAN_UP)


    ### Click on VOL_DOWN button
    def vol_down_button_click(self):
        self.key_press(LmTvDecoderApi.Key.VOL_DOWN)


    ### Click on CHAN_DOWN button
    def chan_down_button_click(self):
        self.key_press(LmTvDecoderApi.Key.CHAN_DOWN)


    ### Click on MUTE button
    def mute_button_click(self):
        self.key_press(LmTvDecoderApi.Key.MUTE)


    ### Click on PROG button
    def prog_button_click(self):
        self.key_press(LmTvDecoderApi.Key.PROG)


    ### Click on ONE button
    def one_button_click(self):
        self.key_press(LmTvDecoderApi.Key.ONE)


    ### Click on TWO button
    def two_button_click(self):
        self.key_press(LmTvDecoderApi.Key.TWO)


    ### Click on THREE button
    def three_button_click(self):
        self.key_press(LmTvDecoderApi.Key.THREE)


    ### Click on FOUR button
    def four_button_click(self):
        self.key_press(LmTvDecoderApi.Key.FOUR)


    ### Click on FIVE button
    def five_button_click(self):
        self.key_press(LmTvDecoderApi.Key.FIVE)


    ### Click on SIX button
    def six_button_click(self):
        self.key_press(LmTvDecoderApi.Key.SIX)


    ### Click on SEVEN button
    def seven_button_click(self):
        self.key_press(LmTvDecoderApi.Key.SEVEN)


    ### Click on EIGHT button
    def eight_button_click(self):
        self.key_press(LmTvDecoderApi.Key.EIGHT)


    ### Click on NINE button
    def nine_button_click(self):
        self.key_press(LmTvDecoderApi.Key.NINE)


    ### Click on C button
    def c_button_click(self):
        self.key_press(LmTvDecoderApi.Key.C)


    ### Click on ZERO button
    def zero_button_click(self):
        self.key_press(LmTvDecoderApi.Key.ZERO)


    ### Click on VOD button
    def vod_button_click(self):
        self.key_press(LmTvDecoderApi.Key.VOD)


    ### Click on FBWD button
    def fbwd_button_click(self):
        self.key_press(LmTvDecoderApi.Key.FBWD)


    ### Click on PLAY button
    def play_button_click(self):
        self.key_press(LmTvDecoderApi.Key.PLAY)


    ### Click on FFWD button
    def ffwd_button_click(self):
        self.key_press(LmTvDecoderApi.Key.FFWD)


    ### Click on ADMIN button
    def admin_button_click(self):
        self.key_press(LmTvDecoderApi.Key.BACK, LmTvDecoderApi.KeyMode.PRESS_HOLD)
        self.key_press(LmTvDecoderApi.Key.OK, LmTvDecoderApi.KeyMode.PRESS_ONCE)
        self.key_press(LmTvDecoderApi.Key.BACK, LmTvDecoderApi.KeyMode.RELEASE)


    ### Click on RECORD button
    def record_button_click(self):
        self.key_press(LmTvDecoderApi.Key.REC)



# ############# TV Decoder status collector thread #############
class TvDecoderStatusThread(LmThread):
    _status_received = QtCore.pyqtSignal(dict)
    _resume = QtCore.pyqtSignal()

    def __init__(self, tvdecoders):
        super().__init__(None, TVDECODER_STATUS_FREQ)
        self._tvdecoders = tvdecoders


    def connect_processor(self, processor):
        self._status_received.connect(processor)


    def task(self):
        for t in self._tvdecoders:
            status = t.get_status()
            status["tvdecoder"] = t
            self._status_received.emit(status)
