### Livebox Monitor Device APIs ###

from LiveboxMonitor.api.LmApi import LmApi, LmApiException


# ################################ Device APIs ################################
class DeviceApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get device list
    def get_list(self):
        d = self.call_no_check('Devices', 'get', {'expression': 'physical and !self and !voice'}, timeout=10)
        if isinstance(d, list):
            return d
        raise LmApiException('Devices:get query error')


    ### Get USB setup and plugged device list
    def get_usb(self):
        d = self.call_no_check('Devices', 'get', {'expression': 'usb'}, timeout=10)
        if isinstance(d, list) and len(d):
            return d
        raise LmApiException('Devices:get query error')


    ### Get device topology
    def get_topology(self):
        d = self.call_no_check('TopologyDiagnostics', 'buildTopology', {'SendXmlFile': 'false'}, timeout=20)
        if isinstance(d, list) and len(d):
            return d
        raise LmApiException('TopologyDiagnostics:buildTopology query error')


    ### Set device name - key is MAC addr
    def set_name(self, device_key, device_name):
        self.call('Devices.Device.' + device_key, 'setName', {'name': device_name}, err_str='Livebox')


    ### Delete device name - key is MAC addr
    def del_name(self, device_key):
        self.call('Devices.Device.' + device_key, 'removeName', {'source': 'webui'}, err_str='Livebox')


    ### Set device DNS name - key is MAC addr
    def set_dns_name(self, device_key, dns_name):
        self.call('Devices.Device.' + device_key, 'setName', {'name': dns_name, 'source': 'dns'}, err_str='DNS')


    ### Delete device DNS name - key is MAC addr
    def del_dns_name(self, device_key):
        self.call('Devices.Device.' + device_key, 'removeName', {'source': 'dns'}, err_str='DNS')


    ### Set device type - key is MAC addr
    def set_type(self, device_key, device_type):
        self.call('Devices.Device.' + device_key, 'setType', {'type': device_type})


    ### Get device info - key is MAC addr
    def get_info(self, device_key):
         return self.call('Devices.Device.' + device_key, 'get')


    ### Get device IP address - key is MAC addr
    def get_ip_addr(self, device_key):
         return self.call('Devices.Device.' + device_key, 'getFirstParameter', {'parameter': 'IPAddress'})


    ### Get device schedule - key is MAC addr - return None if no schedule
    def get_schedule(self, device_key):
        d = self.call_raw('Scheduler', 'getSchedule', {'type': 'ToD', 'ID': device_key})
        if not d.get('status'):
            return None
        return d.get('data')


    ### Override device schedule - key is MAC addr
    def override_schedule(self, device_key, override_value):
        self.call('Scheduler', 'overrideSchedule', {'type': 'ToD', 'ID': device_key, 'override': override_value})


    ### Add device schedule - key is MAC addr
    def add_schedule(self, device_key, schedule):
        schedule['ID'] = device_key
        self.call('Scheduler', 'addSchedule', {'type': 'ToD', 'info': schedule})


    ### Block device - key is MAC addr
    def block(self, device_key):
        has_schedule = self.get_schedule(device_key) is not None
        # If has schedule override it, otherwise add it
        if has_schedule:
            self.override_schedule(device_key, 'Disable')
        else:
            schedule = {}
            schedule['base'] = 'Weekly'
            schedule['def'] = 'Enable'
            schedule['schedule'] = []
            schedule['enable'] = True
            schedule['override'] = 'Disable'
            self.add_schedule(device_key, schedule)


    ### Unblock device - key is MAC addr - return False if device was not blocked
    def unblock(self, device_key):
        has_schedule = self.get_schedule(device_key) is not None
        # If has schedule override it, otherwise no need to unlock
        if has_schedule:
            self.override_schedule(device_key, 'Enable')
            return True
        return False


    ### Check if device is blocked - key is MAC addr
    def is_blocked(self, device_key):
        d = self.get_schedule(device_key)
        if not d:
            return False

        d = d.get('scheduleInfo')
        if not d:
            return False

        return (d.get('override') == 'Disable') and (d.get('value') == 'Disable')


    ### Delete device from Livebox - key is MAC addr
    def delete(self, device_key):
        self.call('Devices', 'destroyDevice', {'key': device_key})


    ### Send WOL signal to device - key is MAC addr
    def wake_on_lan(self, device_key):
        self.call_no_check('WOL', 'sendWakeOnLan', {'hostID': device_key, 'broadcast': True})
