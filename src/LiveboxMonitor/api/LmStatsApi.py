### Livebox Monitor screen & LEDs APIs ###

from LiveboxMonitor.api.LmApi import LmApi


# ################################ Statistics APIs ################################
class StatsApi(LmApi):
    def __init__(self, api_registry):
        super(StatsApi, self).__init__(api_registry)


    ### Get wifi interface statistics
    def get_wifi_intf(self, wifi_intf_key):
        return self.call('NeMo.Intf.' + wifi_intf_key, 'getStationStats')


    ### Get interface statistics
    # WARNING counters are recycling at 4Gb only
    def get_intf(self, intf_key):
        return self.call('NeMo.Intf.' + intf_key, 'getNetDevStats')


    ### Get interface statistics frequency in seconds
    def get_intf_frequency(self):
        return int(self.call_no_check('HomeLan', 'getReadingInterval'))


    ### Get device statistics frequency in seconds
    def get_device_frequency(self):
        return int(self.call_no_check('HomeLan', 'getDevicesReadingInterval'))


    ### Get interface list with nb of stats samples
    def get_intf_list(self):
        return self.call('HomeLan.Interface', 'get')


    ### Get device list with nb of stats samples
    def get_device_list(self):
        return self.call('HomeLan.Device', 'get')


    ### Get interface results
    def get_intf_results(self, intf_id, start=0, end=0):
        if start:
            d = self.call('HomeLan', 'getResults',
                          {'InterfaceName': intf_id, 'BeginTrafficTimestamp': start, 'EndTrafficTimestamp': end},
                          timeout=15)
        else:
            d = self.call('HomeLan', 'getResults', {'InterfaceName': intf_id}, timeout=15)
        d = d.get(intf_id, {})
        return d.get('Traffic', [])


    ### Get device results
    def get_device_results(self, device_id, start=0, end=0):
        if start:
            d = self.call('HomeLan', 'getDeviceResults',
                          {'DeviceName': device_id, 'BeginTrafficTimestamp': start, 'EndTrafficTimestamp': end},
                          timeout=15)
        else:
            d = self.call('HomeLan', 'getDeviceResults', {'DeviceName': device_id}, timeout=15)
        d = d.get(device_id, {})
        return d.get('Traffic', [])
