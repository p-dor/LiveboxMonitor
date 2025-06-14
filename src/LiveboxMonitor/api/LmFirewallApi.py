### Livebox Monitor Firewall APIs ###

from LiveboxMonitor.api.LmApi import LmApi


# ################################ Firewall APIs ################################
class FirewallApi(LmApi):
    def __init__(self, api_registry):
        super(FirewallApi, self).__init__(api_registry)


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
        d = self.call_no_check('Firewall', 'getDMZ')
        if isinstance(d, dict):
            return d
        raise LmApiException('Firewall:getDMZ query error')


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
        self.call('Firewall', 'deleteDMZ', {'id': dmz_id})


    ### Get list of IPv4 port forwarding rules, returns a dictionary
    # if no rule_id it returns all
    # origin can be 'webui' or 'upnp', default is all
    def get_ipv4_port_forwarding(self, rule_id=None, origin=None):
        p = {}
        if rule_id:
            p['id'] = rule_id
        if origin:
            p['origin'] = origin
        d = self.call_no_check('Firewall', 'getPortForwarding', p)
        if isinstance(d, dict):
            return d
        raise LmApiException('Firewall:getPortForwarding query error')


    ### Set a IPv4 port forwarding rules, returns the rule as the Livebox set it
    # rule must follow Livebox model
    def set_ipv4_port_forwarding(self, rule):
        d = self.call_raw('Firewall', 'setPortForwarding', rule)
        if d.get('status'):
            d = d.get('data')
            if d:
                d = d.get('rule')
            if d:
                return d
        raise LmApiException('Firewall:setPortForwarding query error')


    ### Delete a IPv4 port forwarding rules
    # origin can be 'webui' or 'upnp'
    def del_ipv4_port_forwarding(self, rule_id, dest_ip, origin):
        p = {'id': f'{origin}_{rule_id}',
             'destinationIPAddress': dest_ip,
             'origin': origin}
        self.call('Firewall', 'deletePortForwarding', p)


    ### Delete all IPv4 port forwarding rules
    # origin can be 'webui' or 'upnp'
    def del_all_ipv4_port_forwarding(self, origin):
        self.call('Firewall', 'deletePortForwarding', {'origin': origin})


    ### Get list of IPv4 protocol forwarding rules, returns a dictionary
    def get_ipv4_protocol_forwarding(self):
        d = self.call_no_check('Firewall', 'getProtocolForwarding')
        if isinstance(d, dict):
            return d
        raise LmApiException('Firewall:getProtocolForwarding query error')


    ### Set a IPv4 protocol forwarding rules, returns the rule as the Livebox set it
    # rule must follow Livebox model
    def set_ipv4_protocol_forwarding(self, rule):
        d = self.call_raw('Firewall', 'setProtocolForwarding', rule)
        if d.get('status'):
            d = d.get('data')
            if d:
                d = d.get('rule')
            if d:
                return d
        raise LmApiException('Firewall:setProtocolForwarding query error')


    ### Delete a IPv4 protocol forwarding rules
    def del_ipv4_protocol_forwarding(self, rule_id):
        self.call('Firewall', 'deleteProtocolForwarding', {'id': rule_id})


    ### Get list of IPv6 pinhole rules, returns a dictionary
    # if no rule_id it returns all
    # Origin can be 'webui' or 'upnp', default is all
    def get_ipv6_pinhole(self, rule_id=None, origin=None):
        p = {}
        if rule_id:
            p['id'] = rule_id
        if origin:
            p['origin'] = origin
        d = self.call_no_check('Firewall', 'getPinhole', p)
        if isinstance(d, dict):
            return d
        raise LmApiException('Firewall:getPinhole query error')


    ### Set a IPv6 pinhole rules, returns the rule as the Livebox set it
    # rule must follow Livebox model
    def set_ipv6_pinhole(self, rule):
        d = self.call_raw('Firewall', 'setPinhole', rule)
        if d.get('status'):
            d = d.get('data')
            if d:
                d = d.get('rule')
            if d:
                return d
        raise LmApiException('Firewall:setPinhole query error')


    ### Delete a IPv6 pinhole rules
    # origin can be 'webui' or 'upnp'
    def del_ipv6_pinhole(self, rule_id, origin):
        p = {'id': f'{origin}_{rule_id}',
             'origin': origin}
        self.call('Firewall', 'deletePinhole', p)


    ### Commit a change
    def commit(self):
        self.call('Firewall', 'commit')
