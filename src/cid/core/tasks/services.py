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
                                          "return distinct t")
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
        tasks_list = {
            'ToDo': {'pos': 0, 'category': {'value': 'ToDo'}, 'tasks': []},
            'Doing': {'pos': 1, 'category': {'value': 'Doing'}, 'tasks': []},
            'Done': {'pos': 2, 'category': {'value': 'Done'}, 'tasks': []}}

        for row in results:
            tl = tasks_list[row[1]]['tasks']
            task_class = Task().__class__
            task = task_class.inflate(row[0])
            entity_data = task.serialize()
            tl.append(entity_data)

        return [list for list in
                sorted(tasks_list.values(), key=lambda pos: pos['pos'])]

    @classmethod
    @public("getModel")
    def get_empty_model(cls):
        import os
        template_path = os.path.join(os.path.split(__file__)[0],"templates/" +
                        cls.service_class.__name__ + ".json")
        entity_class = cls.service_class
        rv = super(TaskServices, cls)\
            .get_empty_model(entity_class=entity_class,
                             template_path=template_path)
        return rv

    @classmethod
    @public(name='getModelAndData')
    def get_model_and_data(cls, uuid):
        import os

        template_path = os.path.join(os.path.split(__file__)[0], "templates/" +
                                                                 cls.service_class.__name__ + ".json")
        entity_class = cls.service_class
        rv = super(TaskServices, cls) \
            .get_model_and_data(uuid=uuid, entity_class=entity_class,
                                template_path=template_path)
        return rv

    @staticmethod
    @public(name='getDeletedByCurrentUser')
    def get_deleted_by_current_user():
        rv = TaskServices.get_by_category_and_by_current_user(
            category="deleted")
        return rv

    @staticmethod
    @public(name='getArchivedByCurrentUser')
    def get_archived_by_current_user(project_id):
        rv = TaskServices.get_by_category_and_by_current_user(
            category="archived")
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
        tasks_list = {
            category: {'pos': 0, 'category': {'value': category}, 'tasks': []}}

        for row in results:
            tl = tasks_list[row[1]]['tasks']
            task_class = Task().__class__
            task = task_class.inflate(row[0])
            entity_data = task.get_entity_data()
            tl.append(entity_data)

        return tasks_list
