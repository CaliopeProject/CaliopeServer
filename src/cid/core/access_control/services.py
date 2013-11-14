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
        """
          Instanciate the access control object and return it.
          Read the current ACL configuration.
        """
        acl_conf = loadJSONFromFile('../../conf/permissions_for_test.json')
        return access_control.AccessControl(acl_conf)

    @staticmethod
    @public(name='isAccessGranted')
    def is_access_granted(params):
        return {
            'granted': True
        }

    @staticmethod
    @public(name='getUserList')
    def get_user_list(params):
        acl = AccessControlManager.get_acl()
        return acl.groups_for_user.keys()

    @staticmethod
    @public(name='getGroupList')
    def get_group_list(params):
        acl = AccessControlManager.get_acl()
        return acl.get_group_shorthands()
