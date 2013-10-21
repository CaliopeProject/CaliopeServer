# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM2 Server is the web server of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
#
from neomodel import DoesNotExist

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

#Flask

#from groupmodel import GroupNode
from cid.core.entities import CaliopeUser, CaliopeNode
from cid.utils.thumbnails import get_thumbnail

from flask.globals import current_app


class UsersManager(object):
    @staticmethod
    @public
    def getAll():
        try:
            users = CaliopeUser.index.search('username:*')
            users_list = []
            for user in users:
                users_list.append(UsersManager.get_user_node_data(user))
            return users_list
        except DoesNotExist as e:
            raise JSONRPCInvalidRequestError(e)

    @staticmethod
    @public
    def getGroups():
        raise JSONRPCInvalidRequestError('Unimplemented')


    @staticmethod
    @public(name='getThumbnail')
    def get_thumbnail(user):
        rv = {
            "image":
                get_thumbnail(os.path.join(current_app.config['STATIC_PATH'], user.avatar))
        }
        return rv

    @staticmethod
    @public(name='getThumbnailList')
    def get_thumbnail_list(users):
        rv = []
        for uuid in users:
            try:
                user = CaliopeUser.index.get(uuid=uuid)
                get_thumbnail(os.path.join(current_app.config['STATIC_PATH'], user.avatar))
            except DoesNotExist as e:
                current_app.logger.info('CaliopeUser with uuid: ' + uuid + 'not found')
                pass
        return rv


    @staticmethod
    @public(name='getPublicInfo')
    def get_public_info(users):
        rv = []
        for uuid in users:
            try:
                user = CaliopeUser.index.get(uuid=uuid)
                rv.append(dict(UsersManager.get_user_node_data(user),
                               **UsersManager.get_thumbnail(user)))
            except DoesNotExist as e:
                current_app.logger.info('CaliopeUser with uuid: ' + uuid + 'not found')
                pass
        return rv


    @staticmethod
    @public
    def getGroups():
        raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    @public
    def getFilteredByProyect(proyect_id):
        raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    @public
    def getFilteredByGroup(proyect_id):
        raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    @public
    def addUser(username, password, group=None):
        raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    @public
    def addGroup(groupname):
        raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    def get_user_node_data(user_node):
        rv = {}
        data = user_node._get_node_data()
        for k, v in data.items():
            if not isinstance(v, unicode):
                v = unicode(v)
            data[k] = {'value': v}
        data['name'] = {'value': data['first_name']['value'] + ' ' + data['last_name']['value']}
        rv = {u'name': data['name'],
              u'username': data['username'],
              u'first_name': data['first_name'],
              u'last_name': data['last_name'],
              u'uuid': data['uuid'],
              u'image': get_thumbnail(os.path.join(current_app.config['STATIC_PATH'], data['avatar']['value']))
        }
        return rv
