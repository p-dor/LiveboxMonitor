### Livebox Monitor IPTV APIs ###

from LiveboxMonitor.api.LmApi import LmApi


# ################################ Livebox IPTV APIs ################################
class IptvApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get IPTV status
    def get_status(self):
        d = self.call_raw('NMC.OrangeTV', 'getIPTVStatus')
        d = d.get('data')
        if d:
            d = d.get('IPTVStatus')
        if d is not None:
            return d
        raise LmApiException('NMC.OrangeTV:getIPTVStatus service failed.')


    ### Get IPTV Multi Screens status
    def get_multi_screens_status(self):
        d = self.call_raw('NMC.OrangeTV', 'getIPTVMultiScreens')
        d = d.get('data')
        if d:
            d = d.get('Enable')
        if d is not None:
            return d
        raise LmApiException('NMC.OrangeTV:getIPTVMultiScreens service failed.')


    ### Get IPTV config
    def get_config(self):
        return self.call('NMC.OrangeTV', 'getIPTVConfig')
