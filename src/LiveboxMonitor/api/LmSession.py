### Livebox Monitor session module ###
# Interfaces copied/adapted from sysbus package - https://github.com/rene-d/sysbus

import os
import sys
import json
import tempfile
import pickle
import datetime
import requests
import requests.utils

from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################
APP_NAME = "so_sdkut"
DEFAULT_TIMEOUT = 5
URL_REDIRECTIONS = {}


# ################################ LmSession class ################################

class LmSession:
    ### Setup
    TimeoutMargin = 0

    ### Constructor
    def __init__(self, url, session_name="LiveboxMonitor"):
        url = url.rstrip(" /") + "/"
    
        # URL redirection handling
        if url in URL_REDIRECTIONS:
            self._url = URL_REDIRECTIONS[url]
            print(f"Redirecting '{url}' to '{self._url}'.")
        else:
            self._url = url

        self._verify = self._url.startswith("http://")
        self._user = ""
        self._password = ""
        self._name = session_name
        self._session = None
        self._channel_id = 0
        self._sah_service_headers = None
        self._sah_event_headers = None


    ### Read a url redirection list and store it in the global dict URL_REDIRECTIONS
    ### this fails silently
    @staticmethod
    def load_url_redirections(redirections):
        def fixTrailingSlash(url):
            return url.rstrip(" /") + "/"

        global URL_REDIRECTIONS
        if not redirections:
            return

        try:
            for i in redirections:
                url_from, url_to = i.split("=", 1)
                url_from = fixTrailingSlash(url_from)
                url_to = fixTrailingSlash(url_to)
                if url_from in URL_REDIRECTIONS:
                    raise Exception("Source redirection URL already declared.")
                URL_REDIRECTIONS[url_from] = url_to
                LmTools.log_debug(1, "Added redirection", url_from, "to", url_to)
        except Exception as e:
            LmTools.error(f"Error while processing redirections: {e}")


    ### Setup timeout margin
    @staticmethod
    def set_timeout_margin(timeout):
        LmSession.TimeoutMargin = timeout


    ### Sign in - return -1 in case of connectivity issue, 0 if sign failed, 1 if sign successful
    def signin(self, user, password, new_session=False):
        # Set cookie & contextID file path
        state_file_path = os.path.join(tempfile.gettempdir(), self._name + "_state")
        LmTools.log_debug(1, "State file", state_file_path)

        # Close current session if any
        self.close()

        # Save current user/password
        self._user = user
        self._password = password

        for _ in range(2):
            if not new_session and os.path.exists(state_file_path):
                LmTools.log_debug(1, "Loading saved cookies")

                with open(state_file_path, "rb") as f:
                    cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
                    self._session = requests.Session()
                    self._channel_id = 0
                    self._session.cookies = cookies
                    context_id = pickle.load(f)
            else:
                LmTools.log_debug(1, f"New session ({self._name})")
                self._session = requests.Session()
                self._channel_id = 0

                LmTools.log_debug(1, "Authentication")
     
                auth = '{"service":"sah.Device.Information","method":"createContext","parameters":{"applicationName":"%s","username":"%s","password":"%s"}}' % (APP_NAME, user, password)

                self._sah_service_headers = {"Accept":"*/*",
                                             "Authorization":"X-Sah-Login",
                                             "Content-Type":"application/x-sah-ws-4-call+json"}

                LmTools.log_debug(2, "Auth with", auth)
                try:
                    r = self._session.post(self._url + "ws",
                                           data=auth,
                                           headers=self._sah_service_headers,
                                           timeout=DEFAULT_TIMEOUT + LmSession.TimeoutMargin,
                                           verify=self._verify)
                except Exception as e:
                    LmTools.error(str(e))
                    self._session = None
                    return -1
                LmTools.log_debug(2, "Auth return", r.text)

                resp_json = r.json()
                if "contextID" not in resp_json.get("data", {}):
                    LmTools.error("Auth error", str(r.text))
                    break

                context_id = resp_json["data"]["contextID"]

                # Saving cookie & contextID
                LmTools.log_debug(1, "Setting cookies")
                with open(state_file_path, "wb") as f:
                    cookie_data = requests.utils.dict_from_cookiejar(self._session.cookies)
                    pickle.dump(cookie_data, f, pickle.HIGHEST_PROTOCOL)
                    pickle.dump(context_id, f, pickle.HIGHEST_PROTOCOL)

            self._sah_service_headers = {"Accept":"*/*",
                                         "Authorization":"X-Sah " + context_id,
                                         "Content-Type":"application/x-sah-ws-4-call+json; charset=UTF-8",
                                         "X-Context": context_id}

            self._sah_event_headers = {"Accept":"*/*",
                                       "Authorization":"X-Sah " + context_id,
                                       "Content-Type":"application/x-sah-event-4-call+json; charset=UTF-8",
                                       "X-Context": context_id}

            # Check authentication
            try:
                r = self._session.post(self._url + "ws",
                                       data='{"service":"Time", "method":"getTime", "parameters":{}}',
                                       headers=self._sah_service_headers,
                                       timeout=DEFAULT_TIMEOUT + LmSession.TimeoutMargin,
                                       verify=self._verify)
            except Exception as e:
                LmTools.error(str(e))
                LmTools.error("Authentification check query failed.")
                os.remove(state_file_path)
                self.close()
                return -1

            if r.json().get("status") is True:
                return 1
            else:
                os.remove(state_file_path)

        LmTools.error("Authentification failed.")
        return 0


    ### Close session
    def close(self):
        if self._session is not None:
            # Fails with access denied error (but same behavior from the web interface...)
            self.request("sah.Device.Information:releaseContext", {"applicationName": APP_NAME})
            self._session = None
            self._channel_id = 0
            self._sah_service_headers = None
            self._sah_event_headers = None


    ### Send service request
    def request(self, service, method=None, args=None, get=False, silent=False, timeout=DEFAULT_TIMEOUT):
        # Check session is established
        if self._session is None:
            if self.signin(self._user, self._password) <= 0:
                return {"errors": "No session"}

        if get:
            # Build request path
            c = "sysbus/" + service.replace(".", "/")
            if method is not None:
                c += ":" + method

            if args is None:
                c += "?_restDepth=-1"
            else:
                c += "?_restDepth=" + str(args)

            LmTools.log_debug(2, f"Request: {c}")
            timestamp = datetime.datetime.now()
            try:
                t = self._session.get(self._url + c,
                                      headers=self._sah_service_headers,
                                      timeout=timeout + LmSession.TimeoutMargin,
                                      verify=self._verify)
                LmTools.log_debug(2, f"Request duration: {datetime.datetime.now() - timestamp}")
                t = t.content
            except requests.exceptions.Timeout as e:
                if not silent:
                    LmTools.error(f"Request timeout error: {e}")
                return None
            except Exception as e:
                if not silent:
                    LmTools.error(f"Request error: {e}")
                return {"errors": "Request exception"}

            t = t.decode("utf-8", errors="replace")
            t = t.replace("[,]", "[]")  # Some lists, like in GET '*' request, contain a failing comma
            if t.startswith(',"errors":'):
                t = "{" + t[1:] + "}"
            elif "}{" in t:
                LmTools.log_debug(2, "Multiple json lists")
                t = "[" + t.replace("}{", "},{") + "]"
        else:
            # Setup request parameters
            data = {}
            data["service"] = "sysbus." + service

            if method is not None:
                data["method"] = method

            if args is not None:
                data["parameters"] = args
            else:
                data["parameters"] = {}

            # Send request & headers
            LmTools.log_debug(2, f"Request: {data}")
            timestamp = datetime.datetime.now()
            try:
                t = self._session.post(self._url + "ws",
                                       data=json.dumps(data),
                                       headers=self._sah_service_headers,
                                       timeout=timeout + LmSession.TimeoutMargin,
                                       verify=self._verify)
                LmTools.log_debug(2, f"Request duration: {datetime.datetime.now() - timestamp}")
                t = t.content
            except requests.exceptions.Timeout as e:
                if not silent:
                    LmTools.error(f"Request timeout error: {e}")
                return None
            except Exception as e:
                if not silent:
                    LmTools.error(f"Request error: {e}")
                return {"errors": "Request exception"}

            t = t.decode("utf-8", errors="replace")

        try:
            r = json.loads(t)
        except Exception:
            if not silent:
                LmTools.error(sys.exc_info()[0])
                LmTools.error("Bad json:", t)
            return None

        overview = str(r)
        if len(overview) > 128:
            overview = overview[:128] + "..."
        LmTools.log_debug(2, "Reply:", overview)

        if not get and "result" in r:
            r = r["result"]
            if "errors" in r:
                if not silent:
                    LmTools.error(t)
                return None

        LmTools.log_debug(2, "-------------------------")
        return r


    ### Send event request
    def event_request(self, events, silent=False, timeout=DEFAULT_TIMEOUT):
        # Check session is established
        if self._session is None:
            if self.signin(self._user, self._password) <= 0:
                return {"errors": "No session"}

        data = {"events": events}
        if self._channel_id:
            data["channelid"] = str(self._channel_id)

        # Send request & headers
        LmTools.log_debug(2, f"Event Request: {data}")
        timestamp = datetime.datetime.now()
        try:
            t = self._session.post(self._url + "ws",
                                   data=json.dumps(data),
                                   headers=self._sah_event_headers,
                                   timeout=timeout,
                                   verify=self._verify)
            LmTools.log_debug(2, f"Request duration: {datetime.datetime.now() - timestamp}")
            t = t.content
        except requests.exceptions.Timeout as e:
            if not silent:
                LmTools.log_debug(2, f"Event request timeout error: {e}")
            return None
        except Exception as e:
            if not silent:
                LmTools.error(f"Event request error: {e}")
            return {"errors": "Event request exception"}

        t = t.decode("utf-8", errors="replace")

        # Remove tailing null if present
        if t.endswith("null"):
            t = t[:-4]

        try:
            r = json.loads(t)
        except Exception:
            if not silent:
                LmTools.error(sys.exc_info()[0])
                LmTools.error("Bad json:", t)
            return None

        overview = str(r)
        if len(overview) > 50:
            overview = overview[:50] + "..."
        LmTools.log_debug(2, "Reply:", overview)

        if "result" in r:
            r = r["result"]
            if "errors" in r:
                if not silent:
                    LmTools.error(t)
                return None

        LmTools.log_debug(2, "-------------------------")
        self._channel_id = r.get("channelid", 0)
        return r
