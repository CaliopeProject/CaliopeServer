#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
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
# -*- coding: utf-8 -*-
import os
import unittest
import json
import uuid
import hashlib

from cid import caliope_server
from cid.core.models import CaliopeNode, CaliopeUser, CaliopeGroup
from neomodel import DoesNotExist, UniqueProperty

from cid.core.entities import CaliopeEntity, CaliopeEntityData


class SIIM2ServerTestCase(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank enviroment"""
        caliope_server.app.config['TESTING'] = True
        caliope_server.init_flask_app()
        caliope_server.configure_server_and_app("../../conf/caliope_server.json")
        caliope_server.configure_logger("../../conf/tests_logger.json")
        caliope_server.register_modules()
        self.app = caliope_server.app.test_client()

    def tearDown(self):
        """Get rid of the database again after each test."""
        pass

    def login(self, username, password, callback_id):
        data = dict(cmd="login.autenticate",
                    login=username,
                    password=password,
                    callback_id=callback_id
                    )
        response = self.app.post('/api/rest', data=json.dumps(data),
                                 content_type='application/json')
        return response

    # testing functions
    def test_login(self):
        #: TODO: Implement
        assert True

class TestCaliopeStorage(unittest.TestCase):

    def test_CaliopeNode_init_without_args(self):
        print "Test#1"
        print "-" * 80
        node = CaliopeNode()
        node.save()
        print node.uuid, node.timestamp
        node2 = CaliopeNode.pull(node.uuid)
        assert node2.uuid == node.uuid
        node.delete()
        print u"-" * 80

    def test_CaliopeNode_init_with_args(self):
        print "Test#2"
        print "-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode(**props)
        node.save()
        print node.uuid, node.timestamp
        node.refresh()
        assert node.foo == 'bar' and node.other == 2
        node.delete()
        print "-" * 80

    def test_CaliopeNode_push(self):
        print "Test#3"
        print "-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode.push(**props)
        print node.uuid, node.timestamp
        assert node.foo == 'bar' and node.other == 2
        node.delete()
        print u"-" * 80

    def test_CaliopeNode_evolve(self):
        print "Test#4"
        print "-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode.push(**props)
        print node.uuid, node.timestamp
        node = node.evolve(**{'foo': 'no_bar', 'other': 4})
        assert node.foo == 'no_bar' and node.other == 4
        for ancestor in node.traverse('ancestor_node').run():
            ancestor.delete()
        node.delete()
        print "-" * 80

    def test_CaliopeNode_ancestor(self):
        print "Test#5"
        print "-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode.push(**props)
        print node.uuid, node.timestamp
        node_next = node.evolve()
        node_prev = node_next.ancestor_node.single()
        assert node_prev == node
        node_next.delete()
        node_prev.delete()

    def test_CaliopeUser_creation(self):
        print "Test#6"
        print "-" * 80
        u1 = CaliopeUser()
        u1.username = 'userTmp'
        u1.password = hashlib.sha256(u'123').hexdigest()
        u1.domainname = 'correlibre.org'
        u1.first_name = "UserTmp"
        u1.last_name = "Test"
        assert u1.save() is not None
        u1.delete()
        print "-" * 80

    def test_CaliopeUser_creationMany(self):
        print "Test#7"
        print "-" * 80
        for i in xrange(20):
            u1 = CaliopeUser()
            u1.username = 'userTmp' + str(i)
            u1.password = hashlib.sha256('password' + str(i)).hexdigest()
            u1.domainname = 'correlibre.org'
            u1.first_name = "UserTmp" + str(i)
            u1.last_name = "Test"
            assert u1.save() is not None
            u1.delete()
        print "-" * 80


    def test_CaliopeGroup_creation(self):
        print "Test#8"
        print "-" * 80
        g1 = CaliopeGroup()
        g1.name = 'GroupTmp'
        g1.code = 'g-000Tmp'
        assert g1.save() is not None
        g1.delete()
        print "-" * 80

    def test_CaliopeGroup_creationMany(self):
        print "Test#9"
        print "-" * 80
        for i in xrange(1,5):
            g1 = CaliopeGroup()
            g1.name = u'Group'+ str(i)
            g1.code = u'g-00' + str(i)
            try:
                assert g1.save() is not None
                g1.delete()
            except UniqueProperty:
                assert True
        print "-" * 80

    def test_CaliopeGroup_connectOne(self):
        print "Test#10"
        print "-" * 80
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
            g1.refresh()
            u1.delete()
            u1.refresh()
        except UniqueProperty:
            assert False
        print "-" * 80

    def test_CaliopeStorage_defaultUserGroupOne(self):
        print "Test#11"
        print "-" * 80
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
        print "-" * 80

    def test_CaliopeStorage_defaultUserGroupMany(self):
        print "Test#12"
        print "-" * 80
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
        print "-" * 80

    def test_CaliopeEntity_creationMany(self):
        print "Test#13"
        print "-" * 80
        for i in xrange(1,5):
            e1 = CaliopeEntity()
            try:
                assert e1.save() is not None
                e1.delete()
            except UniqueProperty:
                assert True
        print "-" * 80


if __name__ == '__main__':
    unittest.main()
