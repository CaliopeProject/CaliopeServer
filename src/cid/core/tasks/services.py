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
from cid.core.models import CaliopeUser

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

#Flask

from cid.core.login import LoginManager

from models import Task, TaskData


class TaskManager(object):
    @staticmethod
    @public
    def getAll():
        userNode = CaliopeUser.index.get(username=LoginManager().get_user())

        result = userNode.cypher("START s=node:CaliopeUser('username:" + LoginManager().get_user() + "')" +
                                 " MATCH (s)-[r:HOLDER]-(x)-[e:CURRENT]-(t) " +
                                 " WHERE has(r.category)" +
                                 " Return t,r.category", {})[0]

        ToDo = {'category': 'ToDo', 'tasks': []}
        Doing = {'category': 'Doing', 'tasks': []}
        Done = {'category': 'Done', 'tasks': []}
        for r in result:
            task = {
                'uuid': r[0]['uuid'],
                'tarea': r[0]['tarea'],
                'description': r[0]['descripcion']
            }
            if r[1] == 'ToDo':
                ToDo['tasks'].append(task)
            elif r[1] == 'Doing':
                Doing['tasks'].append(task)
            elif r[1] == 'Done':
                Done['tasks'].append(task)

        tasks = [ToDo, Doing, Done]
        return tasks
        #raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    @public
    def getFilteredByProyect(project_id):
        raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    @public
    def create(formId=None, data=None, formUUID=None):
        task = TaskWrapper()
        task.set_task_data(**data)
        rv = task.get_task_data()
        return rv

    @staticmethod
    @public
    def edit(formId=None, data=None, formUUID=None):
        #TODO: chequearlo todo!!!!!!!!!!
        if 'asignaciones' != formId:
            raise JSONRPCInvalidRequestError('unexpected formId')

       # form = Form(formId=formId)
        if 'category' in data and data['category'] in ['ToDo', 'Doing', 'Done']:
            category = data['category']
            data['category']
        else:
            category = 'ToDo'

        #rv = form.update_form_data(data['uuid'], data)
        rv = None


        #TODO: Category debe ser la misma en donde está la tarea
        #form.node.holder.connect(holderUser, properties={'category': category})
        return rv


class TaskWrapper(object):

    def __init__(self, *args, **kwargs):
        self.task = None

    def set_task_data(self, **data):

        # Check if category type is send, else set default category to ToDo
        if 'category' in data and data['category'] in ['ToDo', 'Doing', 'Done']:
            category = data['category']
            del data['category']
        else:
            category = 'ToDo'

        # Check if is assigned to someone, else assing to the owner
        if 'ente_asignado' in data:
            holders_params = data['ente_asignado']
            if isinstance(holders_params, list):
                holders = [h for h in holders_params]
            else:
                holders = [holders_params]
            del data['ente_asignado']
        else:
            holders = LoginManager().get_user()

        query = ''
        for holder in holders:
            if query == '':
                query += 'username:' + holder
            else:
                query += 'OR username:' + holder
        holdersUsersNodes = CaliopeUser.index.search(query=query)



        if self.task is None:
            self.task = Task()
            self.task.save()
            self.task.init_entity_data(**data)
            ownerUserNode = CaliopeUser.index.get(username=LoginManager().get_user())
            self.task.set_owner(ownerUserNode)
            for holderUser in holdersUsersNodes:
                self.task.set_holder(holderUser, properties={'category': category})
        else:
            self.task.set_entity_data(**data)
            for holderUser in holdersUsersNodes:
                self.task.set_holder(holderUser, properties={'category': category})


    def get_task_data(self):
        return self.task.get_entity_data()