### Livebox Monitor screen & LEDs APIs ###

from LiveboxMonitor.api.LmApi import LmApi


# ################################ Screen APIs ################################
class ScreenApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get Orange LED levels
    def get_orange_led_level(self):
        d = self.call('LEDs.LED.Orange', 'get')
        brightness = d.get('Brightness')
        if brightness is None:
            raise LmApiException('LEDs.LED.Orange:get error: no Brightness field')
        return brightness


    ### Get White LED levels
    def get_white_led_level(self):
        d = self.call('LEDs.LED.White', 'get')
        brightness = d.get('Brightness')
        if brightness is None:
            raise LmApiException('LEDs.LED.White:get error: no Brightness field')
        return brightness


    ### Get Show Wifi Password setup
    def get_show_wifi_password(self):
        return self.call_no_check('Screen', 'getShowWifiPassword')


    ### Set Orange LED level
    def set_orange_led_level(self, level):
        self.call('LEDs.LED.Orange', 'set', {'Brightness': level})


    ### Set White LED level
    def set_white_led_level(self, level):
        self.call('LEDs.LED.White', 'set', {'Brightness': level})


    ### Set Show Wifi Password setup
    def set_show_wifi_password(self, show_wifi_password):
        self.call_no_check('Screen', 'setShowWifiPassword', {'Enable': show_wifi_password})
