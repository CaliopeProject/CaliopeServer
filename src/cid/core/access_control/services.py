#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

from cid.utils.fileUtils import loadJSONFromFile
from cid.core.login import LoginManager
from functools import wraps

import access_control
import os

class AccessControlManager:
    @staticmethod
    def get_acl():
        """
          Instanciate the access control object and return it.
          Read the current ACL configuration.
        """
        acl_conf = loadJSONFromFile('conf/permissions.json')
        return access_control.AccessControl(acl_conf)

    @staticmethod
    def check_permission(action="read", uuid_pos=1, class_type=None):
        def wrap(f):
            def wrapped_f(*args, **kwargs):
                ac = AccessControlManager.get_acl()
                versioned_node_class = getattr(f, "func_globals")[
                    "VersionedNode"]
                class_type = versioned_node_class.pull(args[uuid_pos],
                                                       only_class=True)

                if ac.is_access_granted(LoginManager.get_user(), action,
                                        class_type):
                    return f(*args, **kwargs)
                else:
                    raise RuntimeError("No available {}".format(f.__name__))

            return wrapped_f

        return wrap


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

    @staticmethod
    @public(name='getGroupsOfUser')
    def get_groups_for_user(user):
        acl = AccessControlManager.get_acl()
        return list(acl.get_groups_for_user(user))

    @staticmethod
    @public(name='getUsersOfGroup')
    def get_users_of_group(group):
        acl = AccessControlManager.get_acl()
        return acl.get_users_in_grup(group)

    @staticmethod
    @public(name='getUserPermissions')
    def get_user_permissions(user):
        acl = AccessControlManager.get_acl()
        return acl.get_user_permissions(user)

    @staticmethod
    @public(name='getActionList')
    def get_action_list(params):
        acl = AccessControlManager.get_acl()
        return acl.get_action_names()

    @staticmethod
    @public(name='getThingList')
    def get_thing_list(params):
        acl = AccessControlManager.get_acl()
        return acl.get_thing_names()
