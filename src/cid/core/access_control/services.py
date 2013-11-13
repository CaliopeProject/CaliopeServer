#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

from flask.globals import current_app

import json
import os

import access_control



class AccessControlManager:
    @staticmethod
    def get_acl():
        """ Instanciate the access control object and return it.
            Read the current ACL configuration.
        """
        # TODO(nel): Move from a file to another kind of configuration.
        acl_path = os.path.join(current_app.config['cid_base_directory'],
                                'core/access_control/',
                                current_app.config['server']['acl_file'])
        with open(acl_path) as acl_file:
            return access_control.AccessControl(acl_file.read())

    @staticmethod
    @public(name='isAccessGranted')
    def is_access_granted(params):
        # Unused.
        acl = AccessControlManager.get_acl()
        rv = {
            'granted': True,
        }
        return rv
