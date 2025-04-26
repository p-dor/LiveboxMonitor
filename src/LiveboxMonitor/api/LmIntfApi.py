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
    def __init__(self, api, session):
        super(IntfApi, self).__init__(api, session)
        self._list = None


    ### Get interface information
    def get_intf_info(self, intf):
        return self.call('NeMo.Intf.' + intf, 'get')


    ### Build interface list - return True if successful
    def build_intf_list(self):
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
            d = self.call('HomeLan.Interface', 'get')
        except:
            LmTools.Error(str(e))
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
        i = { 'Key': 'bridge', 'Name': 'LAN', 'Type': 'lan', 'SwapStats': True }
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
