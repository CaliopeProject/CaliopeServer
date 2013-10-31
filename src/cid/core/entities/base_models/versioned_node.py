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
import types

from py2neo import neo4j
from neomodel import (StringProperty,
                      DateTimeProperty,
                      RelationshipTo,
                      AliasProperty,
                      ZeroOrOne,
                      One,
                      DoesNotExist,
                      RelationshipDefinition,
                      RelationshipManager,
                      RelationshipFrom)

from neomodel.contrib import SemiStructuredNode

from cid.core.utils import uuidGenerator, timeStampGenerator

from caliope_properties import CaliopeJSONProperty


class VersionedNode(SemiStructuredNode):
    """
    .. py:class::
    This class is the base for all data in the SIIM2 project.
    """

    __index__ = 'CaliopeStorage'

    __extended_classes__ = dict()

    uuid = StringProperty(default=uuidGenerator, unique_index=True)

    timestamp = DateTimeProperty(default=timeStampGenerator)

    __special_fields__ = set(['timestamp', 'parent', 'uuid'])

    def __new__(cls, *args, **kwargs):
        cls.parent = RelationshipTo(cls, 'PARENT', ZeroOrOne)
        cls.__extended_classes__[cls.__name__] = cls
        return super(VersionedNode, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(VersionedNode, self).__init__(*args, **kwargs)


    def _attributes_to_diff(self):
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
    def pull(cls, uuid):
        """Useful when you have and UUID and you need the inflated object in
        the class it was saved. This methods lookups for the relationship
        which has the `__instance__` property and traceback the class from
        the registered classes in `py:class:cid.core.entities.VersionedNode`.
        The default class for an object is `py:class:cid.core.entities
        .VersionedNode` when no class was traced.

        :param uuid: The UUID of the object you want
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
            assert cls == node_class
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
            'class_1': {'uuid_1': {'property_a': 1, 'property_b': 2},
                        'uuid_2': {'property_a': 2, 'property_b': 3}
                        },
            'class_2': {'uuid_3': {'property_a': 1, 'property_b': 2},
                        'uuid_4': {'property_a': 2, 'property_b': 3}
                        },
                }
        """
        rv = {}
        if self.__node__ and hasattr(self, rel_name):
            relations = getattr(self, rel_name)
            assert issubclass(relations.__class__, RelationshipManager)
            for target in relations.all():
                target_class_name = target.__class__.__name__
                if not target_class_name in rv:
                    rv[target_class_name] = {}
                rel_inst = relations.relationship(target)
                rv[target_class_name][target.uuid] = dict(rel_inst._properties)
        return rv

    def add_or_update_relationship_target(self, rel_name, target_uuid, new_properties=None):
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
        rels = self.__node__.match_one(rel_type=rel_name.upper(),
                                       end_node=target_node,
                                       bidirectional=True)
        assert len(rels) == 1
        if new_properties:
            rels[0].update_properties(new_properties)
        else:
            rels[0].delete_properties()

    def _get_relationships(self):
        rv = {}
        for k, v in self.__class__.__dict__.items():
            if k not in self.__special_fields__ and \
                    isinstance(v, RelationshipDefinition):
                rv[k] = v
        return rv

    def serialize(self):
        rv = self._get_data()
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
                if len(self.parent):
                    copy.parent.connect(self.parent.get())
                    self.parent.disconnect(self.parent.get())
                self.parent.connect(copy)
                self._copy_relationships(self, copy)
                self.timestamp = timeStampGenerator()
        super(VersionedNode, self).save()
        return self

    def update_field(self, field_name, new_value, field_id=None):
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

        if field_name in self._attributes_to_diff() or \
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
                    #: Empty dict property
                    setattr(self, field_name, {field_id: new_value})
            else:
                setattr(self, field_name, new_value)
            self.save()
        else:
            #: TODO: change the following line to support adding new
            # properties.
            raise ValueError("{} not a property or attribute"
            .format(field_name))


class Contextable(object):
    """Mixing class for allowing create contexts between nodes.
    """
    def __init__(self, *args, **kwargs):
        try:
            super(Contextable, self).__init__(*args, **kwargs)
        except TypeError:
            super(Contextable, self).__init__()
        self.__context__ = RelationshipFrom(VersionedNode, "__CONTEXT__")

class Holdable(object):
    """Mixing class for allowing create contexts between nodes.
    """
    def __init__(self, *args, **kwargs):
        try:
            super(Holdable, self).__init__(*args, **kwargs)
        except TypeError:
            super(Holdable, self).__init__()
        self.__hold__ = RelationshipFrom(Holder, "__HOLD__")


class Holder(object):
    """Mixing class for allowing create contexts between nodes.
    """
    def __init__(self, *args, **kwargs):
        try:
            super(Holdable, self).__init__(*args, **kwargs)
        except TypeError:
            super(Holdable, self).__init__()
        self.__hold__ = RelationshipTo(Holdable, "__HOLD__")

