#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

from flask.globals import current_app

import json


class AccessControlManager:
    @staticmethod
    @public(name='isAccessGranted')
    def is_access_granted(params):
        rv = {
            'granted': True,
            'test' : str(current_app.config['server']['acl_file'])
        }
        return rv
