### Livebox Monitor DHCP APIs ###

from LiveboxMonitor.api.LmApi import LmApi


# ################################ Livebox DHCP APIs ################################
class DhcpApi(LmApi):
    def __init__(self, api_registry):
        super(DhcpApi, self).__init__(api_registry)


    ### Get IPv6 prefix leases
    def get_ipv6_prefix_leases(self):
        d = self.call_no_check('DHCPv6.Server', 'getPDPrefixLeases')
        if isinstance(d, list):
            return d
        raise Exception('DHCPv6.Server:getPDPrefixLeases query error')
