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
from tinyrpc.client import RPCClient
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
        tasks_proxy = self.rpc_client.get_proxy(prefix="projects.")
        model = tasks_proxy.getModel()
        self.assertIsNotNone(model)

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
