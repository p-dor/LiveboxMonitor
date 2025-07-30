### Livebox Monitor DynDNS APIs ###

from LiveboxMonitor.api.LmApi import LmApi, LmApiException


# ################################ DynDNS APIs ################################
class DynDnsApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get DynDNS enable status
    def get_enable(self):
        return self.call_no_check("DynDNS", "getGlobalEnable")


    ### Set DynDNS enable status
    def set_enable(self, enable):
        self.call("DynDNS", "setGlobalEnable", {"enable": enable})


   ### Get DynDNS hosts
    def get_hosts(self):
        d = self.call_no_check("DynDNS", "getHosts")
        if isinstance(d, list):
            return d
        raise LmApiException("DynDNS:getHosts query error")


    ### Get DynDNS services
    def get_services(self):
        d = self.call_no_check("DynDNS", "getServices")
        if isinstance(d, list):
            return d
        raise LmApiException("DynDNS:getServices query error")


    ### Add a host entry.
    def add_host(self, service, username, hostname, password):
        self.call("DynDNS", "addHost", {"service": service,
                                        "username": username,
                                        "hostname": hostname,
                                        "password": password})


    ### Delete a host entry
    def delete_host(self, hostname):
        self.call("DynDNS", "delHost", {"hostname": hostname})
