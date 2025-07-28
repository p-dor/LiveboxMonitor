### Livebox Monitor Routing APIs ###

from LiveboxMonitor.api.LmApi import LmApi, LmApiException


# ################################ Routing APIs ################################
# WARNING: available ONLY on Livebox Pro models
class RoutingApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get static routes
    def get_static_routes(self):
        d = self.call_no_check("NMC.LAN", "getStaticRoutes")
        if isinstance(d, dict):
            return d
        raise LmApiException("NMC.LAN:getStaticRoutes query error")


    ### Add static routes
    def add_static_routes(self, route):
        self.call_no_check("NMC.LAN", "addStaticRoute", route)


    ### Delete static routes
    def del_static_routes(self, name):
        self.call_no_check("NMC.LAN", "deleteStaticRoute", {"Name": name})


    ### Enable/Disable static routes
    def set_static_routes_enable(self, name, enable):
        self.call(f"NMC.LAN.IPv4Route.{name}", "set", {"Enable": enable})
