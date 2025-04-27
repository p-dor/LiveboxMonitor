### Livebox Monitor Livebox Info APIs ###

import requests

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################
LIVEBOX_SCAN_TIMEOUT = 0.6

# Livebox versions map
LIVEBOX_MODEL_MAP = {
    'Livebox 4': 4,
    'Livebox Fibre': 5,
    'Livebox 6': 6,
    'Livebox 7': 7
    }


# ################################ Livebox Info APIs ################################
class LiveboxInfoApi(LmApi):
    def __init__(self, api, session):
        super(LiveboxInfoApi, self).__init__(api, session)
        self._livebox_mac = None
        self._livebox_model = None
        self._software_version = None


    ### Get Livebox basic info
    def get_livebox_info(self):
        return self.call('DeviceInfo', 'get')


    ### Set Livebox basic info cache
    def set_livebox_info_cache(self):
        try:
            d = self.get_livebox_info()
        except BaseException as e:
            LmTools.Error(str(e))
            LmTools.Error('Cannot determine Livebox model.')
            self._livebox_mac = ''
            self._livebox_model = 0
            self._software_version = ''
        else:
            self._livebox_mac = d.get('BaseMAC', '').upper()
            aModel = d.get('ProductClass', '')
            if aModel:
                self._livebox_model = LIVEBOX_MODEL_MAP.get(aModel)
            if self._livebox_model is None:
                LmTools.Error(f'Unknown Livebox model: {aModel}.')
                self._livebox_model = 0
            self._software_version = d.get('SoftwareVersion', '')


    ### Get Livebox MAC
    def get_livebox_mac(self):
        if not self._livebox_mac:
            self.set_livebox_info_cache()
        return self._livebox_mac


    ### Get Livebox model
    def get_livebox_model(self):
        if not self._livebox_model:
            self.set_livebox_info_cache()
        return self._livebox_model


    ### Get Livebox software version
    def get_software_version(self):
        if not self._software_version:
            self.set_livebox_info_cache()
        return self._software_version


    ### It is possible to query DeviceInfo service without being logged, e.g. to get MAC address
    @staticmethod
    def get_livebox_mac_nosign(livebox_url):
        if livebox_url is not None:
            try:
                r = requests.Session().post(livebox_url  + 'ws',
                           data='{"service":"sysbus.DeviceInfo", "method":"get", "parameters":{}}',
                           headers={'Accept':'*/*', 'Content-Type':'application/x-sah-ws-4-call+json'},
                           timeout=LIVEBOX_SCAN_TIMEOUT + LmSession.TimeoutMargin)
            except:
                r = None
            if r is not None:
                s = r.json().get('status')
                if s is not None:
                    s = s.get('BaseMAC')
                    if s is not None:
                        return s.upper()

        return None
