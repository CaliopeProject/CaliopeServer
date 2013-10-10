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
import unittest
import hashlib

from py2neo import neo4j
from cid.core.entities import VersionedNode, DoesNotExist, UniqueProperty, CaliopeUser, CaliopeGroup


class TestVersionedNodeStorage(unittest.TestCase):
    def tearDown(self):
        neo4j.GraphDatabaseService().clear()

    def printLine():
        print "-" * 80

    def test_VersionedNode_init_without_args(self):
        print "Test#1"
        self.printLine()
        node = VersionedNode()
        node.save()
        print node.uuid, node.timestamp
        node2 = VersionedNode.pull(node.uuid)
        assert node2.uuid == node.uuid
        self.printLine()

    def test_VersionedNode_init_with_args(self):
        print "Test#2"
        self.printLine()
        props = {'foo': 'bar', 'other': 2}
        node = VersionedNode(**props)
        node.save()
        print node.uuid, node.timestamp
        node.refresh()
        assert node.foo == 'bar' and node.other == 2
        self.printLine()

    def test_VersionedNode_push(self):
        print "Test#3"
        self.printLine()
        props = {'foo': 'bar', 'other': 2}
        node = VersionedNode.push(**props)
        print node.uuid, node.timestamp
        assert node.foo == 'bar' and node.other == 2
        self.printLine()

    def test_VersionedNode_change(self):
        print "Test#4"
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
        print "Test#5"
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

    def test_CaliopeUser_creation(self):
        print "Test#6"
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
        print "Test#7"
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
        print "Test#8"
        self.printLine()
        g1 = CaliopeGroup()
        g1.name = 'GroupTmp'
        g1.code = 'g-000Tmp'
        assert g1.save() is not None
        g1.delete()
        self.printLine()

    def test_CaliopeGroup_creationMany(self):
        print "Test#9"
        self.printLine()
        for i in xrange(1, 5):
            g1 = CaliopeGroup()
            g1.name = u'Group' + str(i)
            g1.code = u'g-00' + str(i)
            try:
                assert g1.save() is not None
                g1.delete()
            except UniqueProperty:
                assert True
        self.printLine()

    def test_CaliopeGroup_connectOne(self):
        print "Test#10"
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

    def test_CaliopeStorage_defaultUserGroupOne(self):
        print "Test#11"
        self.printLine()
        try:
            u1 = CaliopeUser()
            u1.username = 'user'
            u1.password = hashlib.sha256(u'123').hexdigest()
            u1.domainname = 'correlibre.org'
            u1.first_name = "User"
            u1.last_name = "Test"
            u1.save()
            g1 = CaliopeGroup()
            g1.name = 'Group'
            g1.code = 'g-000'
            g1.save()
            u1.member_of.connect(g1)
            g1.members.connect(u1)
            assert u1.member_of.is_connected(g1)
            assert g1.members.is_connected(u1)
        except UniqueProperty:
            try:
                u1 = CaliopeUser.index.get(username='user')
                g1 = CaliopeGroup.index.get(code='g-000')
                assert u1 is not None and g1 is not None
                assert u1.member_of.is_connected(g1)
                assert g1.members.is_connected(u1)
            except DoesNotExist:
                assert False
        self.printLine()

    def test_CaliopeStorage_defaultUserGroupMany(self):
        print "Test#12"
        self.printLine()
        try:
            for i in xrange(1, 5):
                u1 = CaliopeUser()
                u1.username = 'user' + str(i)
                u1.password = hashlib.sha256(u'123').hexdigest()
                u1.domainname = 'correlibre.org'
                u1.first_name = "User" + str(i)
                u1.last_name = "Test"
                u1.save()
                g1 = CaliopeGroup()
                g1.name = 'Group' + str(i)
                g1.code = 'g-00' + str(i)
                g1.save()
                u1.member_of.connect(g1)
                g1.members.connect(u1)
                assert u1.member_of.is_connected(g1)
                assert g1.members.is_connected(u1)
        except UniqueProperty:
            try:
                for i in xrange(1, 5):
                    u1 = CaliopeUser.index.get(username='user' + str(i))
                    g1 = CaliopeGroup.index.get(code='g-00' + str(i))
                    assert u1 is not None and g1 is not None
                    assert u1.member_of.is_connected(g1)
                    assert g1.members.is_connected(u1)
            except DoesNotExist:
                assert False
        self.printLine()


if __name__ == '__main__':
    unittest.main()
