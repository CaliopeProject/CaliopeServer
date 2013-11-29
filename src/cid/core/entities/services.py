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
from tinyrpc.exc import RPCError

from cid.utils.fileUtils import loadJSONFromFile
from cid.utils.helpers import DatetimeEncoder, DatetimeDecoder
from cid.core.pubsub import PubSub

from .utils import CaliopeEntityUtil
from .models import VersionedNode

from cid.core.access_control import AccessControlManager


class CaliopeServices(object):
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
        super(CaliopeServices, self).__init__(*args, **kwargs)

    @classmethod
    @public("getAll")
    def get_all(cls, *args, **kwargs):
        return cls.service_class.category().instance.all()

    @classmethod
    @public("getModel")
    def get_empty_model(cls, entity_class=None, template_html=None, template_layout=None, actions=None):
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
                                                    template_html=template_html,
                                                    template_layout=template_layout,
                                                    actions=actions)
        rv = entity_controller.get_model()
        rv["data"] = entity_controller.get_data()
        cls.set_drafts_uuid(rv['data']['uuid']['value'], entity_class)
        return rv

    @PendingDeprecationWarning
    @classmethod
    @public("getModelAndData")
    def get_model_and_data(cls, uuid, entity_class=None, template_html=None, template_layout=None, actions=None):
        entity_controller = CaliopeEntityController(entity_class=entity_class,
                                                    template_html=template_html,
                                                    template_layout=template_layout,
                                                    actions=actions)
        rv = entity_controller.get_model()
        rv["data"] = entity_controller.get_data()
        cls.subscribe_uuid(uuid)
        return rv

    @classmethod
    def subscribe_uuid(cls, uuid):
        PubSub().subscribe_uuid(uuid)

    @classmethod
    def unsubscribe_uuid(cls, uuid):
        PubSub().unsubscribe_uuid(uuid)

    @classmethod
    def set_drafts_uuid(cls, uuid, entity_class):
        """
        This methods check and creates the HSET in Redis with the key
         cls.draft_hkey  where valid uuids are stored.
        """

        if cls.r.hexists(cls.draft_hkey, uuid):
            raise KeyError("UUID {} already is a draft".format(uuid))
        else:
            cls.r.hset(cls.draft_hkey, uuid, "__draft__")

        if entity_class is None:
            entity_class = VersionedNode
        if not cls.r.hexists(uuid + "_class", "name"):
            cls.r.hset(uuid + "_class", "name", entity_class.__name__)

    @classmethod
    def _set_related(cls, uuid, target_uuid, **kwargs):
        cls.r.hset(uuid + "_related", target_uuid, kwargs)

    @classmethod
    def _get_related(cls, uuid):
        return cls.r.hgetall(uuid + "_related")

    @classmethod
    def _del_related(cls, uuid, target_uuid):
        if cls.r.hexists(uuid + "_related", target_uuid):
            return cls.r.hdel(uuid + "_related", target_uuid)

    @classmethod
    def _is_related(cls, uuid, target_uuid):
        return cls.r.hexists(uuid + "_related", target_uuid)

    @classmethod
    def is_draft_not_commited(cls, uuid):
        if cls.r.hexists(cls.draft_hkey, uuid):
            return True
        return False

    @classmethod
    def _has_draft_props(cls, uuid):
        return cls.r.hlen(uuid) > 0

    @classmethod
    def _has_draft_rels(cls, uuid):
        return cls.r.hlen(uuid + "_rels") > 0

    @classmethod
    def _get_draft_props(cls, uuid):
        return cls.r.hgetall(uuid)

    @classmethod
    def _get_draft_rels(cls, uuid):
        return cls.r.hgetall(uuid + "_rels")


    @classmethod
    def _remove_draft_props(cls, uuid):
        return bool(cls.r.delete(uuid))

    @classmethod
    def _remove_draft_rels(cls, uuid):
        return bool(cls.r.delete(uuid + "_rels"))

    @classmethod
    def _get_draft_class(cls, uuid):
        """
        Return the class of the uuid, even if is not yet saved.
        :param uuid: The UUID of the draft or saved object
        :return: The class of the object with uuid
        """
        hkey = uuid + "_class"
        if cls.r.hexists(hkey, "name"):
            vncls = cls.r.hget(hkey, "name")
            if vncls in VersionedNode\
                .__extended_classes__:
                return VersionedNode.__extended_classes__[vncls]
            return  VersionedNode
        else:
            vncls = VersionedNode.pull(uuid, only_class=True)
            if vncls:
                return vncls
            return VersionedNode

    @classmethod
    @public("updateField")
    def update_field(cls, uuid, field_name, value, subfield_id=None,
                     pos=None, delete=False, metadata=None):
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

        def append_change(uuid, key, value):
            if is_draft(uuid):
                cls.r.hdel(cls.draft_hkey, uuid)
            value = json.loads(json.dumps(value, cls=DatetimeEncoder),
                               object_hook=DatetimeDecoder.json_date_parser)
            if isinstance(value, (dict, list,)):
                return cls.r.hset(uuid, key, json.dumps(value,
                                                        cls=DatetimeEncoder))
            else:
                return cls.r.hset(uuid, key, value)

        def get_in_stage(uuid, field):
            """
            hset returns 1 if is the first time a key, val is set,
            0 if is an update.
            """
            if cls.r.hexists(uuid, field):
                value = cls.r.hget(uuid, field)
                try:
                    return json.loads(value,
                                      object_hook=
                                      DatetimeDecoder.json_date_parser)
                except:
                    return value
            return None

        #: get the current node from database if exists
        versioned_node = cls.service_class.pull(uuid)

        if cls.r.hexists(uuid, field_name):
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
                            if delete:
                                del draft_field[subfield_id][pos]
                            else:
                                draft_field[subfield_id][pos] = value
                        else:
                            raise IndexError("Index does {} not exists in {}"
                            .format(pos, subfield_id))
                    elif isinstance(draft_field[subfield_id], dict) and \
                            isinstance(pos, (unicode, str,)):
                        if delete:
                            del draft_field[subfield_id][pos]
                        else:
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
                                if delete:
                                    del draft_field[subfield_id]
                                else:
                                    draft_field[subfield_id] = value
                            else:
                                raise IndexError("Index {} not exists in {}"
                                .format(subfield_id, field_name))
                        else:
                            raise TypeError("Field {} is not a {}"
                            .format(draft_field, str(list)))
                    elif isinstance(draft_field, dict) and isinstance(
                            subfield_id, (unicode, str,)):
                        if delete:
                            del draft_field[subfield_id]
                        else:
                            draft_field[subfield_id] = value
                    else:
                        raise TypeError("Field {} is not a {}"
                        .format(draft_field, str(dict)))
            else:
                if delete:
                    draft_field = {}
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

        cls._publish_update_field(uuid, field_name, value=value, subfield_id=subfield_id, pos=pos, delete=delete,
                                  metadata=metadata)

        return append_change(uuid, field_name, draft_field) in [0, 1]


    @classmethod
    @public("clearField")
    def clear_field(cls, uuid, field_name, subfield_id=None, pos=None, metadata=None):
        return cls.update_field(uuid, field_name, None,
                                subfield_id=subfield_id,
                                pos=pos, delete=True, metadata=metadata)

    @classmethod
    @public("updateRelationship")
    def update_relationship(cls, uuid, rel_name, target_uuid,
                            new_properties={}, delete=False):
        """
        TODO: Make sure only mark as draft changed rels.
        For updating entity drafts relationships.

        Also pulls the object and refresh the draft with data from the saved
        `py::class VersionedNode`.
        """

        def is_draft(uui):
            if cls.r.hexists(cls.draft_hkey, uuid):
                return True
            return False

        def append_change(uuid, key, value):
            hkey_name = uuid + "_rels"
            if is_draft(uuid):
                cls.r.hdel(cls.draft_hkey, uuid)
            return cls.r.hset(hkey_name, key, json.dumps(value,
                                                         cls=DatetimeEncoder))

        def get_draft_rel_count(uuid, rel_name):
            hkey_name = uuid + "_rels"
            draft_rel = get_in_stage(uuid, rel_name)
            added=0
            removed=0
            if draft_rel:
                added =  len([x for x in draft_rel.values() if '__changed__' in x])
                removed =  len([x for x in draft_rel.values() if '__delete__' in x])
            return added - removed


        def get_in_stage(uuid, key):
            """
            hset returns 1 if is the first time a key, val is set,
            0 if is an update.
            """
            hkey_name = uuid + "_rels"
            if cls.r.hexists(hkey_name, key):
                return json.loads(cls.r.hget(hkey_name, key),
                                  object_hook=DatetimeDecoder.json_date_parser)
            return None

        draft_rel = get_in_stage(uuid, rel_name)

        if draft_rel is None:
            versioned_node = cls.service_class.pull(uuid)
            if versioned_node is not None:
                draft_rel = versioned_node._format_relationships(rel_name)
            else:
                draft_rel = {}
        #: TODO this information can be extracted and put in redis
        rel_def = getattr(cls._get_draft_class(uuid), rel_name)
        if rel_def:
            __cardinality__ = rel_def.manager.description

        if delete:
            #: Mark the relationship to deletion on commit.
            draft_rel[target_uuid]["__delete__"] = True
            #: Remove from related
            cls._del_related(uuid, target_uuid)
            #remove changed mark
            if "__changed__" in draft_rel[target_uuid]:
                del draft_rel[target_uuid]["__changed__"]

        else:
            if 'zero or one' in __cardinality__:
                if get_draft_rel_count(uuid, rel_name) >= 1:
                    for target_other in draft_rel.keys():
                        draft_rel[target_other]['__delete__'] = True
                        cls._del_related(uuid, target_other)
                        #remove changed mark
                        if "__changed__" in draft_rel[target_other]:
                            del draft_rel[target_other]["__changed__"]
                draft_rel[target_uuid] = new_properties
                draft_rel[target_uuid]["__changed__"] = True
                #: add to related
                cls._set_related(uuid, target_uuid)
                #: remove if marked to delete
                if "__delete__" in draft_rel[target_uuid]:
                    del draft_rel[target_uuid]["__delete__"]

            elif 'one or more' in __cardinality__:
                #Check at least one valid
                pass
            elif 'one relationship' == __cardinality__:
                #Check exactly one rel}
                pass
            elif 'zero or more' in __cardinality__:
                draft_rel[target_uuid] = new_properties
                draft_rel[target_uuid]["__changed__"] = True
                #: add to related
                cls._set_related(uuid, target_uuid)
                #: remove if marked to delete
                if "__delete__" in draft_rel[target_uuid]:
                    del draft_rel[target_uuid]["__delete__"]



        return append_change(uuid, rel_name, draft_rel) in [0, 1]

    @classmethod
    @public("deleteRelationship")
    def delete_relationship(cls, uuid, rel_name, target_uuid):
        return cls.update_relationship(uuid, rel_name, target_uuid,
                                       delete=True)


    @classmethod
    @public("commit")
    def commit(cls, uuid, loopback_notification=False):
        """
        Push the changes that are in the draft (Redis) to the neo4j database
        """
        #: TODO: Ensure all updates runs within the same transaction or batch.

        #: check for changes of any kind
        if cls._has_draft_props(uuid) or cls._has_draft_rels(uuid):
            versioned_node = cls.service_class.pull(uuid)
            #: if first time save create a node with given uuid.
            if versioned_node is None:
                node_class = cls._get_draft_class(uuid)
                versioned_node = node_class(uuid=uuid)
                #: apply first the properties changes
            if cls._has_draft_props(uuid):
                changes = cls._get_draft_props(uuid)
                for delta_k, delta_v in changes.items():
                    try:
                        delta_v = json.loads(delta_v,
                                             object_hook=
                                             DatetimeDecoder.json_date_parser)
                    except:
                        delta_v = DatetimeDecoder._parser(delta_v)
                        #: do the changes
                    versioned_node.update_field(delta_k, delta_v)
                    #: clean stage area
                #: push all changes to database
                versioned_node.save()
            cls._remove_draft_props(uuid)
            if cls._has_draft_rels(uuid):
                changes = cls._get_draft_rels(uuid)
                for delta_k, delta_v in changes.items():
                    delta_v = json.loads(delta_v,
                                         object_hook=DatetimeDecoder.json_date_parser)
                    #: do the deletes first.
                    order_list = []
                    for target, props in delta_v.items():
                        if "__delete__" in props and props["__delete__"]:
                            order_list.insert(0, target)
                        elif "__changed__" in props and props["__changed__"]:
                            order_list.append(target)
                    #: do the changes for each target, in order
                    for i in xrange(len(order_list)):
                        target = order_list[i]
                        props = delta_v[target]
                        if "__delete__" in props and props["__delete__"]:
                            versioned_node.delete_relationship(delta_k, target)
                        elif "__changed__" in props and props["__changed__"]:
                            del props["__changed__"]
                            versioned_node.add_or_update_relationship_target(
                                delta_k, target, new_properties=props)
                            #: clean stage area
                cls._remove_draft_rels(uuid)
            return {'uuid': uuid,
                    'value': versioned_node.uuid == uuid}
        else:
            return {'uuid': uuid, 'value': False}


    @classmethod
    @public("getData")
    def get_data(cls, uuid, entity_class=None):
        try:
            PubSub().subscribe_uuid(uuid)
            if entity_class is None:
                entity_class = VersionedNode.pull(uuid, only_class=True)
            vnode = entity_class.pull(uuid)
            if vnode is None:
                #get a vnode with the class and uuid
                vnode = cls._get_vnode_with_data(uuid, entity_class)
                #: Append related uuids to the list.
            for rel_name, rel_repr in vnode._serialize_relationships() \
                .items():
                for target_uuid in rel_repr.keys():
                    direction = getattr(vnode, rel_name).direction
                    cls._set_related(uuid, target_uuid, direction=direction)
            return cls._get_data_with_draft(vnode)
        except AssertionError:
            return RuntimeError("The give uuid {0} is not a valid object of "
                                "class {1}".format(uuid, cls.__name__))

    @classmethod
    @public("discardDraft")
    #@AccessControlManager.check_permission(
    #    action="write", uuid_pos=1)
    def discard_draft(cls, uuid):
        changed_fields = {}
        if cls._has_draft_props(uuid):
            changed_fields = cls._get_draft_props(uuid)
        vnode = VersionedNode.pull(uuid)
        if vnode is None:
            #: TODO what to do with non-saved nodes on discard
            pass
            return {'uuid': uuid, 'value': False}
        else:
            saved_data = vnode.serialize()
            #Notify to go back on saved data.
            for field_name in changed_fields.keys():
                value = saved_data[field_name]["value"] if \
                    field_name in saved_data else None
                cls._publish_update_field(uuid, field_name, value=value)
            rv = (cls._has_draft_props(uuid) and cls
            ._remove_draft_props(
                uuid))
            rv = rv or (cls._has_draft_rels(uuid) and cls._remove_draft_rels(
                uuid))
            return {'uuid': uuid, 'value': rv}

    @classmethod
    def _publish_update_field(cls, uuid, field_name, value, subfield_id=None,
                              pos=None, delete=False, metadata=None, loopback_notification=False):
        rv = {'uuid': uuid, 'field': field_name, 'value': value,
              'subfield_id': subfield_id, 'pos': pos, 'delete': delete, 'metadata': metadata}
        PubSub().publish_command('from_unused', uuid, 'updateField', rv, loopback=loopback_notification)


    @classmethod
    def _get_data_with_draft(cls, vnode):
        #: This method does nothing to the node it self, it just rewrites the
        #: value to be returned.
        rv = vnode.serialize()
        if cls._has_draft_props(vnode.uuid):
            for prop, value in cls._get_draft_props(vnode.uuid).items():
                rv[prop] = value
        if cls._has_draft_rels(vnode.uuid):
            for rel_name, rel_value in cls._get_draft_rels(vnode.uuid).items():
                rv[rel_name] = json.loads(rel_value,
                                          object_hook=
                                          DatetimeDecoder.json_date_parser)
        return rv


    @classmethod
    def _get_vnode_with_data(cls, uuid, entity_class):
        vnode = entity_class()
        vnode.uuid = uuid
        return vnode


    @classmethod
    @public("getDataByIndexKeyValue")
    def get_data_key_value(cls, key, value):
        try:
            param = {key: value}
            return [vnode.serialize() for vnode in VersionedNode.index \
                .search(**param)]
        except Exception as e:
            return RuntimeError(e)


class CaliopeEntityController(object):
    """
    For handing operations on the nodes, this controller with be able to do
    operations with the data.

    Also will provide the json models from templates.
    """

    def __init__(self, uuid=None, entity_class=None, template_html=None, template_layout=None, actions=None):
        """

        :param entity_class:
        :param template_html:
        :return:
        """
        self.template = None
        self.entity_class = entity_class
        self.entity = self.entity_class.pull(uuid) if uuid is not None else \
            self.entity_class()
        self.template_html = template_html
        self.template_layout = template_layout
        self.actions = actions

    def get_data(self):
        if self.entity is None:
            self.entity = self.entity_class()
        return self.entity.serialize()

    def get_model(self):
        rv = dict()
        rv['form'] = self.get_form()
        rv['actions'] = self.get_actions()
        rv['layout'] = self.get_layout()
        return rv

    def get_form(self):
        try:
            if self.template_html is not None:
                self.template = loadJSONFromFile(self.template_html)
            else:
                self.template = CaliopeEntityUtil() \
                    .makeFormTemplate(self.entity_class)
            return self.template
        except:
            return list()

    def get_actions(self):
        #: TODO: Implement depending on user
        if self.actions is not None:
            return self.actions
        elif self.template and 'actions' in self.template:
            self.actions = self.template['actions']
            self.template.pop('actions')
        else:
            self.actions = [{"name": "Guardar", "method":
                self.entity_class.__name__ + ".commit"}]
        return self.actions

    def get_layout(self):
        #: TODO: Implement depending on user
        try:
            if self.template_layout is not None:
                self.layout = loadJSONFromFile(self.template_layout)['layout']
            elif 'layout' in self.template: #for all in one template compatibility workaround
                self.layout = self.template['layout']
                self.template.pop('layout')
            else:
                self.layout = CaliopeEntityUtil() \
                    .makeLayoutTemplate(self.entity_class)
            return self.layout
        except:
            return list()



