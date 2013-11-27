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
    @classmethod
    @public(name='getAll')
    def get_all(cls):
        raise NotImplementedError

    @classmethod
    @public(name='getCurrentUserKanban')
    def get_current_user_kanban(cls, category=None, context=None):

        user_node = CaliopeUser.index.get(username=LoginManager().get_user())

        #: Starting from current user, match all nodes which are connected througth a HOLDER
        #: relationship and that node is connected with a  CURRENT relationship to a task.
        #: From the task find the FIRST node
        if context:
            node_context = VersionedNode.pull(context).__node__.id
        else:
            node_context = '*'

        if category is None:
            results, metadata = user_node.cypher("""
            START user=node({{self}}), context_node=node({context})
            MATCH (user)-[r:HOLDER]-(t)-[TASK]-(), (t)-[:__CONTEXT__]-(context)
            WHERE has(r.category) and (r.category='ToDo' or
                                        r.category='Doing' or
                                        r.category='Done') and
                   id(context_node)=id(context)
            RETURN distinct t, r.category
             """.format(context=node_context))
        else:
            results, metadata = user_node.cypher("""
            START user=node({{self}}), context_arg=node({context})
            MATCH (user)-[r:HOLDER]-(t)-[TASK]-(), (t)-[:__CONTEXT__]-(context)
            WHERE has(r.category) and (r.category='{category}')
            RETURN distinct t, r.category
             """.format(category=category, context=node_context))

        tasks_list = {
            'ToDo': {'pos': 0, 'category': {'value': 'ToDo'}, 'tasks': []},
            'Doing': {'pos': 1, 'category': {'value': 'Doing'}, 'tasks': []},
            'Done': {'pos': 2, 'category': {'value': 'Done'}, 'tasks': []}}

        for row in results:
            tl = tasks_list[row[1]]['tasks']
            task = cls.get_data(row[0]._properties['uuid'])
            tl.append(task)

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

        template_path = os.path.join(
            os.path.split(__file__)[0], "templates/" +
                                        cls.service_class.__name__ + ".json")
        entity_class = cls.service_class
        rv = super(TaskServices, cls) \
            .get_empty_model(entity_class=entity_class,
                             template_html=template_path)
        rv["data"]["holders"] = append_default_holder(rv["data"]["uuid"][
            "value"])
        return rv

    @classmethod
    @public(name='getData')
    def get_data(cls, uuid):
        import os

        template_path = os.path.join(
            os.path.split(__file__)[0], "templates/" +
                                        cls.service_class.__name__ + ".json")
        entity_class = cls.service_class
        rv = super(TaskServices, cls) \
            .get_data(uuid=uuid, entity_class=entity_class)
        return rv

    @classmethod
    @public(name='commit')
    def commit(cls, uuid, loopback_notification=False):
        hkey_name = uuid
        #Create form if is associated to a form
        if cls.r.hexists(hkey_name, "formtask"):
            from cid.core.forms.services import FormManager

            form_name = cls.r.hget(hkey_name, "formtask")
            form = FormManager.create_form_from_id(form_name, {})
            cls.update_relationship(uuid, "target", form["uuid"])

        #set the default context to user if no context defined.
        if not 'contexts' in cls._get_draft_rels(uuid):
            #: TODO: Add change the method for getting current user uuid
            cls.update_relationship(uuid, 'contexts',
                                    CaliopeUser.index.get(
                                        username=LoginManager().get_user())
                                    .uuid)

        #notify the other users of the change
        hkey_name_rels = uuid + "_rels"
        holders_to_add = []
        holders_to_remove = []
        if cls.r.hexists(hkey_name_rels, "holders"):
            holders_to_add = [h for h, v in
                              json.loads(cls.r.hget(hkey_name_rels, "holders"),
                                         object_hook=DatetimeDecoder
                                         .json_date_parser).items()
                              if "__changed__" in v]
            holders_to_remove = [h for h, v in
                                 json.loads(cls.r.hget(hkey_name_rels, "holders"),
                                            object_hook=DatetimeDecoder
                                            .json_date_parser).items()
                                 if "__delete__" in v]
        rv = super(TaskServices, cls).commit(uuid)
        for holder in holders_to_add:
            PubSub().publish_command("",
                                     holder, "createTask", VersionedNode.pull(uuid).serialize(),
                                     loopback=loopback_notification)
            PubSub().subscribe_uuid_with_user_uuid(holder, uuid)

        for holder in holders_to_remove:
            PubSub().publish_command("",
                                     holder, "removeTask", VersionedNode.pull(uuid).serialize(),
                                     loopback=loopback_notification)
        return rv

    @classmethod
    @public(name="getCurrentUserContexts")
    def get_current_user_contexts(cls):
        user = CaliopeUser.index.get(username=LoginManager().get_user())
        return [{'uuid': {'value': user.uuid}, 'caption': {'value':
                                                               'Personal'}}]

    @classmethod
    @public(name='getDeletedByCurrentUser')
    def get_deleted_by_current_user(cls):
        rv = cls.get_current_user_kanban(category="deleted")
        return rv

    @classmethod
    @public(name='getArchivedByCurrentUser')
    def get_archived_by_current_user(cls):
        rv = cls.get_current_user_kanban(category="archived")
        return rv

