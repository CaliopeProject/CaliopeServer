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

from neomodel import StringProperty, DateTimeProperty, RelationshipTo, ZeroOrOne, DoesNotExist, RelationshipDefinition, RelationshipManager
from neomodel.contrib import SemiStructuredNode

from cid.core.utils import uuidGenerator, timeStampGenerator

class VersionedNode(SemiStructuredNode):
    """
    :class: VersionedNode
    """

    __index__ = 'CaliopeStorage'

    uuid = StringProperty(default = uuidGenerator, unique_index = True)

    #: All timestamps should be in UTC using pytz.utc
    # TODO:
    # 1) When a timestamp is stored and then loaded the value is different.
    #    Timezone issue.
    # 2) Check that the timestamp is updated when needed.
    timestamp = DateTimeProperty(default = timeStampGenerator)

    __special_fields__ = set(['timestamp', 'parent', 'uuid'])

    def __new__(cls, *args, **kwargs):
        cls.parent = RelationshipTo(cls, 'PARENT', ZeroOrOne)
        return super(VersionedNode, cls).__new__(cls, *args, **kwargs)

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

    """def _copy_connections_broken(self, new_node):
        for attribute_name in self._attributes_to_diff():
            if not issubclass(getattr(self, attribute_name).__class__, \
                              RelationshipManager):
                continue # Not a relationship. Nothing to do.
	    if not hasattr(new_node, attribute_name):
                continue # New node doesn't have the relationship.
	    self_rel = getattr(self, attribute_name)
	    new_rel = getattr(new_node, attribute_name)
            print 'hey', new_rel.__class__
	    for node in self_rel.all():
                print 'old rel', self_rel
                print 'BEGIN connecting', new_rel, 'to', node
                print 'New node uuid', new_node.uuid
	        new_rel.connect(node)
                print 'END'
    """

    @classmethod
    def _copy_connections(cls, old_node, new_node):
        for key, val in cls.__dict__.items():
            if issubclass(val.__class__, RelationshipDefinition):
                if key != 'parent' and hasattr(new_node, key):
                    new_rel = getattr(new_node, key)
                    old_rel = getattr(old_node, key)
                    print key, val.__class__
                    print 'old_rel', old_rel
                    print 'new_rel', new_rel
                    for n in old_rel.all():
                        #saved = False
                        #for node_class_rel in n._get_class_relationships():
                        #    node_rel = getattr(n,node_class_rel[0], None)
                        #    if issubclass(node_rel.__class__, (One, ZeroOrOne)):
                        #        if (getattr(node_rel, 'relation_type', None) ==
                        #            getattr(new_rel, 'relation_type', None)):
                        #            node_rel.reconnect(old_node, new_node)
                        #            saved = True
                        #if not saved:
                        #    new_rel.connect(n)
                        new_rel.connect(n)

    def save(self, skip_difference = False):
        if not skip_difference:
            # TODO(nel): Don't use an exception here.
            try:
                stored_node = self.__class__.index.get(uuid = self.uuid)
            except DoesNotExist:
                stored_node = None
            if stored_node and self._should_save_history(stored_node):
                # The following operations should be atomic.
                copy = stored_node.__class__()
                print 'class', stored_node.__class__
                print 'COPY', copy
                print 'STOR', stored_node
	        for field in stored_node._attributes_to_diff():
                    setattr(copy, field, getattr(stored_node, field))
		copy.save(skip_difference = True)
                if len(self.parent):
                    copy.parent.connect(self.parent.get())
                    self.parent.disconnect(self.parent.get())
                self.parent.connect(copy)
                #self._copy_connections(self, copy)
                self.timestamp = timeStampGenerator()
        super(VersionedNode, self).save()

    def __init__(self, *args, **kwargs):
        super(VersionedNode, self).__init__(*args, **kwargs)

#class Car(VersionedNode):
#  plate = StringProperty()

# TODO(nel): Make this a test.
# Sample use:
#class Person(VersionedNode):
#   name = StringProperty()
#   age = StringProperty()
#   car = RelationshipTo(Car, 'CAR')

#person = Person(name = 'Alice')
#person.age = 10
#person.save()
#person = Person(name = 'Bob')
#person.age = 10

#car = Car(plate = '7777')
#car.save()
#person.save()
#person.car.connect(car)

#person.age = 20
#person.save()
#person.age = 30
#person.save()
#person.age = 40
#person.save()
