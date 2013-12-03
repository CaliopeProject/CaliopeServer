#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Nelson Castillo <nelsoneci@gmail.com>
          Sebastián Ortiz V. neoecos@gmail.com


SIIM Server is the web server of SIIM's Framework
Copyright (C) 2013 Infometrika Ltda

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

# TODO(nel,neoecos): Use assertEqual(a, b) functions and friends.
# http://docs.python.org/2/library/unittest.html#unittest.TestCase

import unittest
import hashlib

from py2neo import neo4j
from cid.core.entities import (VersionedNode,
                               DoesNotExist,
                               UniqueProperty,
                               CaliopeUser,
                               CaliopeGroup,
                               CaliopeJSONProperty)
from neomodel import StringProperty, RelationshipFrom, ZeroOrOne


class TestVersionedNodeStorage(unittest.TestCase):
    def tearDown(self):
        #:Delete database
        neo4j.GraphDatabaseService().clear()

    def printLine(self):
        print "-" * 80

    def test_VersionedNode_add_or_update_relationship_target(self):
        # First, create Person and Car objects.
        class Person(VersionedNode):
            pass
        class Car(VersionedNode):
            owner = RelationshipFrom(Person, 'OWNER', ZeroOrOne)
        person = Person(name='Bob')
        person.save()
        car = Car(plate='7777')
        car.save()

        # Create the relationship and add properties.
        car.owner.connect(person, {'brand' : 'BMW'})

        # Check relationship properties are there.
        assert {'brand': 'BMW'} == car._format_relationships('owner')[
            person.uuid]

        # Delete the relationship properties.
        car.add_or_update_relationship_target('owner', person.uuid)

        # Properties should be empty.
        assert {} == car._format_relationships('owner')[person.uuid]

        # Add new properties. Let's add two.
        car.add_or_update_relationship_target('owner', person.uuid, {'brand' : 'Twingo', 'KM' : 0})
        assert {'brand': 'Twingo', 'KM': 0} == car._format_relationships('owner')[person.uuid]

    def test_VersionedNode_init_without_args(self):
        self.printLine()
        node = VersionedNode()
        node.save()
        print node.uuid, node.timestamp
        node2 = VersionedNode.pull(node.uuid)
        assert node2.uuid == node.uuid
        self.printLine()

    def test_VersionedNode_init_without_args(self):
        self.printLine()
        node = VersionedNode()
        node.save()
        print node.uuid, node.timestamp
        node2 = VersionedNode.pull(node.uuid)
        assert node2.uuid == node.uuid
        self.printLine()

    def test_VersionedNode_init_with_args(self):
        self.printLine()
        props = {'foo': 'bar', 'other': 2}
        node = VersionedNode(**props)
        node.save()
        print node.uuid, node.timestamp
        node.refresh()
        assert node.foo == 'bar' and node.other == 2
        self.printLine()

    def test_VersionedNode_push(self):
        self.printLine()
        props = {'foo': 'bar', 'other': 2}
        node = VersionedNode.push(**props)
        print node.uuid, node.timestamp
        assert node.foo == 'bar' and node.other == 2
        self.printLine()

    def test_VersionedNode_change(self):
        self.printLine()
        props = {'foo': 'bar', 'other': 2}
        node = VersionedNode.push(**props)
        print node.uuid, node.timestamp
        setattr(node, 'foo', 'no_bar')
        setattr(node, 'other', 4)
        node.save()
        assert node.foo == 'no_bar' and node.other == 4
        self.printLine()

    def test_VersionedNode_parent(self):
        self.printLine()
        props = {'foo': 'bar', 'other': 2}
        node = VersionedNode.push(**props)
        print node.uuid, node.timestamp
        setattr(node, 'foo', 'no_bar')
        setattr(node, 'other', 3)
        node.save()
        node_prev = node.parent.single()
        assert node_prev.foo == props['foo']
        assert node_prev.other == props['other']
        self.printLine()

    def test_VersionedNode_history(self):
        self.printLine()
        props = {'foo': 'bar', 'other': 2}
        node = VersionedNode.push(**props)
        print node.uuid, node.timestamp
        setattr(node, 'foo', 'no_bar')
        setattr(node, 'other', 3)
        node.save()
        node_prev = node.parent.single()
        history = node.get_change_history()
        #:TODO Asserts.
        setattr(node, 'x', 'new')
        setattr(node, 'other', 3)
        delattr(node,'foo')
        node.save()
        history = node.get_change_history()

        self.printLine()

    def test_versionednode_update_field(self):
        self.printLine()
        node = VersionedNode()
        node.foo = 'bar'
        node.save()
        print node.uuid, node.timestamp, node.foo
        node.update_field("foo", "new_bar")
        assert node.foo == "new_bar"
        self.printLine()

    def test_VersionedNode_update_field_list_append(self):
        self.printLine()
        node = VersionedNode()
        node.foo = ['item0', "item1"]
        node.save()
        print node.uuid, node.timestamp, node.foo
        node.update_field("foo", "bar", 0)
        assert node.foo[0] == "bar"
        assert node.foo[1] == "item1"
        self.printLine()

    def test_VersionedNode_update_field_list_update(self):
        self.printLine()
        node = VersionedNode()
        node.foo = ['item0', "item1"]
        node.save()
        print node.uuid, node.timestamp, node.foo
        node.update_field("foo", "bar", -1)
        assert node.foo[2] == "bar"
        assert node.foo[0] == "item0"
        assert node.foo[1] == "item1"
        self.printLine()


    def test_VersionedNode_update_field_dict_update(self):
        self.printLine()
        setattr(VersionedNode, "foo", CaliopeJSONProperty())
        node = VersionedNode()
        node.foo = {"foo": "bar", "a": 1}
        node.save()
        print node.uuid, node.timestamp, node.foo
        node.update_field("foo", "new_bar", "foo")
        assert node.foo["foo"] == "new_bar"
        self.printLine()

    def test_VersionedNode_update_field_dict_append(self):
        self.printLine()
        setattr(VersionedNode, "foo", CaliopeJSONProperty())
        node = VersionedNode()
        node.save()
        print node.uuid, node.timestamp, node.foo
        node.update_field("foo", "bar", field_id="foo")
        assert node.foo["foo"] == "bar"
        self.printLine()

    def test_VersionedNode_format_relationships_only_one(self):
        class Person(VersionedNode):
            name = StringProperty()
            age = StringProperty()

        class Car(VersionedNode):
            plate = StringProperty()
            owner = RelationshipFrom(Person, 'OWNER', ZeroOrOne)

        self.printLine()

        person = Person(name='Bob')
        person.age = 10
        person.save()

        car = Car(plate='7777')
        car.save()

        # Test empty relationship
        assert {} == car._format_relationships('owner')
        # Create the relationship with attributes
        car.owner.connect(person, {'km': 0, 'brand': 'BMW'})
        #Expected value for relationships (with different UID):
        #{'Person': {u'21b04fc6-3e97-4584-926a-28497d997447':
        #{u'brand': u'BMW', u'km': 0}}}
        relationships = car._format_relationships('owner')
        assert len(relationships) == 1
        assert person.uuid in relationships
        assert relationships[person.uuid] == {u'brand': u'BMW',
                                              u'km': 0}
        self.printLine()

    def test_VersionedNode_format_relationships_many(self):
        class Car(VersionedNode):
            plate = StringProperty()

        class ParkingLot(VersionedNode):
            parked = RelationshipFrom(Car, 'PARKED')

        self.printLine()

        car_uuids = []
        parking_lot = ParkingLot()
        parking_lot.save()
        for i in range(5):
            car = Car(plate=str(i))
            car.save()
            parking_lot.parked.connect(car, {'i': i})
            car_uuids.append(car.uuid)

        relationships = parking_lot._format_relationships('parked')

        assert len(car_uuids) == len(relationships)
        for i, uuid in enumerate(car_uuids):
            assert uuid in relationships
            assert {'i': i} == relationships[uuid]

        self.printLine()

    def test_VersionedNode_pull(self):
        class Car(VersionedNode):
            plate = StringProperty()

        car = Car(plate="777")
        self.assertIsNotNone(car.save())
        uuid = car.uuid
        pulled_object = Car.pull(uuid)
        self.assertIsInstance(pulled_object, Car)
        self.assertEqual(car.plate, pulled_object.plate)
        car.delete()


    #: TODO: Move the following test to a new file.
    def test_CaliopeUser_creation(self):
        self.printLine()
        u1 = CaliopeUser()
        u1.username = 'userTmp'
        u1.password = hashlib.sha256(u'123').hexdigest()
        u1.domainname = 'correlibre.org'
        u1.first_name = "UserTmp"
        u1.last_name = "Test"
        assert u1.save() is not None
        self.printLine()

    def test_CaliopeUser_creationMany(self):
        self.printLine()
        for i in xrange(20):
            u1 = CaliopeUser()
            u1.username = 'userTmp' + str(i)
            u1.password = hashlib.sha256('password' + str(i)).hexdigest()
            u1.domainname = 'correlibre.org'
            u1.first_name = "UserTmp" + str(i)
            u1.last_name = "Test"
            assert u1.save() is not None
        self.printLine()

    def test_CaliopeGroup_creation(self):
        self.printLine()
        g1 = CaliopeGroup()
        g1.name = 'GroupTmp'
        g1.code = 'g-000Tmp'
        assert g1.save() is not None
        g1.delete()
        self.printLine()

    def test_CaliopeGroup_creationMany(self):
        self.printLine()
        for i in xrange(1, 5):
            g1 = CaliopeGroup()
            g1.name = u'Group' + str(i)
            g1.code = u'g-00' + str(i)
            try:
                assert g1.save() is not None
                g1.delete()
            except UniqueProperty:
                pass
        self.printLine()

    def test_CaliopeGroup_connectOne(self):
        self.printLine()
        try:
            u1 = CaliopeUser()
            u1.username = 'userTmp'
            u1.password = hashlib.sha256(u'123').hexdigest()
            u1.domainname = 'correlibre.org'
            u1.first_name = "User"
            u1.last_name = "Test"
            u1.save()
            g1 = CaliopeGroup()
            g1.name = 'GroupTmp'
            g1.code = 'g-000Tmp'
            g1.save()
            u1.member_of.connect(g1)
            g1.members.connect(u1)
            assert u1.member_of.is_connected(g1)
            assert g1.members.is_connected(u1)
            g1.delete()
            u1.delete()
        except UniqueProperty:
            assert False
        self.printLine()


if __name__ == '__main__':
    unittest.main()
