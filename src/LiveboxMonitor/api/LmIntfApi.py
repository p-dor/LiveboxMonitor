### Livebox Monitor Interface APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################
# Friendly name map
FRIENDLY_NAME_MAP = {
    'WAN_Ethernet':         'WAN',
    'WAN_GPON':             'Fiber',
    'eth1':                 'Ethernet 1',
    'eth2':                 'Ethernet 2',
    'eth3':                 'Ethernet 3',
    'eth4':                 'Ethernet 4',
    '2.4GHz-Private_SSID':  'Wifi 2.4GHz',
    '5GHz-Private_SSID':    'Wifi 5GHz',
    '6GHz-Private_SSID':    'Wifi 6GHz',
    '2.4GHz-Guest_SSID':    'Guest 2.4GHz',
    '5GHz-Guest_SSID':      'Guest 5GHz',
    'LAN-2.5G':             'Ether 2.5G',
    'LAN-10G':              'Ether 10G'
}


# ################################ Interface APIs ################################
class IntfApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)
        self._list = None
        self._has_radio_band_2 = False
        self._has_radio_band_5 = False
        self._has_radio_band_6 = False


    ### Get interface information
    def get_info(self, intf):
        return self.call('NeMo.Intf.' + intf, 'get')


    ### Get Ethernet Interfaces setup - returns base, eth
    def get_eth_mibs(self):
        d = self.call('NeMo.Intf.lan', 'getMIBs', {'mibs': 'base eth'}, timeout=25)
        base = d.get('base')
        eth = d.get('eth')
        if (base is None) or (eth is None):
            raise LmApiException('NeMo.Intf.lan:getMIBs service failed.')
        return base, eth


    ### Get Wifi or Guest Interfaces setup - returns base, radio and vap
    def get_wifi_mibs(self, guest=False):
        i = 'guest' if guest else 'lan'
        d = self.call('NeMo.Intf.' + i, 'getMIBs', {'mibs': 'base wlanradio wlanvap'}, timeout=25)
        base = d.get('base')
        radio = d.get('wlanradio')
        vap = d.get('wlanvap')
        if (base is None) or (radio is None) or (vap is None):
            raise LmApiException('NeMo.Intf.' + i + ':getMIBs service failed.')
        return base, radio, vap


    ### Get ONT Interface setup - if ONT intf not given will take the first one found
    def get_ont_mibs(self, ont_intf=None):
        if not ont_intf:
            try:
                ont_intf = next(i['Key'] for i in self.get_list() if i['Type'] == 'ont')
            except StopIteration:
                raise LmApiException('No ONT interface found.')

        d = self.call('NeMo.Intf.' + ont_intf, 'getMIBs', {'mibs': 'gpon'})
        d = d.get('gpon')
        if d:
            d = d.get(ont_intf)
        if not d:
            raise LmApiException('NeMo.Intf.' + ont_intf + ':getMIBs service failed.')
        return d


    ### Get SFP ONT module infos (only for Livebox 4)
    def get_sfp_info(self):
        return self.call('SFP', 'get')


    ### Get list of interface keys
    def get_key_list(self):
        return self.call('NeMo.Intf.lo', 'getIntfs', {'traverse': 'all'})


    ### Get interface list from HomeLan package
    def get_raw_list(self):
        return self.call('HomeLan.Interface', 'get')


    ### Get list of useful interfaces with key, name, type and swap stats fields
    def get_list(self):
        if self._list is None:
            if not self._api._intf.build_list():
                LmTools.error('Failed to build interface list.')
        return self._list


    ### Build interface list - return True if successful
    def build_list(self):
        self._list = []

        '''
        Each entry must have those fields:
        - Key -> intf key
        - Name -> intf friendly name - used to display info in UI
        - Type -> wan/ont/lan/eth/wif (Wifi)/wig (Wifi Guest)
        - SwapStats -> True is stats must be swapped when displayed (R <-> T)
        '''

        # Call Homeland package to get interface list
        try:
            d = self.get_raw_list()
        except Exception as e:
            LmTools.error(str(e))
            return False

        # Collect all interfaces per type
        wan = []
        ont = []
        eth = []
        wif = []
        wig = []
        for k in d:
            e = d.get(k)
            type = e.get('Alias')
            name = e.get('FriendlyName')
            if type == 'Eth':
                i = {}
                i['Key'] = k
                i['Name'] = FRIENDLY_NAME_MAP.get(name, name)
                i['Type'] = 'eth'
                i['SwapStats'] = True
                eth.append(i)
            elif type == 'WiFi':
                i = {}
                i['Key'] = k
                i['Name'] = FRIENDLY_NAME_MAP.get(name, name)
                if 'Guest' in name:
                    i['Type'] = 'wig'
                    wig.append(i)
                else:
                    i['Type'] = 'wif'
                    wif.append(i)
                if '2.4GHz' in name:
                    self._has_radio_band_2 = True
                elif '5GHz' in name:
                    self._has_radio_band_5 = True
                elif '6GHz' in name:
                    self._has_radio_band_6 = True
                i['SwapStats'] = True
            elif name == 'WAN_Ethernet':
                i = {}
                i['Key'] = k
                i['Name'] = FRIENDLY_NAME_MAP.get(name, name)
                i['Type'] = 'wan'
                i['SwapStats'] = False
                wan.append(i)
            elif name == 'WAN_GPON':
                i = {}
                i['Key'] = k
                i['Name'] = FRIENDLY_NAME_MAP.get(name, name)
                i['Type'] = 'ont'
                i['SwapStats'] = False
                ont.append(i)

        # Build correctly sorted list
        if wan:
            # Add only if there is no ONT interface
            if not ont:
                for i in wan:
                    self._list.append(i)
        if ont:
            for i in ont:
                self._list.append(i)

        # All Livebox have bridge intf as LAN interface
        i = {'Key': 'bridge', 'Name': 'LAN', 'Type': 'lan', 'SwapStats': True}
        self._list.append(i)

        if eth:
            for i in eth:
                self._list.append(i)
        if wif:
            for i in wif:
                self._list.append(i)
        if wig:
            for i in wig:
                self._list.append(i)

        return True


    ### Is 2.4GHz radio band available
    def has_radio_band_2(self):
        return self._has_radio_band_2


    ### Is 5GHz radio band available
    def has_radio_band_5(self):
        return self._has_radio_band_5


    ### Is 6GHz radio band available
    def has_radio_band_6(self):
        return self._has_radio_band_6
