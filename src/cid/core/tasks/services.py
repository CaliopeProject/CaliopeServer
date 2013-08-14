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
from neomodel.exception import DoesNotExist

#CaliopeStorage
from cid.core.models import CaliopeUser

from cid.core.entities.services import CaliopeEntityController, CaliopeEntityService


#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

#Flask
from cid.core.login import LoginManager
#temporal
from cid.core.forms import FormManager
from models import Task


class TaskServices(object):

    @staticmethod
    @public
    def getAll():

        user_node = CaliopeUser.index.get(username=LoginManager().get_user())
        results, metadata = user_node.cypher("START user=node({self})"
                                             "MATCH (user)-[r:HOLDER]-(td)-[e:CURRENT]-(t)"
                                             "WHERE has(r.category)"
                                             "return t, r.category");
        tasks_list = {'ToDo': {'pos': 0, 'category': 'ToDo', 'tasks': []},
                      'Doing': {'pos': 1, 'category': 'Doing', 'tasks': []},
                      'Done': {'pos':2, 'category': 'Done', 'tasks': []}}

        for row in results:
            tl = tasks_list[row[1]]['tasks']
            tl.append(Task().__class__.inflate(row[0]).get_entity_data())

        return [list for list in sorted(tasks_list.values(), key=lambda pos: pos['pos'])]

    @staticmethod
    @public
    def getTemplate():
        pass

    @staticmethod
    @public(name='getModel')
    def get_model():
        rv = FormManager.get_form_template('asignaciones')
        rv['data'] = TaskController().get_data()
        return rv


    @staticmethod
    @public
    def getFilteredByProject(project_id):
        raise JSONRPCInvalidRequestError('Unimplemented')

    @staticmethod
    @public
    def create(formId=None, data=None, formUUID=None):
        if 'uuid' in data:
            task = TaskController(uuid=data['uuid'])
        else:
            task = TaskController()
        task.set_data(**data)
        rv = task.get_data()
        return rv

    @staticmethod
    @public
    def edit(formId=None, data=None, formUUID=None):
        task_controller = TaskController(uuid=formUUID)
        task_controller.set_data(**data)
        rv = task_controller.get_data()
        return rv

    @staticmethod
    @public
    def add_subtasks():
        pass


    @staticmethod
    @public
    def set_category(uuid=None, data=None):
        task_controller = TaskController(uuid=uuid)
        task_controller.set_data(**data)
        rv = task_controller.get_data()
        return rv


class TaskController(CaliopeEntityController):

    def __init__(self, *args, **kwargs):
        if 'uuid' in kwargs:
            try:
                self.task = Task.index.get(uuid=kwargs['uuid'])
            except DoesNotExist as e:
                self.task = None
            except Exception as e:
                raise e
        else:
            #: TODO check initialization
            self.task = None
            self.set_data(**{})

    @staticmethod
    def get_model():
        pass

    def set_data(self, **data):
        # Check if category type is send, else set default category to ToDo
        if 'category' in data and data['category'] in ['ToDo', 'Doing', 'Done']:
            category = data['category']
            del data['category']
        else:
            category = 'ToDo'
        if 'ente_asignado' in data:
            holders = data['ente_asignado']
            del data['ente_asignado']
        else:
            holders = LoginManager().get_user()

        if self.task is None:
            self.task = Task()
            self.task.save()
            self.task.init_entity_data(**data)
            ownerUserNode = CaliopeUser.index.get(username=LoginManager().get_user())
            self.task.set_owner(ownerUserNode)
        else:
            self.task.set_entity_data(**data)
        self.set_holders(holders, category)

    def get_data(self):
        return self.task.get_entity_data()

    def set_holders(self, holders, category):

        if isinstance(holders, list):
            holders = [h for h in holders]
        else:
            holders = [holders]

        query = ''
        for holder in holders:
            if query == '':
                query += 'username:' + holder
            else:
                query += ' OR username:' + holder
        holdersUsersNodes = CaliopeUser.index.search(query=query)
        for holderUser in holdersUsersNodes:
            self.task.set_holder(holderUser, properties={'category': category})

    def set_category(self, category):
        pass

