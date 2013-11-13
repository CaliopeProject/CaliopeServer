#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

from cid.utils.fileUtils import loadJSONFromFile
from flask.globals import current_app

import access_control

class AccessControlManager:
    @staticmethod
    def get_acl():
        """ Instanciate the access control object and return it.
            Read the current ACL configuration.
        """
"""
        # TODO(nel): Move from a file to another kind of configuration.
        acl_path = os.path.join(current_app.config['cid_base_directory'],
                                'conf',
                                current_app.config['server']['acl_file'])
        conf = loadJSONFromFile(current_app.config['server']['acl_file'] , 'conf' )
        with open(acl_path) as acl_file:
            return access_control.AccessControl(acl_file.read())
            """

    @staticmethod
    @public(name='isAccessGranted')
    def list_groups(params):
        #TODO(nel): Get rid of the parameters.
        acl = AccessControlManager.get_acl()


    @staticmethod
    @public(name='isAccessGranted')
    def is_access_granted(params):
        # Unused.
        acl = AccessControlManager.get_acl()
        rv = {
            'granted': True,
        }
        return rv
