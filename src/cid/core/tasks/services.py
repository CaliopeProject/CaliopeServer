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
from cid.core.models import CaliopeUser, CaliopeNode

from cid.core.entities.services import CaliopeEntityController, CaliopeEntityService
from cid.utils.fileUtils import loadJSONFromFile


#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError, RPCError
from tinyrpc.dispatch import public

#Flask
from flask import current_app

#SIIM2
from cid.core.login import LoginManager

from models import Task


class TaskServices(CaliopeEntityService):
    def __init__(self, *args, **kwargs):
        super(TaskServices, self).__init__(*args, **kwargs)

    @staticmethod
    @public(name='getAll')
    def get_all():

        user_node = CaliopeUser.index.get(username=LoginManager().get_user())
        #: Starting from current user, match all nodes which are connected througth a HOLDER
        #: relationship and that node is connected with a  CURRENT relationship to a task.
        #: From the task find the FIRST node
        results, metadata = user_node.cypher("START user=node({self})"
                                             "MATCH (user)-[r:HOLDER]-(tdc)-[e:CURRENT]-(t), (t)-[:FIRST]-(tdf)"
                                             "WHERE has(r.category) and not(tdf=tdc)"
                                             "return t, r.category");
        tasks_list = {'ToDo': {'pos': 0, 'category': {'value': 'ToDo'}, 'tasks': []},
                      'Doing': {'pos': 1, 'category': {'value': 'Doing'}, 'tasks': []},
                      'Done': {'pos': 2, 'category': {'value': 'Done'}, 'tasks': []}}

        for row in results:
            tl = tasks_list[row[1]]['tasks']
            task_class = Task().__class__
            task = task_class.inflate(row[0])
            entity_data = task.get_entity_data()
            tl.append(entity_data)

        return [list for list in sorted(tasks_list.values(), key=lambda pos: pos['pos'])]


    @staticmethod
    @public(name='getData')
    def get_data(uuid):
        data = {}
        data['uuid'] = uuid
        task_controller = TaskController(**data)
        return task_controller.get_data()


    @staticmethod
    @public(name='getModel')
    def get_model():
        task_controller = TaskController()
        rv = task_controller.get_model()
        rv['data'] = task_controller.get_data()
        return rv

    @staticmethod
    @public(name='getModelAndData')
    def get_model_and_data(uuid):
        data = {}
        data['uuid'] = uuid
        task_controller = TaskController(**data)
        rv = task_controller.get_model()
        rv['data'] = task_controller.get_data()
        return rv

    @staticmethod
    @public
    def create(data=None):
        if 'uuid' in data:
            task = TaskController(uuid=data['uuid'])
        else:
            task = TaskController()
        task.set_data(**data)
        rv = task.get_data()
        return rv

    @staticmethod
    @public
    def edit(data=None):
        task_controller = TaskController(**data)
        task_controller.set_data(**data)
        rv = task_controller.get_data()
        return rv

    @staticmethod
    @public
    def getFilteredByProject(project_id):
        raise JSONRPCInvalidRequestError('Unimplemented')


class TaskController(CaliopeEntityController):
    def __init__(self, *args, **kwargs):
        super(TaskController, self).__init__(*args, **kwargs)
        if 'uuid' in kwargs:
            try:
                node = CaliopeNode.index.get(uuid=kwargs['uuid'])
                self.task = Task().__class__.inflate(node.__node__)
            except DoesNotExist as e:
                self.task = None
            except Exception as e:
                raise e
        else:
            #: TODO check initialization
            self.task = None
            self.set_data(**{})

    def get_model(self):
        if self._check_template():
            rv = dict()
            rv['form'] = self._get_form()
            rv['actions'] = self._get_actions()
            rv['layout'] = self._get_layout()
            return rv
        else:
            raise RPCError('Template error')

    def set_data(self, **data):
        # Check if category type is send, else set default category to ToDo
        if 'category' in data and data['category'] in ['ToDo', 'Doing', 'Done']:
            category = data['category']
            del data['category']
        else:
            category = 'ToDo'
        holders = []
        if 'ente_asignado' in data:
            if len(data['ente_asignado']) > 0 :
                holders = data['ente_asignado']
            holders = LoginManager().get_user()
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

    def _check_template(self):
        #: TODO: Check if form_name is valid and form_path is a file
        #: TODO: Cache this files
        try:
            self.template = loadJSONFromFile('core/tasks/templates/tasks.json', current_app.root_path)
            return True
        except IOError:
            return False

    def _get_form(self):
        return self.template

    def _get_actions(self):
        #: TODO: Implement depending on user
        if 'actions' in self.template:
            self.actions = self.template['actions']
            self.template.pop('actions')
        return self.actions

    def _get_layout(self):
        #: TODO: Implement depending on user
        if 'layout' in self.template:
            self.layout = self.template['layout']
            self.template.pop('layout')
        else:
            self.layout = []
        return self.layout

