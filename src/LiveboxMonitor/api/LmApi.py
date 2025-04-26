### Livebox Monitor APIs base class ###


# ################################ Livebox Monitor APIs ################################
class LmApi:
    def __init__(self, api_registry, session):
        self._api = api_registry    # ApiRegistry instance
        self._session = session     # LmSession instance


    ### Compute error string
    @staticmethod
    def err_str(package, method=None, err_str=None):
        e = package
        if method is not None:
            e += ':' + method
        if err_str is not None:
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
        # Call Livebox API
        try:
            if timeout is None:
                d = self._session.request(package, method, args)
            else:
                d = self._session.request(package, method, args, timeout=timeout)
        except BaseException as e:
            raise Exception(f'{self.err_str(package, method, err_str)}: {e}.') from e
        if d is not None:
            e = self.get_errors(d)
            if e:
                raise Exception(f'{self.err_str(package, method, err_str)}: {e}')
            if 'status' in d:
                return d

        raise Exception(self.err_str(package, method, err_str) + ' service error.')


    ### Call a Livebox API - raise exception or return 'status' value, can be None
    def call_no_check(self, package, method=None, args=None, timeout=None, err_str=None):
        return self.call_raw(package, method, args, timeout, err_str).get('status')


    ### Call a Livebox API - raise exception or return 'status' value if not '', 0, False or None
    def call(self, package, method=None, args=None, timeout=None, err_str=None):
        d = self.call_no_check(package, method, args, timeout, err_str)
        if not d:
            raise Exception(self.err_str(package, method, err_str) + ' service failed.')
        return d
