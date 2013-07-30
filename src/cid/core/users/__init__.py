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

#CaliopeStorage
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeUser

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError, JSONRPCInternalError
from tinyrpc.dispatch import public

#Flask
from flask import current_app, g

#from groupmodel import GroupNode

class UsersManager(object):
    @staticmethod
    @public
    def getAll():
        try:
            users = CaliopeUser.index.search('username:*')
            users_list = [user._get_node_data() for user in users]
            return users_list
        except DoesNotExist as e:
            raise JSONRPCInvalidRequestError(e)

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
    def addUser(username,password,group=None):
        raise JSONRPCInvalidRequestError('Unimplemented')
    
    @staticmethod
    @public
    def addGroup(groupname):
        raise JSONRPCInvalidRequestError('Unimplemented')
    