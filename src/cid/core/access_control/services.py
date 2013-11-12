__author__ = 'afc'

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

class AccessControlManager:
    @staticmethod
    @public(name='isAccessGranted')
    def is_access_granted(params):
        rv = {
            "granted": True
        }
        return rv
