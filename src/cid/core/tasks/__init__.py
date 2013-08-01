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
from neomodel import DoesNotExist, RelationshipTo, RelationshipFrom
from odisea.CaliopeStorage import CaliopeUser

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError, JSONRPCInternalError
from tinyrpc.dispatch import public

#Flask
from flask import current_app, g

from cid.core.login import LoginManager
from cid.core.forms import FormManager,Form
from tasksmodel import TaskNode
import json

class TaskManager(object):
    @staticmethod
    @public
    def getAll():
        userNode = CaliopeUser.index.get( username=LoginManager().get_user() )
        
        result = userNode.cypher("START s=node:CaliopeUser('username:" + LoginManager().get_user() + "')" +
                          " MATCH (s)-[r:HOLDER]-(x) " +
                          " WHERE has(r.category)" + 
                          " Return x,r.category", {'username': LoginManager().get_user()})[0]
                          
        
        ToDo  = {'category': 'ToDo',  'tasks': []}
        Doing = {'category': 'Doing', 'tasks': []}
        Done  = {'category': 'Done',  'tasks': []}
        for r in result:
            task = { 
                'uuid':        r[0]['uuid'], 
                'tarea':       r[0]['tarea'], 
                'description': r[0]['descripcion']
                }
            if r[1] == 'ToDo':
                ToDo['tasks'].append(task)
            elif r[1] == 'Doing':
                Doing['tasks'].append(task)
            elif r[1] == 'Done':
                Done['tasks'].append(task)
               
        tasks = [ToDo,Doing,Done]
        return tasks 
        #raise JSONRPCInvalidRequestError('Unimplemented')
    
    @staticmethod
    @public
    def getFilteredByProyect(proyect_id):
        raise JSONRPCInvalidRequestError('Unimplemented')
    
    @staticmethod
    @public
    def create(formId=None, data=None, formUUID=None):
        #TODO: chequearlo todo!!!!!!!!!!
        if 'asignaciones' != formId:
            raise JSONRPCInvalidRequestError('unexpected formId')        
        form = Form(formId=formId)
        rv = form.create_form(data,formUUID)
        
        if hasattr(form.node, 'ente_asignado'):
            holder_user = form.node.ente_asignado
        else:
            holder_user = LoginManager().get_user()
            
        holderUser = form.node.holder.all()[0]
        form.node.holder.disconnect(holderUser)
        holderUser = CaliopeUser.index.get(username=holder_user)
        form.node.holder.connect(holderUser,  properties={'category': 'ToDo'})
       
        return rv
    
    @staticmethod
    @public
    def edit(formId=None, data=None, formUUID=None):
        #TODO: chequearlo todo!!!!!!!!!!
        if 'asignaciones' != formId:
            raise JSONRPCInvalidRequestError('unexpected formId')
        form = Form(formId=formId)
        rv = form.update_form_data(data['uuid'], data);
        
        return rv    
    
        
    @staticmethod
    @public
    def setState():
        raise JSONRPCInvalidRequestError('Unimplemented')
    