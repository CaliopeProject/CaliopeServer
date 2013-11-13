#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

from cid.utils.fileUtils import loadJSONFromFile
from flask.globals import current_app

import access_control
import os

class AccessControlManager:
    @staticmethod
    def get_acl():
        """ Instanciate the access control object and return it.
            Read the current ACL configuration.
        """
        acl_conf = loadJSONFromFile(current_app.config['server']['acl_file'],
                                    os.path.join(current_app.root_path, '../../'))
        return access_control.AccessControl(acl_conf)

    @staticmethod
    @public(name='isAccessGranted')
    def is_access_granted(params):

        # ***************************** Unused ****************************
        acl = AccessControlManager.get_acl()
        # ***************************** Unused ****************************

        rv = {
            'granted': True
        }
        return rv
