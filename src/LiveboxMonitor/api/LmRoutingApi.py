### Livebox Monitor Routing APIs ###

from LiveboxMonitor.api.LmApi import LmApi, LmApiException


# ################################ Routing APIs ################################
# WARNING: available ONLY on Livebox Pro models
class RoutingApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get static routes
    def get_list(self):
        d = self.call_no_check("NMC.LAN", "getStaticRoutes", timeout=30)
        if isinstance(d, dict):
            return d
        raise LmApiException("NMC.LAN:getStaticRoutes query error")


    ### Add static route
    def add(self, route):
        self.call_no_check("NMC.LAN", "addStaticRoute", route, timeout=30)


    ### Delete static route
    def delete(self, name):
        self.call_no_check("NMC.LAN", "deleteStaticRoute", {"Name": name}, timeout=30)


    ### Enable/Disable static routes
    def set_enable(self, name, enable):
        self.call(f"NMC.LAN.IPv4Route.{name}", "set", {"Enable": enable}, timeout=30)
