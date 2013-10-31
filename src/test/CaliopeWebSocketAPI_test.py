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
from cid.utils.DefaultDatabase import DefaultDatabase



class CaliopeServerTestCase(unittest.TestCase):
    def setUp(self):
        caliope_server.app.config['TESTING'] = True
        caliope_server.init_flask_app()
        caliope_server.configure_server_and_app("../../conf/test_caliope_server.json")
        caliope_server.configure_logger("../../conf/tests_logger.json")
        caliope_server.register_modules()
        caliope_server.app.storekv = RedisStore(redis.StrictRedis())
        self.http_server = WSGIServer((caliope_server.app.config['address'],
                                       caliope_server.app.config['port']),
                                      caliope_server.app,
                                      handler_class=WebSocketHandler)  # @IgnorePep8
        self.http_server.start()
        self.create_default_database()

    def tearDown(self):
        """Get rid of the database again after each test."""
        if self.rpc_client:
            self.rpc_client.transport.close()
        self.http_server.stop()
        self.http_server = None
        caliope_server.app = Flask('caliope_server')
        #:Delete database
        neo4j.GraphDatabaseService().clear()


    def create_default_database(self):
        DefaultDatabase().test_defaultUserGroupOne()


    def login(self, username, password):
        self.rpc_client = RPCClient(JSONRPCProtocol(),
                                    HttpWebSocketClientTransport('ws://localhost:9001/api/ws'))
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
        assert 'login' in rv
        assert rv['login'] is True
        assert 'user_uuid' in rv
        assert 'session_uuid' in rv

    def test_logout(self):
        uuid = self.login(u'user', u'123')['user_uuid']['value']
        rv = self.logout(uuid=uuid)
        assert 'logout' in rv
        assert rv['logout']

    def test_accounts_get_public_info(self):
        users = [self.login(u'user', u'123')['user_uuid']['value']]
        accounts_proxy = self.rpc_client.get_proxy(prefix="accounts.")
        info = accounts_proxy.getPublicInfo(users)
        assert len(info) == 1
        assert 'uuid' in info[0]
        for user in users:
            info_uuid = info[0]['uuid']['value']
            assert user == info_uuid

    def test_task_get_model(self):
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


    def test_projects_create(self):
        user = self.login(u'user', u'123')
        projects_proxy = self.rpc_client.get_proxy(prefix="projects.")
        model = projects_proxy.getModel()
        data = {"name": "PROYECTO 305",
                "general_location": "<p><em><strong>ASDASDASD</strong></em><br></p>",
                "locality": "suba",
                "project_type": "py_gr_escala",
                "profit_center": "ASDASDADS",
                "areas": [{"tipo": "A1", "valor": "121"}, {"tipo": "A2", "valor": "13"}],
                "uuid": model['data']['uuid']['value']
        }
        #: TODO Check for real asserts
        try:
            rv = projects_proxy.create(data=data)
            assert True
        except BaseException:
            assert False

    def test_projects_get_all(self):
        user = self.login(u'user', u'123')
        projects_proxy = self.rpc_client.get_proxy(prefix="projects.")
        rv = projects_proxy.getAll()
        self.assertIsNotNone(rv)


if __name__ == '__main__':
    unittest.main()
