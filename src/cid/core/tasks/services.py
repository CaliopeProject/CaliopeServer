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
from cid.core.entities import (CaliopeNode, CaliopeUser, CaliopeEntityController,
                               CaliopeEntityService)

from cid.utils.fileUtils import loadJSONFromFile

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError, RPCError
from tinyrpc.dispatch import public

#Flask
from flask import current_app

#SIIM2
from cid.core.login import LoginManager
from cid.core.forms.services import FormManager
from models import Task


class TaskServices(CaliopeEntityService):

    def __init__(self, *args, **kwargs):
        super(TaskServices, self).__init__(*args, **kwargs)

    #: TODO: Valida users and return based on context
    @staticmethod
    @public(name='getAll')
    def get_all():
        a_node = CaliopeUser.category().instance.single()
        results, metadata = a_node.cypher("START user=node(*)"
                                          "MATCH (user)-[r:HOLDER]-(tdc)-[e:CURRENT]-(t)"
                                          "WHERE has(r.category) "
                                          "return t, r.category")
        task_list = []
        for row in results:
            task_class = Task().__class__
            task = task_class.inflate(row[0])
            entity_data = task.serialize()
            task_list.append(entity_data)
        return task_list

    @staticmethod
    @public(name='getCurrentUserKanban')
    def get_current_user_kanban():

        user_node = CaliopeUser.index.get(username=LoginManager().get_user())
        #: Starting from current user, match all nodes which are connected througth a HOLDER
        #: relationship and that node is connected with a  CURRENT relationship to a task.
        #: From the task find the FIRST node
        results, metadata = user_node.cypher("START user=node({self})"
                                             "MATCH (user)-[r:HOLDER]-(tdc)-[e:CURRENT]-(t)"
                                             "WHERE has(r.category) and "
                                             "(r.category='ToDo' or "
                                             "r.category='Doing' or "
                                             "r.category='Done')"
                                             "return t, r.category");
        tasks_list = {'ToDo': {'pos': 0, 'category': {'value': 'ToDo'}, 'tasks': []},
                      'Doing': {'pos': 1, 'category': {'value': 'Doing'}, 'tasks': []},
                      'Done': {'pos': 2, 'category': {'value': 'Done'}, 'tasks': []}}

        for row in results:
            tl = tasks_list[row[1]]['tasks']
            task_class = Task().__class__
            task = task_class.inflate(row[0])
            entity_data = task.serialize()
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
        TaskServices.service_requested_uuid.add(rv['data']['uuid']['value'])
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
    def create(formId=None, data=None):
        if 'uuid' in data:
            task_controller = TaskController(uuid=data['uuid'])
        else:
            task_controller = TaskController()

        for target in data['target']['target']:
            if 'entity' in target:
                form = target['entity']
                res = FormManager.create_form_from_id(form, None)
                if res:
                    target['entity_data'] = res

        task_controller.set_data(**data)
        task_controller.set_owner()
        rv = task_controller.get_data()

        return rv

    @staticmethod
    @public
    def edit(formId=None, data=None):
        task_controller = TaskController(**data)
        task_controller.set_data(**data)
        rv = task_controller.get_data()
        return rv

    @staticmethod
    @public
    def archive(formId=None, data=None):
        task_controller = TaskController(**data)
        task_controller.archive()
        return {'result': True}

    @staticmethod
    @public
    def delete(formId=None, data=None):
        task_controller = TaskController(**data)
        task_controller.delete()
        return {'result': True}


    @staticmethod
    @public(name='getDeletedByCurrentUser')
    def get_deleted_by_current_user():
        rv = TaskServices.get_by_category_and_by_current_user(category="deleted")
        return rv

    @staticmethod
    @public(name='getArchivedByCurrentUser')
    def get_archived_by_current_user(project_id):
        rv = TaskServices.get_by_category_and_by_current_user(category="archived")
        return rv


    @staticmethod
    def get_by_category_and_by_current_user(category):
        user_node = CaliopeUser.index.get(username=LoginManager().get_user())
        #: Starting from current user, match all nodes which are connected througth a HOLDER
        #: relationship and that node is connected with a  CURRENT relationship to a task.
        #: From the task find the FIRST node
        results, metadata = user_node.cypher("START user=node({self})"
                                             "MATCH (user)-[r:HOLDER]-(tdc)-[e:CURRENT]-(t), (t)-[:FIRST]-(tdf)"
                                             "WHERE has(r.category) and "
                                             "(r.category='" + category + "')"
                                                                          "      and not(tdf=tdc)"
                                                                          "return t, r.category");
        tasks_list = {category: {'pos': 0, 'category': {'value': category}, 'tasks': []}}

        for row in results:
            tl = tasks_list[row[1]]['tasks']
            task_class = Task().__class__
            task = task_class.inflate(row[0])
            entity_data = task.get_entity_data()
            tl.append(entity_data)

        return tasks_list


class TaskController(CaliopeEntityController):
    def __init__(self, *args, **kwargs):
        super(TaskController, self).__init__(*args, **kwargs)
        if 'uuid' in kwargs:
            try:
                node = CaliopeNode.index.get(uuid=kwargs['uuid'])
                self.task = Task().__class__.inflate(node.__node__)
            except DoesNotExist:
                if kwargs['uuid'] in TaskServices.service_requested_uuid:
                    TaskServices.service_requested_uuid.remove(kwargs['uuid'])
                    self.task = Task()
                else:
                    raise DoesNotExist("Invalid UUID")
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
        rels = list()
        if 'holders' in data and 'target' in data['holders'] and len(data['holders']['target']) > 0:
            holders = data['holders']
        else:
            holders = [CaliopeUser.index.get(username=LoginManager().get_user())]

        for rel in Task.__entity_data_type__._get_class_relationships():
            if rel[0] in data:
                rels.append(data[rel[0]])
                del data[rel[0]]

        # Check if category type is send, else set default category to ToDo
        if 'category' in data and data['category'] in ['ToDo', 'Doing', 'Done']:
            category = data['category']
            del data['category']
        else:
            category = 'ToDo'

        if self.task is None:
            self.task = Task()
        else:
            self.task.set_entity_data(**data)
            if isinstance(holders, list):
                self.set_holders(holders, category)
            elif isinstance(holders, dict):
                for target in holders['target']:
                    # target_class = target['entity'].strip...
                    target_class = CaliopeUser
                    target_node = target_class.index.get(**{k: v for k, v in target['entity_data'].items()})
                    self.set_holder(target_node, **target['properties'])


    def get_data(self):
        return self.task.serialize()

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
        self.task.remove_holders()
        for holderUser in holdersUsersNodes:
            self.task.set_holder(holderUser, properties={'category': category})

    def set_owner(self):
        owner = CaliopeUser.index.get(username=LoginManager().get_user())
        self.task.set_owner(owner)

    def set_holder(self, holder_node, category):
        self.task.set_holder(holder_node, properties={'category': category})

    def archive(self):
        holder_user = CaliopeUser.index.get(username=LoginManager().get_user())
        self.set_holder(holder_user, 'archived')


    def delete(self):
        holder_user = CaliopeUser.index.get(username=LoginManager().get_user())
        self.set_holder(holder_user, 'deleted')


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

