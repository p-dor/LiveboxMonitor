### Livebox Monitor APIs base class ###

import os
import json
import hashlib
import base64

from LiveboxMonitor.tools import LmTools


# ################################ VARS & DEFS ################################
TEST_MODE = None    # Set to the name of the test folder containing matching call signatures


# ################################ Exceptions ################################
class LmApiException(Exception):
    """Livebox Monitor APIs exception."""


# ################################ Livebox Monitor APIs ################################
class LmApi:
    def __init__(self, api_registry):
        self._api = api_registry    # ApiRegistry instance
        self._session = self._api._session


    ### Compute error string
    @staticmethod
    def err_str(service, method=None, err_str=None):
        e = service
        if method:
            e += f":{method}"
        if err_str:
            e += f" {err_str}"
        return e


    ### Compute error description from Livebox reply
    @staticmethod
    def get_error_str(desc, info, err_id=None):
        parts = []
        if err_id is not None:
            parts.append(f"[{err_id}]")
        if desc:
            parts.append(desc)
        if info:
            if desc:
                parts.append(f"-> {info}")
            else:
                parts.append(info)
        if parts:
            return " ".join(parts) + "."
        return ""


    ### Collect potential error description(s) from Livebox reply
    @staticmethod
    def get_errors(reply):
        if reply:
            errors = reply.get("errors")
            if isinstance(errors, list):
                return "\n".join(LmApi.get_error_str(e.get("description"), e.get("info")) for e in errors)
            else:
                e = reply.get("error")
                if e is not None:
                    return LmApi.get_error_str(reply.get("description"), reply.get("info"), e)
        return ""


    ### Call a Livebox API - raise exception or return the full reply, cannot be None and contains 'status'
    def call_raw(self, service, method=None, args=None, timeout=None, err_str=None):
        d = self.get_mockup(service, method, args) if TEST_MODE else None

        # Call Livebox API
        if not d:
            if not self._session:
                raise LmApiException("No session")
            try:
                if timeout:
                    d = self._session.request(service, method, args, timeout=timeout)
                else:
                    d = self._session.request(service, method, args)
            except Exception as e:
                raise LmApiException(f"{self.err_str(service, method, err_str)}: {e}.") from e

        # Check reply
        if d is not None:
            e = self.get_errors(d)
            if e:
                raise LmApiException(f"{self.err_str(service, method, err_str)}: {e}")
            if "status" in d:
                return d

        raise LmApiException(self.err_str(service, method, err_str) + " service error")


    ### Call a Livebox API - raise exception or return 'status' value, can be None
    def call_no_check(self, service, method=None, args=None, timeout=None, err_str=None):
        return self.call_raw(service, method, args, timeout, err_str).get("status")


    ### Call a Livebox API - raise exception or return 'status' value if not '', 0, False or None
    def call(self, service, method=None, args=None, timeout=None, err_str=None):
        d = self.call_no_check(service, method, args, timeout, err_str)
        if not d:
            raise LmApiException(self.err_str(service, method, err_str) + " service failed")
        return d


    ### Notification that the session has been closed
    def session_closed(self):
        self._session = None


    ### Test mode - try to find a call mockup
    @staticmethod
    def get_mockup(service, method, args):
        if args: # If args, try with full signature then simple
            mockup = LmApi.find_mockup(service, method, args)
            if mockup:
                return mockup
        return LmApi.find_mockup(service, method, None)


    ### Test mode - find a call mockup file matching criteria
    @staticmethod
    def find_mockup(service, method, args):
        signature = LmApi.get_call_signature(service, method, args)

        # Look for a file in test folder matching call signature
        test_file_path = os.path.join("test", TEST_MODE, f"{signature}.json")
        # LmTools.log_debug(1, f'Looking for testing with: {test_file_path}')

        test_file = None
        mockup = None
        try:
            test_file = open(test_file_path)
            mockup = json.load(test_file)
            LmTools.log_debug(1, f"Testing with: {test_file_path}")
        except OSError:
            mockup = None    # No test file found
        except Exception as e:
            LmTools.error(f"Wrong JSON {signature}.json: {e}")
            raise LmApiException(f"{LmApi.err_str(service, method, err_str)}: bad test driver json")
        finally:
            if test_file is not None:
                test_file.close()

        return mockup


    ### Test mode - get API call signature
    @staticmethod
    def get_call_signature(service, method, args):
        sign_list = [service.replace(".", "_")]
        if method:
            sign_list.append(method)
        if args:
            arg_sign = "_".join(LmApi.get_arg_signature(args))
            if len(arg_sign) > 50:
                arg_sign = LmApi.hash_arguments(arg_sign)
            sign_list.append(arg_sign)
        return "_".join(sign_list)


    ### Test mode - get arg signature
    @staticmethod
    def get_arg_signature(arg):
        items = []
        if isinstance(arg, dict):
            for k, v in arg.items():
                items.append(k)
                items.extend(LmApi.get_arg_signature(v))
        elif isinstance(arg, (list, tuple)):
            for v in arg:
                items.extend(LmApi.get_arg_signature(v))
        else:
            items.append(str(arg).replace(" ", "_"))
        return items


    ### Test mode - hash arguments for API call signature
    @staticmethod
    def hash_arguments(string, algorithm="sha256"):
        # Use the specified hash algorithm
        h = hashlib.new(algorithm)
        h.update(string.encode("utf-8"))
        # Use base64 for compactness, but make it filesystem-safe
        hash_bytes = h.digest()
        hash_b64 = base64.urlsafe_b64encode(hash_bytes).decode("utf-8")
        return hash_b64
