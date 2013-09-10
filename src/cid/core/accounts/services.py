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
from cid.core.entities.base_models.entities_models import CaliopeUser
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
                data = user._get_node_data()
                for k, v in data.items():
                    if not isinstance(v, unicode):
                        v = unicode(v)
                    data[k] = {'value': v}
                data['name'] = {'value': data['first_name']['value'] + ' ' + data['last_name']['value']}
                users_list.append({u'name': data['name'],
                                   u'username': data['username'],
                                   u'first_name': data['first_name'],
                                   u'last_name': data['last_name']})
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
            "image" :
            get_thumbnail(os.path.join(current_app.config['STATIC_PATH'], 'common-img/avatar1.png'))
        }
        return rv


    @staticmethod
    @public(name='getThumbnailList')
    def get_thumbnail_list(users):
        rv = []
        for user in users:
            rv.append({
                user:
                get_thumbnail(os.path.join(current_app.config['STATIC_PATH'], 'common-img/avatar1.png'))
            })
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
