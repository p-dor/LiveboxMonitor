### Livebox Monitor TV Decoder tab module ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmThread import LmThread
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.lang.LmLanguages import get_tvdecoder_label as lx, get_tvdecoder_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = "tvdecoderTab"    # 'Key' dynamic property indicates the MAC addr

# Static Config
DEFAULT_TVDECODER_NAME = "TV #"
TVDECODER_STATUS_FREQ = 3000      # status polling frequency in milliseconds


# ################################ LmTvDecoder class ################################
class LmTvDecoder:

    ### Create TvDecoder tab
    def create_tvdecoder_tab(self, tvdecoder):
        tvdecoder._tab = QtWidgets.QWidget(objectName=TAB_NAME)
        tvdecoder._tab.setProperty("Key", tvdecoder._key)

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        tvdecoder._tab.setLayout(vbox)

        LmConfig.set_tooltips(tvdecoder._tab, "tvdecoder")
        self._tab_widget.insertTab(tvdecoder.tab_index_from_config(), tvdecoder._tab, tvdecoder._name)
        tvdecoder.set_tab_icon()


    ### Identify potential TV Decoder device & add it to the list
    def identify_tvdecoder(self, device):
        return None     ###TODO### - to remove

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

            ip_struct = LmTools.determine_ip(device)
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
            tvdecoder.set_tab_icon()


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


    ### React to device a name update
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
        print(status)    ###TODO###



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


    ### Set tab icon according to connection status
    def set_tab_icon(self):
        if self._tab:
            icon = LmIcon.TickPixmap if self.is_active() else LmIcon.CrossPixmap
            self._app._tab_widget.setTabIcon(self.tab_index(), QtGui.QIcon(icon))


    ### Process an update of the device name
    def process_update_device_name(self):
        new_name = LmConf.MacAddrTable.get(self._key, None)
        if new_name is None:
            new_name = DEFAULT_TVDECODER_NAME + str(self._index + 1)
        self._name = new_name
        self._app._tab_widget.setTabText(self.tab_index(), self._name)


    ### Process a device updated event
    def process_device_updated_event(self, event):
        ipv4_struct = LmTools.determine_ip(event)
        ipv4 = ipv4_struct.get("Address") if ipv4_struct else None
        if self._ip_addr != ipv4:
            self.process_ip_address_event(ipv4)

        self.process_active_event(event.get("Active", False))


    ### Process an active status change event
    def process_active_event(self, is_active):
        if self._active != is_active:
            self._active = is_active
            self.set_tab_icon()


    ### Process a IP Address change event
    def process_ip_address_event(self, ipv4):
        self._ip_addr = ipv4
        self.set_tab_icon()


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
            if r.is_active():
                e = {"TvDecoder": t,
                     "Status": "Status TEST"}    ###TODO###
                self._status_received.emit(e)
