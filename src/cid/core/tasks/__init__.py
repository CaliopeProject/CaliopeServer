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

from cid.core.forms import FormManager
from tasksmodel import TaskNode
import json

class TaskManager(object):
    @staticmethod
    @public
    def getAll():
        tasks =   '''    
        {
            "ToDo": [
                {
                    "tarea": "t 1",
                    "description": "Buscar que hacer"
                },
                {
                    "tarea": "t 2",
                    "description": "El ser o el ente?"
                },
                {
                    "tarea": "t 3",
                    "description": "Salvar al mundo (con la panza llena)"
                },
                {
                    "tarea": "t 4",
                    "description": "Adoptar una directiva sin controlador"
                }
            ],
            "Doing": [
                {
                    "tarea": "t 5",
                    "description": "plantilla de tareas"
                }
            ],
            "Done": [
                {
                    "tarea": "t 6",
                    "description": "Perder muchoooo tiempo contando llaves, corchetes y paréntesis"
                },
                {
                    "tarea": "t 7",
                    "description": "hablar mal de JS"
                },
                {
                    "tarea": "t 8",
                    "description": "desterrar a Java"
                }
            ]
        }
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
    def create(data=None, formUUID=None):
        rv = FormManager().edit_form('asignaciones', data, formUUID=formUUID)
        return rv
        #raise JSONRPCInvalidRequestError('Unimplemented')
    
        
    @staticmethod
    @public
    def setState():
        raise JSONRPCInvalidRequestError('Unimplemented')
    