### Livebox Monitor Firewall APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ Firewall APIs ################################
class FirewallApi(LmApi):
    def __init__(self, api, session):
        super(FirewallApi, self).__init__(api, session)


    ### Get IPv4 firewall level
    def get_ipv4_firewall_level(self):
        return self.call('Firewall', 'getFirewallLevel')


    ### Get IPv6 firewall level
    def get_ipv6_firewall_level(self):
        return self.call('Firewall', 'getFirewallIPv6Level')


    ### Set IPv4 firewall level
    def set_ipv4_firewall_level(self, level):
        self.call('Firewall', 'setFirewallLevel', {'level': level})


    ### Set IPv6 firewall level
    def set_ipv6_firewall_level(self, level):
        self.call('Firewall', 'setFirewallIPv6Level', {'level': level})


    ### Get IPv4 & IPv6 respond to ping setup
    def get_respond_to_ping(self):
        # ###Info### - works also for other sourceInterfaces such as veip0, eth0, voip, etc, but usefulness?
        return self.call('Firewall', 'getRespondToPing', {'sourceInterface': 'data'})


    ### Set IPv6 firewall level - enable must be a dict with 'enableIPv4' & 'enableIPv6' boolean values
    def set_respond_to_ping(self, enable):
        self.call('Firewall', 'setRespondToPing', {'sourceInterface': 'data', 'service_enable': enable})


    ### Get list of devices in DMZ, returns a dictionary
    def get_dmz_devices(self):
        return self.call_no_check('Firewall', 'getDMZ')


    ### Add a DMZ entry
    def add_dmz(self, dmz_id, dest_ip, ext_ips=None, enable=True):
        p = {'id': dmz_id,
             'sourceInterface': 'data',
             'destinationIPAddress': dest_ip,
             'enable': enable}
        if ext_ips:
            p['sourcePrefix'] = ext_ips
        self.call('Firewall', 'setDMZ', p)


    ### Delete a DMZ entry
    def delete_dmz(self, dmz_id):
        self.call('Firewall', 'deleteDMZ', { 'id': dmz_id })
