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
from exceptions import ValueError

from tinyrpc.dispatch import public
from redis import Redis
import json

from cid.utils.fileUtils import loadJSONFromFile
from cid.utils.helpers import DatetimeEncoder, DatetimeDecoder

from .utils import CaliopeEntityUtil
from .models import VersionedNode

class CaliopeEntityService(object):
    """

    This class is the base for all future forms elements.
    """
    def __new__(cls, *args, **kwargs):
        cls.r = Redis()
        cls.service_class = kwargs["service_class"] if "service_class" in \
                             kwargs else VersionedNode
        cls.draft_hkey = cls.service_class.__name__ + "_drafts"

        return cls

    def __init__(self, *args, **kwargs):

        super(CaliopeEntityService, self).__init__(*args, **kwargs)


    @classmethod
    @public("getAll")
    def get_all(cls, *args, **kwargs):
        return cls.service_class.category().instance.all()

    @classmethod
    @public("getModel")
    def get_empty_model(cls, entity_class=None, template_path=None):
        """
        This method needs to be override if you want to use configured json
        forms.

        This methods creates an empty `py::class CaliopeEntityController` and
        returns the model and empty data. The model is returned based on the
        template, or creates a default template if `py::cons None`.

        At the ends, append generated draft uuid to Redis

        :param
        """
        entity_controller = CaliopeEntityController(entity_class=entity_class,
                                                    template_path=template_path)
        rv = entity_controller.get_model()
        rv["data"] = entity_controller.get_data()
        cls.set_drafts_uuid(rv['data']['uuid']['value'])
        return rv

    @classmethod
    @public("getModelAndData")
    def get_model_and_data(cls, uuid, entity_class=None, template_path=None):
        entity_controller = CaliopeEntityController(uuid=uuid,
                                                    entity_class=entity_class,
                                                    template_path=template_path)
        rv = entity_controller.get_model()
        rv["data"] = entity_controller.get_data()
        return rv


    @classmethod
    def set_drafts_uuid(cls, uuid):
        """
        This methods check and creates the HSET in Redis with the key
         cls.draft_hkey  where valid uuids are stored.
        """

        if cls.r.hexists(cls.draft_hkey, uuid):
            raise KeyError("UUID {} already is a draft".format(uuid))
        else:
            cls.r.hset(cls.draft_hkey, uuid, "__draft__")


    @classmethod
    @public("updateField")
    def update_field(cls, uuid, field_name, value, subfield_id=None, pos=None):
        """
        For updating entity drafts.

        This methods first checks for valid drafts in the Redis drafts for the
        class in cls.service_class, then creates a new redis.hset with the uuid
        and append the changes, if any, and marks the draft as stagged.

        Also pulls the object and refresh the draft with data from the saved
        `py::class VersionedNode`.


        """
        def is_draft(uui):
             if cls.r.hexists(cls.draft_hkey, uuid):
                 return True
             return False
        def stage(uuid):
            if not cls.r.hexists(uuid, "__stagged__"):
                cls.r.hset(uuid, "__stagged__", json.dumps(True,
                                                    cls=DatetimeEncoder))
        def mark_edit(uuid):
            if is_draft(uuid):
                cls.r.hdel(cls.draft_hkey, uuid)
            if cls.r.hlen(uuid) == 0:
                stage(uuid)
                return True
            return False

        def append_change(uuid, key, value):
            mark_edit(uuid)
            return cls.r.hset(uuid, key, json.dumps(value,
                                                    cls=DatetimeEncoder))
        def get_in_stage(uuid, field):
            """
            hset returns 1 if is the first time a key, val is set,
            0 if is an update.
            """
            if cls.r.hexists(uuid, field):
                return json.loads(cls.r.hget(uuid, field),
                                  object_hook=DatetimeDecoder.json_date_parser)
            return None

        #: get the current node from database if exists
        versioned_node = cls.service_class.pull(uuid)

        if cls.r.hexists(uuid,field_name):
            draft_field = get_in_stage(uuid, field_name)
        elif versioned_node is not None:
            draft_field = getattr(versioned_node, field_name)
        else:
            draft_field = None

        if draft_field is not None:
            if subfield_id is not None:
                if pos is not None:
                    if isinstance(draft_field[subfield_id], list) and \
                       isinstance(pos, int):
                        if pos == -1:
                            draft_field[subfield_id].append(value)
                        elif len(draft_field[subfield_id]) > pos:
                            draft_field[subfield_id][pos] = value
                        else:
                            raise IndexError("Index does {} not exists in {}"
                                             .format(pos, subfield_id))
                    elif isinstance(draft_field[subfield_id], dict) and \
                         isinstance(pos, (unicode, str,)):
                         draft_field[subfield_id][pos] = value
                    else:
                        raise KeyError("Field {} does not exists in {}"
                                       .format(subfield_id, field_name))
                else:
                    if isinstance(subfield_id, int):
                        if isinstance(draft_field, list):
                            if subfield_id == -1:
                                draft_field.append(value)
                            elif len(draft_field) > subfield_id:
                                draft_field[subfield_id] = value
                            else:
                                raise IndexError("Index {} not exists in {}"
                                             .format(subfield_id, field_name))
                        else:
                            raise TypeError("Field {} is not a {}"
                                       .format(draft_field, str(list)))
                    elif isinstance(draft_field, dict) and isinstance(
                        subfield_id, (unicode, str,)):
                        draft_field[subfield_id] = value
                    else:
                        raise TypeError("Field {} is not a {}"
                                       .format(draft_field, str(dict)))
            else:
                draft_field = value
        else:
            field = None
            subfield = None
            if pos is not None:
                if isinstance(pos, int):
                    if pos == -1:
                        subfield = [value]
                    else:
                        raise IndexError("Index does {} not exists in {}"
                                             .format(pos, subfield_id))
                elif isinstance(pos, (unicode, str)):
                    subfield = {pos: value}
                if subfield_id is not None:
                    if isinstance(subfield_id, int):
                        if subfield_id == -1:
                            field = [subfield]
                        else:
                            raise IndexError("Index {} not exists in {}"
                                             .format(subfield_id, field_name))
                    elif isinstance(subfield_id, (unicode, str,)):
                        field = {subfield_id: subfield}
                draft_field = field
            elif subfield_id is not None:
                if isinstance(subfield_id, int):
                    if subfield_id == -1:
                            field = [value]
                    else:
                        raise IndexError("Index {} not exists in {}"
                                             .format(subfield_id, field_name))
                elif isinstance(subfield_id, (unicode, str,)):
                    field = {subfield_id: value}
                draft_field = field
            else:
                draft_field = value

        return append_change(uuid, field_name, draft_field) in [0, 1]

    @classmethod
    @public("commit")
    def commit(cls, uuid):
        """
        Push the changes that are in the draft (Redis) to the neo4j database
        """
        def is_stagged(uuid):
            return cls.r.hexists(uuid,"__stagged__")

        def get_changes(uuid):
            return cls.r.hgetall(uuid)

        def remove_draft(uuid):
            cls.r.delete(uuid)


        if is_stagged(uuid):
            changes = get_changes(uuid)
            del changes["__stagged__"]
            for delta_k, delta_v in changes.items():
                delta_v = json.loads(delta_v,
                                object_hook=DatetimeDecoder.json_date_parser)
                versioned_node = cls.service_class.pull(uuid)
                if versioned_node is None:
                    versioned_node = cls.service_class(uuid=uuid)
                versioned_node.update_field(delta_k, delta_v)
                remove_draft(uuid)
                return versioned_node.uuid == uuid





    @classmethod
    @public("getData")
    def get_data(cls, uuid):
        try:
            return cls.pull(uuid).serialize()
        except AssertionError:
            return RuntimeError("The give uuid {0} is not a valid object of "
                                "class {1}".format(uuid, cls.__name__))



    @staticmethod
    @public("edit")
    def edit(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @public("create")
    def create(*args, **kwargs):
        raise NotImplementedError

class CaliopeEntityController(object):
    """
    For handing operations on the nodes, this controller with be able to do
    operations with the data.

    Also will provide the json models from templates.
    """

    def __init__(self, uuid=None, entity_class=None, template_path=None):
        """

        :param entity_class:
        :param template_path:
        :return:
        """
        self.entity_class = entity_class
        self.entity = self.entity_class.pull(uuid) if uuid is not None else \
            self.entity_class()
        self.template_path= template_path

    def get_data(self):
        if self.entity is None:
            self.entity = self.entity_class()
        return self.entity.serialize()

    def get_model(self):
        if self.check_template():
            rv = dict()
            rv['form'] = self.get_form()
            rv['actions'] = self.get_actions()
            rv['layout'] = self.get_layout()
            return rv
        else:
            raise ValueError('Template error')

    def check_template(self):
        try:
            if self.template_path is not None:
                self.template = loadJSONFromFile(self.template_path)
        except IOError:
            self.template = CaliopeEntityUtil()\
                                .makeFormTemplate(self.entity_class)
        finally:
            return True


    def get_form(self):
        return self.template

    def get_actions(self):
        #: TODO: Implement depending on user
        if 'actions' in self.template:
            self.actions = self.template['actions']
            self.template.pop('actions')
        else:
            self.actions = [{"name": "Guardar", "method":
                            self.entity_class.__name__ + ".commit"}]
        return self.actions

    def get_layout(self):
        #: TODO: Implement depending on user
        if 'layout' in self.template:
            self.layout = self.template['layout']
            self.template.pop('layout')
        else:
            self.layout = []
        return self.layout




