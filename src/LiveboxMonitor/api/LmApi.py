### Livebox Monitor APIs base class ###

import os
import json

from LiveboxMonitor.app import LmTools


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
    def err_str(package, method=None, err_str=None):
        e = package
        if method:
            e += ':' + method
        if err_str:
            e += ' ' + err_str
        return e


    ### Compute error description from Livebox reply
    @staticmethod
    def get_error_str(desc, info, id=None):
        parts = []
        if id is not None:
            parts.append(f'[{id}]')
        if desc:
            parts.append(desc)
        if info:
            if desc:
                parts.append(f'-> {info}')
            else:
                parts.append(info)
        if parts:
            return ' '.join(parts) + '.\n'
        return ''


    ### Collect potential error description(s) from Livebox reply
    @staticmethod
    def get_errors(reply):
        if reply:
            errors = reply.get('errors')
            if isinstance(errors, list):
                return ''.join(LmApi.get_error_str(e.get('description'), e.get('info')) for e in errors)
            else:
                e = reply.get('error')
                if e is not None:
                    return LmApi.get_error_str(reply.get('description'), reply.get('info'), e)
        return ''


    ### Call a Livebox API - raise exception or return the full reply, cannot be None and contains 'status'
    def call_raw(self, package, method=None, args=None, timeout=None, err_str=None):
        if TEST_MODE:
            signature = self.get_call_signature(package, method, args)
            # Look for a file in test folder matching call signature
            test_file_path = os.path.join('test', TEST_MODE, f'{signature}.json')
            test_file = None
            try:
                test_file = open(test_file_path)
                d = json.load(test_file)
                LmTools.log_debug(1, f'Testing with: {test_file_path}')
            except OSError:
                d = None    # No test file found
            except Exception as e:
                LmTools.error(f'Wrong JSON {signature}.json: {e}')
                raise LmApiException(f'{self.err_str(package, method, err_str)}: bad test driver json')
            finally:
                if test_file is not None:
                    test_file.close()
        else:
            d = None

        # Call Livebox API
        if not d:
            try:
                if timeout is None:
                    d = self._session.request(package, method, args)
                else:
                    d = self._session.request(package, method, args, timeout=timeout)
            except Exception as e:
                raise LmApiException(f'{self.err_str(package, method, err_str)}: {e}.') from e

        # Check reply
        if d is not None:
            e = self.get_errors(d)
            if e:
                raise LmApiException(f'{self.err_str(package, method, err_str)}: {e}')
            if 'status' in d:
                return d

        raise LmApiException(self.err_str(package, method, err_str) + ' service error.')


    ### Call a Livebox API - raise exception or return 'status' value, can be None
    def call_no_check(self, package, method=None, args=None, timeout=None, err_str=None):
        return self.call_raw(package, method, args, timeout, err_str).get('status')


    ### Call a Livebox API - raise exception or return 'status' value if not '', 0, False or None
    def call(self, package, method=None, args=None, timeout=None, err_str=None):
        d = self.call_no_check(package, method, args, timeout, err_str)
        if not d:
            raise LmApiException(self.err_str(package, method, err_str) + ' service failed.')
        return d


    ### Test mode - get API call signature
    @staticmethod
    def get_call_signature(package, method, args):
        signature = package
        if method:
            signature += f'_{method}'
        if args:
            for arg in args:
                signature += f'_{arg}-{str(args[arg]).replace(" ", "_")}'
        return signature
