# -*- coding: utf-8 -*-
"""
    .. codeauthor:: Sebastián Ortiz <neoecos@gmail.com>
    .. codeauthor:: Nelson Castillo <nelsoneci@gmail.com>
    .. copyright:: (c) 2013 por Fundación CorreLibre
    .. license::  GNU AFFERO GENERAL PUBLIC LICENSE

#SIIM2 Storage is the base of SIIM2's Framework
#Copyright (C) 2013  Fundación Correlibre
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re

from py2neo import neo4j
from neomodel import (StringProperty,
                      DateTimeProperty,
                      AliasProperty,
                      IntegerProperty,
                      FloatProperty,
                      ZeroOrMore,
                      ZeroOrOne,
                      One,
                      DoesNotExist,
                      RelationshipDefinition,
                      RelationshipManager,
                      RelationshipFrom,
                      RelationshipTo,
                      CustomBatch,
                      connection)

from neomodel.contrib import SemiStructuredNode

from cid.core.utils import uuidGenerator, timeStampGenerator, DictDiffer

from caliope_properties import CaliopeJSONProperty


camel_to_upper = lambda x: "_".join(word.upper() for word in re.split(r"([A-Z][0-9a-z]*)", x)[1::2])
upper_to_camel = lambda x: "".join(word.title() for word in x.split("_"))

class VersionedNode(SemiStructuredNode):
    """
    .. py:class::
    This class is the base for all data in the SIIM2 project.
    """

    __index__ = 'CaliopeStorage'

    __extended_classes__ = dict()

    uuid = StringProperty(default=uuidGenerator, unique_index=True)

    timestamp = DateTimeProperty(default=timeStampGenerator)

    change_info = StringProperty(index=True)

    __special_fields__ = set(['timestamp', 'parent', 'uuid'])

    def __new__(cls, *args, **kwargs):
        cls.parent = RelationshipTo(cls, 'PARENT', ZeroOrOne)
        cls.__extended_classes__[cls.__name__] = cls
        return super(VersionedNode, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(VersionedNode, self).__init__(*args, **kwargs)


    def _attributes_to_diff(self, special=False):
        if special:
            return [a for a in self.__dict__ if a[:1] != '_']
        return [a for a in self.__dict__ if a[:1] != '_'
        and a not in self.__special_fields__]

    def _should_save_history(self, stored_node):
        for field in set(self._attributes_to_diff() +
                stored_node._attributes_to_diff()):
        # If versioned nodes have different fields they are different.
            if not hasattr(stored_node, field) or not hasattr(self, field):
                return True
                # A field has a different value.
            if getattr(self, field) != getattr(stored_node, field):
                return True
                # Versioned nodes have the save fields and field values.
        return False

    @classmethod
    def _copy_relationships(cls, old_node, new_node):
        for key, val in cls.__dict__.items():
            if issubclass(val.__class__, RelationshipDefinition):
                if key != 'parent' and hasattr(new_node, key):
                    new_rel = getattr(new_node, key)
                    old_rel = getattr(old_node, key)
                    for related_node in old_rel.all():
                        new_rel.connect(related_node)

    @classmethod
    def push(cls, *args, **kwargs):
        """
        Creates a single node of one class and return it.
        """
        new_node = cls(*args, **kwargs)
        new_node.save()
        return new_node

    @classmethod
    def inflate(cls, node):
        if "uuid" in node._properties:
            return cls.pull(node._properties["uuid"])
        return super(VersionedNode, cls).inflate(node)

    @classmethod
    def pull(cls, uuid, only_class=False):
        """Useful when you have and UUID and you need the inflated object in
        the class it was saved. This methods lookups for the relationship
        which has the `__instance__` property and traceback the class from
        the registered classes in `py:class:cid.core.entities.VersionedNode`.
        The default class for an object is `py:class:cid.core.entities
        .VersionedNode` when no class was traced.

        :param uuid: The UUID of the object you want
        :param only_class: True if you only want to get the class for the uuid.
        :return: An instance of the class of the object with the data.
        `py::const None` if does not exists.
        """
        try:
            versioned_node = VersionedNode.index.get(uuid=uuid)
            node = versioned_node.__node__
            graph_db = node._graph_db
            node_rels = graph_db.match(end_node=node)
            for relationship in node_rels:
                if "__instance__" in relationship._properties \
                    and relationship._properties["__instance__"]:
                    category_node = relationship.start_node
                    category_node.get_properties()
                    node_class = VersionedNode.__extended_classes__[
                        category_node._properties["category"] if
                        "category" in category_node._properties else
                        "VersionedNode"]
            if only_class:
                return node_class
            assert issubclass(node_class, cls)
            return node_class.inflate(node)
        except DoesNotExist as dne:
            #: TODO LOG
            return None


    def _get_node_data(self):
        return self.__properties__

    def _get_data(self):
        return {k: self._format_data(v)
                for k, v in self._get_node_data().iteritems()}

    def _format_data(self, value):
        if isinstance(value, list):
            return [self._format_data(item) for item in value]
        if isinstance(value, dict):
            return {k: self._format_data(v) for k, v in value.iteritems()}
        return {'value': value}

    def _format_relationships(self, rel_name):
        """
        Format relationship in JSON friendly way.
        :param: rel_name: The name of the relationship to be parsed
        :return: A relationship in json friendly dict, example
        {
            'uuid_1': {'property_a': 1, 'property_b': 2},
            'uuid_2': {'property_a': 2, 'property_b': 3}
            'uuid_3': {'property_a': 1, 'property_b': 2},
            'uuid_4': {'property_a': 2, 'property_b': 3}
        }
        """
        rv = {}
        if hasattr(self, rel_name):
            relations = getattr(self, rel_name)
            assert issubclass(relations.__class__, RelationshipManager)
            if self.__node__ is not None:
                for target in relations.all():
                    rel_inst = relations.relationship(target)
                    rv[target.uuid] = dict(rel_inst._properties)
                    #TODO: fix workaround
                    rv[target.uuid]['uuid'] = target.uuid
            return rv
        else:
            raise ValueError("{} not a relationship"
            .format(rel_name))


    def add_or_update_relationship_target(self, rel_name, target_uuid,
                                          new_properties=None, delete=False):
        """
        Add or update  a relationship target. If the relationship target exists,
        the properties get overwritten. Otherwise the relationship target is
        created with the new properties.

        :param: rel_name: The name of the relationship.
        :param: target_uuid: The uuid of the target node.
        :param: new_properties : If set, a dictionary with the new properties.
                If not supplied, all the properties will be deleted.
        """

        target_node = self.__class__.index.get(uuid=target_uuid).__node__
        reldef = getattr(self, rel_name)
        rels = self.__node__.match_one(rel_type=reldef.relation_type,
                                       end_node=target_node,
                                       bidirectional=True)

        #: check if just to delete.
        if delete:
            #check if there is a rel to delete
            if len(rels) == 1:
                #delete the rel
                rels[0].delete()
        else:
            #check if already exists
            if len(rels) == 1:
                #set the new properties
                if new_properties:
                    rels[0].update_properties(new_properties)
                else:
                 #delete properties
                    rels[0].delete_properties()
            else:
                # a new relationship, so connect.
                target_vnode = VersionedNode.pull(target_uuid)
                other_node = reldef.single()
                #TODO: Add support for the different types of cardinality
                if isinstance(reldef, ZeroOrOne) and other_node:
                    reldef.reconnect(other_node,target_vnode)
                    return
                reldef.connect(target_vnode, new_properties)


    def delete_relationship(self, rel_name, target_uuid):
        self.add_or_update_relationship_target(rel_name, target_uuid,
                                               delete=True)


    def _get_relationships(self):
        rv = {}
        for k, v in self.__class__.__dict__.items():
            if k not in self.__special_fields__ and \
                    isinstance(v, RelationshipDefinition):
                rv[k] = v


        return rv

    def serialize(self):
        rv = self._get_data()
        rv.update(self._serialize_relationships())
        return rv

    def _serialize_relationships(self):
        rv = {}
        for rel_name in self._get_relationships():
            assert not rel_name in rv  # TODO : remove
            if rel_name not in self.__special_fields__:
                rv[rel_name] = self._format_relationships(rel_name)
        return rv


    def save(self, skip_difference=False):
        """
        This will save a copy of the previous version of the new, and update
        the changes.

        :param skip_difference: True when saving a previous version, should
                                not be modified unless you know what you're
                                doing.
        :return: The saved object.
        """
        if not skip_difference:
            # TODO(nel): Don't use an exception here.
            try:
                stored_node = self.__class__.index.get(uuid=self.uuid)
            except DoesNotExist:
                stored_node = None
            if stored_node and self._should_save_history(stored_node):
                # The following operations should be atomic.
                copy = stored_node.__class__()
                for field in stored_node._attributes_to_diff():
                    if not isinstance(getattr(stored_node, field),
                                      RelationshipManager):
                        setattr(copy, field, getattr(stored_node, field))
                copy.save(skip_difference=True)
                #Don't keep track of old information
                self._remove_indexes(copy)
                if len(self.parent):
                    copy.parent.connect(self.parent.get())
                    self.parent.disconnect(self.parent.get())
                self.parent.connect(copy)
                self._copy_relationships(self, copy)
                self.timestamp = timeStampGenerator()
        super(VersionedNode, self).save()
        return self


    def _remove_indexes(self, vnode):
        batch = CustomBatch(connection(), vnode.index.name, vnode.__node__.id)
        props = self.deflate(vnode.__properties__, vnode.__node__.id)
        self._remove_prop_indexes(vnode.__node__, props, batch)
        batch.submit()

    def update_field(self, field_name, new_value, field_id=None,
                     special=False):
        """
        Allow granular update of individual fields, including granular items
        and specific keys within dicts.

        Also, allows to update specific index within lists or keys within dicts.
        If the field_name is of type `list` the field_id should be the index to
        be update, if index is -1 a new value will be appended at the end of the
        list. In case the index is not a valid index, will raise an exception.
        If the type of field_name is `dict` the field_id will be the key,
        if the key already exists will be updated if does not exists will be
        create.

        If field_name is not a property or attribute, raise an exception.

        :param field_name: Name of the field to update
        :param new_value: Value that needs to be saved or updated
        :param field_id: If is a list the index to be updated -1 to add a new
                         item, if a dict the key to be updated or added.
        :raise ValueError: If the field_name is not a property of the object.
        """

        if field_name in self._attributes_to_diff(special=special) or \
                        getattr(self, field_name, None) is not None:
            if field_id is not None:
                curr_value = getattr(self, field_name)
                if isinstance(curr_value, list) and isinstance(field_id, int):
                    if field_id == -1:
                        curr_value.append(new_value)
                    elif len(curr_value) > field_id:
                        curr_value[field_id] = new_value
                    else:
                        raise IndexError("Index does {} not exists in {}"
                        .format(field_id, field_name))
                elif isinstance(curr_value, dict) \
                    and isinstance(field_id, (str, unicode)):
                    curr_value[field_id] = new_value
                elif isinstance(curr_value, CaliopeJSONProperty):
                    #: Empty dict propety
                    setattr(self, field_name, {field_id: new_value})
            else:
                setattr(self, field_name, new_value)
            #: Moved to services.commit
            #self.save()
        else:
            #: TODO: change the following line to support adding new
            # properties.
            raise ValueError("{} not a property or attribute"
            .format(field_name))


    def _get_change_history(self, history={}):
        previous = self.parent.single()
        if previous:
            p_data = previous._get_node_data()
            #p_data.update(previous._serialize_relationships())
            c_data = self._get_node_data()
            #c_data.update(self._serialize_relationships())
            diff = DictDiffer(c_data, p_data)
            history[previous.uuid] = \
                {'changed': {k:v for k,v in p_data.iteritems()
                             if k in diff.changed()},\
                 'added': {k:v for k,v in p_data.iteritems()
                           if k in diff.added()},\
                 'removed': {k:v for k,v in p_data.iteritems()
                             if k in diff.removed()},\
                 'unchanged': {k:v for k,v in p_data.iteritems()
                               if k in diff.unchanged()},
                 'change_info': p_data['change_info'] if 'change_info' in
                                                         p_data else 'None'}
            previous._get_change_history(history=history)

        rels = self._serialize_relationships()
        allrels_history = {}
        if rels:
            for k, v in rels.items():
                rel_history = {}
                if v:
                    for r_uuid in v.keys():
                        rel_history[r_uuid] = VersionedNode.pull(r_uuid)._get_change_history(history={})
                allrels_history[k] = rel_history
        history.update(allrels_history)
        return history

    def get_history(self, format='json'):
        if format=='json':
            return {k:self._format_data(v) for k, v in self
            ._get_change_history(history={})\
                .iteritems()}
        else:
            return self._get_change_history()


class NonVersionedNode(VersionedNode):

    def save(self):
        super(self, VersionedNode).save(skip_difference=True)

