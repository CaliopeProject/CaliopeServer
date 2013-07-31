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


        tasks =   '''    
[
    {
        "category": "ToDo",
        "tasks": [
            {
                "uuid" : "1",
                "tarea": "t 1",
                "description": "Buscar que hacer"
            },
            {
                "uuid" : "2",
                "tarea": "t 2",
                "description": "El ser o el ente?"
            },
            {
                "uuid" : "3",
                "tarea": "t 3",
                "description": "Salvar al mundo (con la panza llena)"
            },
            {
                "uuid" : "4",
                "tarea": "t 4",
                "description": "Adoptar una directiva sin controlador"
            }
        ]
    },
    {
        "category": "Doing",
        "tasks": [
            {
                "uuid" : "5",
                "tarea": "t 5",
                "description": "plantilla de tareas"
            }
        ]
    },
    {
        "category": "Done",
        "tasks": [
            {
                "uuid" : "6",
                "tarea": "t 6",
                "description": "Perder muchoooo tiempo contando llaves, corchetes y paréntesis"
            },
            {
                "uuid" : "7",
                "tarea": "t 7",
                "description": "hablar mal de JS"
            },
            {
                "uuid" : "8",
                "tarea": "t 8",
                "description": "desterrar a Java"
            }
        ]
    }
]
        '''

        json_data = json.loads(tasks)
        return json_data
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
            holderUser = form.node.holder.all()[0]
            form.node.holder.disconnect(holderUser)
            
            #print "form.node.ente_asignado "+ form.node.ente_asignado
            holderUser = CaliopeUser.index.get(username=form.node.ente_asignado)
            form.node.holder.connect(holderUser,  properties={'category': 'ToDo'})
            
        return rv
    
        
    @staticmethod
    @public
    def setState():
        raise JSONRPCInvalidRequestError('Unimplemented')
    