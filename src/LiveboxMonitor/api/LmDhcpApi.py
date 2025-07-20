### Livebox Monitor DHCP APIs ###

from LiveboxMonitor.api.LmApi import LmApi, LmApiException


# ################################ Livebox DHCP APIs ################################
class DhcpApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get DHCP setup
    def get_setup(self):
        d = self.call_raw("NMC", "getLANIP")
        return d.get("data")


    ### Set DHCP setup
    def set_setup(self, setup):
        self.call_raw("NetMaster.LAN.default.Bridge.lan", "setIPv4", setup)


    ### Get DHCP leases list - default to standard domain
    def get_leases(self, guest=False):
        domain = "guest" if guest else "default"
        d = self.call_no_check("DHCPv4.Server.Pool." + domain, "getStaticLeases", domain)
        if isinstance(d, list):
            return d
        raise LmApiException(f"DHCPv4.Server.Pool.{domain}:getStaticLeases query error")


    ### Add a DHCP lease - default to standard domain
    def add_lease(self, mac_addr, ip_addr, guest=False):
        domain = "guest" if guest else "default"
        self.call_no_check("DHCPv4.Server.Pool." + domain, "addStaticLease", {"MACAddress": mac_addr, "IPAddress": ip_addr})


    ### Delete a DHCP lease - default from standard domain
    def delete_lease(self, mac_addr, guest=False):
        domain = "guest" if guest else "default"
        self.call_no_check("DHCPv4.Server.Pool." + domain, "deleteStaticLease", {"MACAddress": mac_addr})


    ### Get DHCP infos - domain can be default or guest or bridge_ctr, get all if None
    def get_info(self, domain=None):
        if domain:
            return self.call("DHCPv4.Server", "getDHCPServerPool", {"id": domain})
        return self.call("DHCPv4.Server", "getDHCPServerPool")


    ### Get DHCPv6 server status
    def get_v6_server_status(self):
        return self.call_no_check("DHCPv6.Server", "getDHCPv6ServerStatus")


    ### Get DHCPv6 prefix
    def get_v6_prefix(self):
        d = self.call_no_check("DHCPv6.Server", "getPDPrefixInformation")
        if isinstance(d, list):
            return d
        raise LmApiException("DHCPv6.Server:getPDPrefixInformation query error")


    ### Get IPv6 prefix leases
    def get_v6_prefix_leases(self):
        d = self.call_no_check("DHCPv6.Server", "getPDPrefixLeases")
        if isinstance(d, list):
            return d
        raise LmApiException("DHCPv6.Server:getPDPrefixLeases query error")


    ### Get DHCP MIBs information
    def get_mibs(self, dhcp_v4, dhcp_v6):
        p = []
        if dhcp_v4:
            p.append("dhcp")
        if dhcp_v6:
            p.append("dhcpv6")
        mibs = " ".join(p) or None
        if mibs:
            return self.call("NeMo.Intf.data", "getMIBs", {"mibs": mibs})
        raise LmApiException("At least one MIB must be selected")
