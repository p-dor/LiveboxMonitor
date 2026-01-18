### Livebox Monitor TV Decoder APIs ###

# ### Resources used as reference to build this module ###
# https://github.com/AkA57/liveboxtvuhd
# https://github.com/DalFanajin/Orange-Livebox-TV-UHD-4K-python-controller
# https://github.com/bbastou/livebox-remote/tree/master
# https://gist.github.com/alexandrevilain/c74fd7dabe148c8a16092eba38267c63
# https://github.com/Spine34/jeedom-plugin-tvByOrange
# https://github.com/f-lawe/plugin.video.orange.fr

import json
import requests
import xmltodict
from random import randint
from enum import IntEnum

from LiveboxMonitor.api.LmApi import LmApiException


# ################################ VARS & DEFS ################################
class Key(IntEnum):
    C = 14
    OK_ALT = 28
    UP = 72
    LEFT = 75
    RIGHT = 77
    DOWN = 80
    UP_ALT = 103
    LEFT_ALT = 105
    RIGHT_ALT = 106
    DOWN_ALT = 108
    MUTE = 113
    VOL_DOWN = 114
    VOL_UP = 115
    POWER = 116
    MENU = 139
    BACK = 158
    FFWD = 159
    PLAY = 164
    REC = 167
    FBWD = 168
    OK = 352
    PROG = 365
    VOD = 393
    CHAN_UP = 402
    CHAN_DOWN = 403
    ZERO = 512
    ONE = 513
    TWO = 514
    THREE = 515
    FOUR = 516
    FIVE = 517
    SIX = 518
    SEVEN = 519
    EIGHT = 520
    NINE = 521
    MIC = 582

class KeyMode(IntEnum):
    PRESS_ONCE = 0
    PRESS_HOLD = 1
    RELEASE = 2

DEFAULT_TIMEOUT = 3

OSD_CONTEXT_MAP = {
    "AmazonInstantVideo": "Amazon Prime",
    "AppShop": "Application menu",
    "CANAL": "Canal+ offer",
    "CANALUNIVERSE": "Canal+",
    "chaines-locales": "Local TNT channels menu",
    "DIGITAL_HOME": "Media Center home",
    "FILMOTV": "Filmo commercial offer",
    "GAMES": "Video Games",
    "guidetv": "TV Guide",
    "GULLI": "GulliMax offer",
    "HOMEPAGE": "Orange main menu",
    "hotlinemenu": "Administration",
    "ISMOSAIC": "Thematic video pass",
    "LEGUIDETV": "Replay menu",
    "LIVE": "Television",
    "MAIN_PROCESS": "Standby",
    "MusicEntry": "Music menu",
    "MYACCOUNT": "My Account menu",
    "mytf1max": "TF1+",
    "NA": "-",
    "NAP:INTERNET": "Internet application",
    "NAP:mediacenter": "Media Center menu",
    "netflix": "Netflix",
    "ONEIMUSIC": "Orange Radio & Music",
    "paramount": "Paramount offer",
    "PROMO_TV": "Canal+ application",
    "PROMO_TV_LIVE": "Commercial offer",
    "PVR": "Recording menu",
    "SEARCH": "Search menu",
    "shopxocav": "Commercial offer",
    "TFOUMAX": "Tfou Max offer",
    "TVEP": "Commercial offer",
    "UPSELLTV": "Commercial offer",
    "UWA:ClouddOrange": "Orange Cloud",
    "VOD": "Video on demand",
    "VODFACTORY": "Ina Madelen offer",
    "youtube": "YouTube",
    "6PLAYRNG": "M6+"
}

USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.3",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.3",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0",  # noqa: E501
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.",
    # Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.",  # noqa: E501
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.1",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.1",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.1",  # noqa: E501
]

CHANNELS_URL = "https://rp-ott-mediation-tv.woopic.com/api-gw/pds/v1/live/ew?everywherePopulation=OTT_Metro"
CHANNEL_ICON_URL = "https://proxymedia.woopic.com/api/v1/images/2090{}"



# ################################ TV Decoder APIs ################################
# ###WARNIN### : device must be ACTIVE to call those APIs, otherwise they will just timeout

class TvDecoderApi:
    tv_channels = None


    ### Init
    def __init__(self, decoder_ip):
        self.set_ip(decoder_ip)


    ### Update IP address
    def set_ip(self, decoder_ip):
        self._ip = decoder_ip


    ### Load TV channels information
    @staticmethod
    def load_channels():
        if not TvDecoderApi.tv_channels:
            try:
                resp = TvDecoderApi.web_request(CHANNELS_URL)
                resp.raise_for_status()     # Check HTTP status code
                data = resp.json()

                # Check if error
                err_msg = data.get("message")
                if err_msg:
                    err_desc = data.get("description", "")
                    err_code = data.get("code", 0)
                    raise LmApiException(f"Channels query error: {err_msg} - {err_desc} [{err_code}]")

                tv_channels = data.get("channels")
                if tv_channels:
                    TvDecoderApi.tv_channels = tv_channels
                else:
                    raise LmApiException(f"Channels query error: no channels found")
            except Exception as e:
                raise LmApiException(f"Channels query error: {e}")


    ### Get TV channels information
    @staticmethod
    def get_channels():
        return TvDecoderApi.tv_channels


    ### Set TV channels information
    @staticmethod
    def set_channels(channels):
        TvDecoderApi.tv_channels = channels


    ### Press a key
    def key_press(self, key, mode=KeyMode.PRESS_ONCE):
        try:
            resp = requests.get(f"http://{self._ip}:8080/remoteControl/cmd?operation=01&key={key}&mode={mode}", timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()     # Check HTTP status code
            data = resp.json()
            result = data.get("result")
            if result:
                msg = result.get("message")
                if msg == "ok":
                    return
                raise LmApiException(f"TvDecoder key_press query error: {msg} [{result.get('responseCode')}]")
            raise LmApiException(f"TvDecoder key_press query error: no result")
        except requests.exceptions.Timeout:
            raise LmApiException(f"Timeout connecting to TVDecoder {self._ip}")
        except Exception as e:
            raise LmApiException(f"TvDecoder key_press query error: {e}")


    ### Change channel providing its EPG ID
    def change_channel(self, epg):
        epg = f"{epg:*>10}"     # set a string of 10 chars padded left with *
        try:
            resp = requests.get(f"http://{self._ip}:8080/remoteControl/cmd?operation=09&epg_id={epg}&uui=1", timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()     # Check HTTP status code
            data = resp.json()
            result = data.get("result")
            if result:
                msg = result.get("message")
                if msg == "ok":
                    return
                raise LmApiException(f"TvDecoder change_channel query error: {msg} [{result.get('responseCode')}]")
            raise LmApiException(f"TvDecoder change_channel query error: no result")
        except requests.exceptions.Timeout:
            raise LmApiException(f"Timeout connecting to TVDecoder {self._ip}")
        except Exception as e:
            raise LmApiException(f"TvDecoder change_channel query error: {e}")


    ### Get basic description
    def get_basic_description(self):
        try:
            resp = requests.get(f"http://{self._ip}:8080/BasicDeviceDescription.xml", timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()     # Check HTTP status code
            return xmltodict.parse(resp.content)["root"]["device"]
        except requests.exceptions.Timeout:
            raise LmApiException(f"Timeout connecting to TVDecoder {self._ip}")
        except Exception as e:
            raise LmApiException(f"TvDecoder get_basic_description query error: {e}")


    ### Get description
    def get_description(self):
        try:
            resp = requests.get(f"http://{self._ip}:52235/devicedescription.xml", timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()     # Check HTTP status code
            return xmltodict.parse(resp.content)["root"]["device"]
        except requests.exceptions.Timeout:
            raise LmApiException(f"Timeout connecting to TVDecoder {self._ip}")
        except Exception as e:
            raise LmApiException(f"TvDecoder get_description query error: {e}")


    ### Get status
    def get_status(self):
        try:
            resp = requests.get(f"http://{self._ip}:8080/remoteControl/cmd?operation=10", timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()     # Check HTTP status code
            data = resp.json()
            result = data["result"]
            if result["responseCode"] != "0":
                raise LmApiException(f"TvDecoder get_status bad response code: {result['responseCode']}")
            if result["message"] != "ok":
                raise LmApiException(f"TvDecoder get_status bad status code: {result['message']}")
            return result["data"]
        except requests.exceptions.Timeout:
            raise LmApiException(f"Timeout connecting to TVDecoder {self._ip}")
        except Exception as e:
            raise LmApiException(f"TvDecoder get_status query error: {e}")


    ### State field (osdContext) decoder
    def decode_status(self, status):
        if status:
            return OSD_CONTEXT_MAP.get(status, status)
        return status


    ### Type field (playedMediaType) decoder
    def decode_type(self, type):
        if not type or (type == "NA"):
            return "-"
        return type


    ### Status field (playedMediaState) decoder
    def decode_state(self, state):
        if not state or (state == "NA"):
            return "-"
        return state


    ### EPG field (playedMediaId) decoder
    def decode_epg(self, epg):
        if not epg or (epg == "NA"):
            return "-"
        return epg


    ### Retrieve channel EPG from its number - return None if not found
    def get_epg_from_number(self, number):
        if TvDecoderApi.tv_channels:
            try:
                n = int(number)
            except:
                return None

            channel = next((c for c in TvDecoderApi.tv_channels if c.get("displayOrder", 0) == n), None)
            if channel:
                return channel.get("idEPG")

        return None


    ### Retrieve channel EPG from its name - return None if not found
    def get_epg_from_name(self, name):
        if TvDecoderApi.tv_channels:
            name = name.lower()
            # First try exact match
            channel = next((c for c in TvDecoderApi.tv_channels if name == c.get("name", "").lower()), None)

            # If not found, find as substring
            if not channel:
                channel = next((c for c in TvDecoderApi.tv_channels if name in c.get("name", "").lower()), None)

            if channel:
                return channel.get("idEPG")

        return None


    ### Retrieve channel information from EPG field (playedMediaId)
    def get_channel_infos(self, epg):
        infos = {
            "name": "-",
            "number": "-",
            "desc": "",
            "icon": None
        }

        if TvDecoderApi.tv_channels:
            try:
                epg_int = int(epg)
            except:
                return infos

            channel = next((c for c in TvDecoderApi.tv_channels if c.get("idEPG", 0) == epg_int), None)
            if channel:
                infos["name"] = channel.get("name", "?")
                infos["number"] = str(channel.get("displayOrder", "-"))
                infos["desc"] = channel.get("slogan")
                infos["icon"] = TvDecoderApi.get_channel_icon(channel)

        return infos


    ### Get channel icon from channel information
    # Icon type can be "mobileAppli", "mobileAppliDark", "webTVLogo" or "webTVSquare"
    @staticmethod
    def get_channel_icon(channel, icon_type="webTVSquare"):
        if channel:
            logos = channel.get("logos")
            if logos:
                logo_def = next((l for l in logos if l.get("definitionType") == icon_type), None)
                if logo_def:
                    logo_list = logo_def.get("listLogos")
                    if logo_list:
                        path = logo_list[0].get("path")
                        if path:
                            if path.startswith("https"):
                                return path
                            else:
                                return CHANNEL_ICON_URL.format(path)
        return None


    ### Get channel icon from channel information
    @staticmethod
    def web_request(url, timeout=5):
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "*",
            "Sec-Fetch-Mode": "cors",
            "User-Agent": USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
        }

        session = requests.Session()
        resp = session.request("GET", url, headers=headers, timeout=timeout)
        return resp
