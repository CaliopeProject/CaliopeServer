#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Sebastián Ortiz V. neoecos@gmail.com

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

#gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.client import RPCClient, RPCError
from tinyrpc.transports.http import HttpWebSocketClientTransport

#neo4j
from py2neo import neo4j

#flask
from flask import (Flask)

#simplekv
import redis
from simplekv.memory.redisstore import RedisStore

from cid import caliope_server
from cid.core.entities import (DoesNotExist,
                               UniqueProperty,
                               CaliopeUser,
                               CaliopeGroup)


class TaskServicesTestCase(unittest.TestCase):
    def setUp(self):
        caliope_server.app.config['TESTING'] = True
        caliope_server.init_flask_app()
        caliope_server.configure_server_and_app(
            "conf/test_caliope_server.json")
        caliope_server.configure_logger("conf/tests_logger.json")
        caliope_server.register_modules()
        caliope_server.app.storekv = RedisStore(redis.StrictRedis())
        self.http_server = WSGIServer((caliope_server.app.config['address'],
                                       caliope_server.app.config['port']),
                                      caliope_server.app,
                                      handler_class=WebSocketHandler)  # @IgnorePep8
        self.http_server.start()
        self.nodes_created = set()
        self.create_default_database()

    def tearDown(self):
        """Get rid of the database again after each test."""
        if self.rpc_client:
            self.rpc_client.transport.close()
        self.http_server.stop()
        self.http_server = None
        caliope_server.app = Flask('caliope_server')
        #:Delete database
        self.remove_used_nodes(self.nodes_created)


    def create_default_database(self):
        self.create_UserGroup('user', 'group')

    def create_UserGroup(self, username, groupname):
        try:
            u1 = CaliopeUser()
            u1.username = username
            u1.password = hashlib.sha256(u'123').hexdigest()
            u1.domainname = 'correlibre.org'
            u1.first_name = "User"
            u1.last_name = "Test"
            u1.avatar = "common-img/avatar.png"
            u1.save()
            self.nodes_created.add(u1.uuid)
            g1 = CaliopeGroup()
            g1.name = groupname
            g1.code = groupname
            g1.save()
            self.nodes_created.add(g1.uuid)
            u1.member_of.connect(g1)
            g1.members.connect(u1)
            self.assertTrue(u1.member_of.is_connected(g1))
            self.assertTrue(g1.members.is_connected(u1))
        except UniqueProperty:
            try:
                u1 = CaliopeUser.index.get(username=username)
                g1 = CaliopeGroup.index.get(code=groupname)
                assert u1 is not None and g1 is not None
                assert u1.member_of.is_connected(g1)
                assert g1.members.is_connected(u1)
            except DoesNotExist:
                assert False

    def remove_used_nodes(self, node_list):
        query = "START n=node:CaliopeStorage('uuid:{}') " \
                "MATCH  n-[r]-() " \
                "DELETE n, r"
        batch_query = []
        for uuid in node_list:
            batch_query.append(neo4j.cypher.Query(neo4j.GraphDatabaseService(),
                                                  query.format(uuid)).execute())

    def login(self, username, password):
        self.rpc_client = RPCClient(JSONRPCProtocol(),
                                    HttpWebSocketClientTransport(
                                        'ws://localhost:9001/api/ws'))
        self.loginManager = self.rpc_client.get_proxy("login.")
        hashed_password = hashlib.sha256(password).hexdigest()
        return self.loginManager.authenticate(username=username,
                                              password=hashed_password)

    def logout(self, uuid):
        if self.loginManager is None:
            return
        return self.loginManager.logout(uuid=uuid)


    def test_login(self):
        rv = self.login(u'user', u'123')
        expected = \
            {u'first_name': {u'value': u'User'},
             u'last_name': {u'value': u'Test'},
             u'image': {u'data': None},
             u'user': {u'value': u'user'},
             u'login': True,
            }
        self.assertDictContainsSubset(expected, rv)
        self.assertIn("session_uuid", rv)
        self.assertIn("user_uuid", rv)


    def test_logout(self):
        uuid = self.login(u'user', u'123')['user_uuid']['value']
        rv = self.logout(uuid=uuid)
        self.assertIn('logout', rv)
        self.assertTrue(rv['logout'])
        self.assertIn('uuid', rv)
        self.assertEqual(uuid, rv['uuid'])


    def test_ts_get_model(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        self.assertIsNotNone(model)

    def test_task_get_model_and_data(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        self.assertIsNotNone(model)
        uuid = model["data"]["uuid"]["value"]
        #:update
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="name",
                                         value="test")

        #:commit
        commit = tasks_proxy.commit(uuid=uuid)
        self.assertTrue(commit)
        model_and_data = tasks_proxy.getModelAndData(uuid=uuid)
        self.assertEqual(model_and_data["data"]["name"]["value"], "test")


    def test_task_update_commit_field_single_value(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        uuid = model["data"]["uuid"]["value"]
        #:update
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="name",
                                         value="test")

        #:commit
        commit = tasks_proxy.commit(uuid=uuid)
        self.assertTrue(commit)

        #:update a commited value
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="name",
                                         value="foo")
        self.assertTrue(update)

        #:commit again a previusly commited value after being updated
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #:update twice a draft and commit
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="name",
                                         value="more foo")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="name",
                                         value="not more foo")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))
        self.nodes_created.add(uuid)


    def test_task_update_commit_field_single_value_not_exist_in_class(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        uuid = model["data"]["uuid"]["value"]
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="other",
                                         value="test")
        self.assertTrue(update)
        try:
            response = tasks_proxy.commit(uuid=uuid)
        except RPCError as error:
            self.assertIsInstance(error, RPCError)

    def test_task_update_commit_field_list(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        uuid = model["data"]["uuid"]["value"]

        #:update invalid index first.
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="subtasks",
                                             subfield_id=0,
                                             value="subtask0")
            self.assertTrue(update)
        except RPCError as error:
            self.assertIsInstance(error, RPCError)

        #:update and commit with empty lists
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=-1,
                                         value="subtask0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #: update and commit already commited lists
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         value="new_subtask0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #: update twice and commit
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         value="new_subtask0_up1")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         value="new_subtask_up2")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #:update a non valid subfield_id
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="subtasks",
                                             subfield_id=1,
                                             value="not subtask1")
        except RPCError as error:
            self.assertIsInstance(error, RPCError)

    def test_task_update_commit_field_list_list(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        uuid = model["data"]["uuid"]["value"]

        #:update with invalid pos
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="subtasks",
                                             subfield_id=-1,
                                             pos=0,
                                             value="subtask0")
        except RPCError as error:
            self.assertIsInstance(error, RPCError)

        #:update with invalid subfield_id
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="subtasks",
                                             subfield_id=0,
                                             pos=-1,
                                             value="subtask0")
        except RPCError as error:
            self.assertIsInstance(error, RPCError)

        #:update and commit with empty lists
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=-1,
                                         pos=-1,
                                         value="subtask0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #: update and commit already commited lists
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos=0,
                                         value="new_subtask0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #update twice same, append new and commit
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos=0,
                                         value="new_subtask0_up1")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos=0,
                                         value="new_subtask0_up2")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos=-1,
                                         value="new_subtask1_up2")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #:update a non valid pos
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="subtasks",
                                             subfield_id=0,
                                             pos=1,
                                             value="not subtask1")
        except RPCError as error:
            self.assertIsInstance(error, RPCError)


    def test_task_update_commit_field_list_dict(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        uuid = model["data"]["uuid"]["value"]

        #:update with invalid subfield_id
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="subtasks",
                                             subfield_id=0,
                                             pos="foo",
                                             value="subtask0")
        except RPCError as error:
            self.assertIsInstance(error, RPCError)

        #:update and commit with empty subfield
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=-1,
                                         pos="foo",
                                         value="subtask0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #: update and commit already commited lists
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos="foo",
                                         value="new_subtask0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #update twice same, append new and commit
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos="foo1",
                                         value="new_subtask0_up1")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos="foo1",
                                         value="new_subtask0_up2")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="subtasks",
                                         subfield_id=0,
                                         pos="foo_new",
                                         value="new_subtask0_up2")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #:update a non valid pos
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="subtasks",
                                             subfield_id=0,
                                             pos=1,
                                             value="not subtask1")
        except RPCError as error:
            self.assertIsInstance(error, RPCError)

    def test_task_update_commit_field_dict(self):
        user = self.login(u'user', u'123')
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        uuid = model["data"]["uuid"]["value"]


        #:update and commint for fist time
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="comments",
                                         subfield_id="user1",
                                         value="comment0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #: update and commit already commited lists
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="comments",
                                         subfield_id="user1",
                                         value="comment0_up0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #: update twice, append new and commit
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="comments",
                                         subfield_id="user1",
                                         value="comment0_up1")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="comments",
                                         subfield_id="user1",
                                         value="comment0_up2")
        self.assertTrue(update)
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="comments",
                                         subfield_id="user2",
                                         value="comment0")
        self.assertTrue(update)
        self.assertTrue(tasks_proxy.commit(uuid=uuid))

        #:update a non valid subfield_id
        try:
            update = tasks_proxy.updateField(uuid=uuid,
                                             field_name="comments",
                                             subfield_id=1,
                                             value="not subtask1")
        except RPCError as error:
            self.assertIsInstance(error, RPCError)


if __name__ == '__main__':
    unittest.main()
