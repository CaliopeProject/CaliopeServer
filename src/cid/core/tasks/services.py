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
import os
import json
#CaliopeStorage
from cid.core.entities import (VersionedNode, CaliopeUser,
                               CaliopeServices)


#tinyrpc
from tinyrpc.dispatch import public


#SIIM2
from cid.core.login import LoginManager
from models import Task
from cid.utils.helpers import DatetimeEncoder, DatetimeDecoder
from cid.core.pubsub import PubSub

class TaskServices(CaliopeServices):
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
                                             "MATCH (user)-[r:HOLDER]-(t)-["
                                             "TASK]-()"
                                             "WHERE has(r.category) and "
                                             "(r.category='ToDo' or "
                                             "r.category='Doing' or "
                                             "r.category='Done')"
                                             "return distinct (t), "
                                             "r.category");
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
        """
        In order to create a Task, first you need to get the model, in the
        model is incluided de default dform (.json) the layout, the actions
        and the default data.

        In the default data is included the default uuid for the new object
        and cannot be changed otherwise the item will not commit or update
        because is not a valid uuid.

        Also appends as the default holder to the current user under the
        ToDo category.

        :return: the model, actions, layout, data.
        """

        def append_default_holder(uuid):
            user_node = CaliopeUser.index.get(
                username=LoginManager().get_user())
            super(TaskServices, cls) \
                .update_relationship(uuid, "holders", user_node.uuid,
                                     new_properties={"category": "ToDo"})
            return {user_node.uuid: {"category": "ToDo"}}

        template_path = os.path.join(os.path.split(__file__)[0], "templates/" +
                                                                 cls.service_class.__name__ + ".json")
        entity_class = cls.service_class
        rv = super(TaskServices, cls) \
            .get_empty_model(entity_class=entity_class,
                             template_html=template_path)
        rv["data"]["holders"] = append_default_holder(rv["data"]["uuid"][
            "value"])
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

    @classmethod
    @public(name='commit')
    def commit(cls, uuid):
        hkey_name = uuid
        if cls.r.hexists(hkey_name, "formtask"):
            from cid.core.forms.services import FormManager

            form_name = cls.r.hget(hkey_name, "formtask")
            form = FormManager.create_form_from_id(form_name, {})
            cls.update_relationship(uuid, "target", form["uuid"])

        hkey_name_rels = uuid + "_rels"
        holders_to_add = []
        holders_to_remove = []
        if cls.r.hexists(hkey_name_rels, "holders"):
            holders_to_add = [h for h, v in json.loads(cls.r.hget(hkey_name_rels,
                                                       "holders"),
                                         object_hook=DatetimeDecoder.json_date_parser).items()
                          if "__changed__" in v]
            holders_to_remove =[h for h, v in json.loads(cls.r.hget(hkey_name_rels,
                                                       "holders"),
                                         object_hook=DatetimeDecoder.json_date_parser).items()
                          if "__delete__" in v]
        rv = super(TaskServices, cls).commit(uuid)
        for holder in holders_to_add:
            PubSub().publish_command("",
            holder, "createTask", VersionedNode.pull(uuid).serialize())
        for holder in holders_to_remove:
            PubSub().publish_command("",
            holder, "removeTask", VersionedNode.pull(uuid).serialize())
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
