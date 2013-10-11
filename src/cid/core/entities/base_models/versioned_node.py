# -*- coding: utf-8 -*-
"""
    cid.core.entities.versioned_node
    ~~~~~~~~~~~~~~

    :author: Sebastián Ortiz <neoecos@gmail.com>
    :author: Nelson Castillo <nelsoneci@gmail.com>
    :copyright: (c) 2013 por Fundación CorreLibre
    :license:  GNU AFFERO GENERAL PUBLIC LICENSE

SIIM2 Storage is the base of SIIM2's Framework
Copyright (C) 2013  Fundación Correlibre

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

from neomodel import StringProperty, DateTimeProperty, RelationshipTo, ZeroOrOne, One, DoesNotExist, RelationshipDefinition, RelationshipManager, RelationshipFrom
from neomodel.contrib import SemiStructuredNode

from cid.core.utils import uuidGenerator, timeStampGenerator


class VersionedNode(SemiStructuredNode):
    """
    :class: VersionedNode
    """

    __index__ = 'CaliopeStorage'

    uuid = StringProperty(default=uuidGenerator, unique_index=True)

    #: All timestamps should be in UTC using pytz.utc
    # TODO:
    # 1) When a timestamp is stored and then loaded the value is different.
    #    Timezone issue.
    # 2) Check that the timestamp is updated when needed.
    timestamp = DateTimeProperty(default=timeStampGenerator)

    __special_fields__ = set(['timestamp', 'parent', 'uuid'])

    def __new__(cls, *args, **kwargs):
        cls.parent = RelationshipTo(cls, 'PARENT', ZeroOrOne)
        return super(VersionedNode, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(VersionedNode, self).__init__(*args, **kwargs)

    def _attributes_to_diff(self):
        return [a for a in self.__dict__ if a[:1] != '_' \
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
    def pull(cls, id_node):
        return cls.index.get(uuid=id_node)

    @classmethod
    def push(cls, *args, **kwargs):
        """
        Creates a single node of one class and return it.
        """
        new_node = cls(*args, **kwargs)
        new_node.save()
        return new_node

    def _get_node_data(self):
        return self.__properties__

    def _get_data(self):
        return {k: self._format_data(v) \
                for k, v in self._get_node_data().iteritems()}

    def _format_data(self, value):
        if isinstance(value, list):
            return [self._format_data(item) for item in value]
        if isinstance(value, dict):
            return {k: self._format_data(v) for k, v in value.iteritems()}
        return {'value': value}

    def _format_relationships(self, rel_name):
        """
        Format in a json friendly way a relationship, including direction, and target.
        Target contains the class, the properties and the uuid of the object

        :param rel_name: The name of the relationship to be parsed
        :return: A relationship in json friendly dict, example
        `{'direction':0,
         'target':[
                    {'entity':'class name',
                     'entity_data': {'uuid': 'UUID4', 'other':'some'},
                     'properties':{'category':'prop1', 'other_prop':'foo'}
                    },
                    ...
                  ]
        }`
        """
        rel = getattr(self, rel_name)
        target = []
        if self.__node__ is not None:
            for rel_target in rel.all():
                rel_inst = rel.relationship(rel_target)  # Returns relationship instance.
                target.append({
                    'entity': repr(rel_target.__class__),
                    'properties': dict(rel_inst._properties),
                    'entity_data': {'uuid': rel_target.uuid},
                })
                # If there is no target to return, return an empty target with the entity class name.
        if len(target) == 0:
            for t_name, t_class in rel.target_map.items():
                target.append({
                    'entity': repr(t_class),
                    'properties': {},
                    'entity_data': {},
                })
        rv = {
            'target': target,
            'direction': rel.definition['direction'],
        }
        return rv

    def _get_relationships(self):
        rv = {}
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, RelationshipDefinition):
                rv[k] = v
        return rv

    def serialize(self):
        rv = self._get_data()
        for rel_name in self._get_relationships():
            assert not rel_name in rv  # TODO : remove
            if rel_name not in self.__special_fields__:
                rv[rel_name] = self._format_relationships(rel_name)
        return rv

    def update_relationship(self, rel_name, new_rel_dict):

        def dict_diff(dict_a, dict_b):
            """
            :return Return the keys of the dict_a that are not in the dict_b
            """
            return set(dict_a).difference(dict_b)

        def dict_intersection(dict_a, dict_b):
            """
            :return Return the keys of the dict_a that also are in dict_b
            """
            return set(dict_a).intersection(dict_b)

        current_rel_dict = self._format_relationships(rel_name)
        assert current_rel_dict['direction'] == new_rel_dict['direction']
        for key_not_in_new in dict_diff(current_rel_dict, new_rel_dict):
            pass
        for key_not_in_current in dict_diff(new_rel_dict, current_rel_dict):
            pass
        for key_in_both in dict_intersection(current_rel_dict, new_rel_dict):
            pass



    def save(self, skip_difference=False):
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
                    if not isinstance(getattr(stored_node, field), RelationshipManager):
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


"""
class Person(VersionedNode):
    name = StringProperty()
    age = StringProperty()
    #car = RelationshipTo(Car, 'CAR')

class Car(VersionedNode):
    plate = StringProperty()
    owner = RelationshipFrom(Person, 'OWNER', ZeroOrOne)

person = Person(name='Bob')
person.age = 10
person.save()

print  person.serialize()

car = Car(plate='7777')
car.save()
car.owner.connect(person)

print car.serialize()

import sys
sys.exit(1)
"""
