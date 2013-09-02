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
#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInternalError
from tinyrpc.dispatch import public

#Flask
from cid.core.entities.base_models.entities_models import CaliopeDocument


class DocumentManager(object):
    @staticmethod
    @public
    def getAll():
        return JSONRPCInternalError('Unimplemented')

    @staticmethod
    @public
    def getFilteredByProyect(proyect_id):
        return JSONRPCInternalError('Unimplemented')

    @staticmethod
    @public
    def setState():
        return JSONRPCInternalError('Unimplemented')

    @staticmethod
    def addDocument(parent_uuid, url, description):
        node = CaliopeDocument()
        node.add_to_repo(parent_uuid, url, description)
        
        