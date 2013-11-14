#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
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

class AccessControlTestCase(unittest.TestCase):
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
        DefaultDatabase().test_defaultUserGroupOne()

    def tearDown(self):
        """Get rid of the database again after each test."""
        if self.rpc_client:
            self.rpc_client.transport.close()
        self.http_server.stop()
        self.http_server = None
        caliope_server.app = Flask('caliope_server')
        #:Delete database
        neo4j.GraphDatabaseService().clear()


    def login(self, username='user', password='123'):
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


    """def test_login(self):
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
    """

    def test_isAccessGranted(self):
        # TODO(nel): Deprecate this method.
        self.login()
        ac_proxy = self.rpc_client.get_proxy("ac.")
        self.assertEqual({'granted': True}, ac_proxy.isAccessGranted({}))

    def test_getUserList(self):
        self.login()
        ac_proxy = self.rpc_client.get_proxy("ac.")
        user_list = set(['revisor_1', 'revisor_2', 'revisor_3', 'recepcionista_1',
                         'recepcionista_2', 'superuser', 'secretaria_1', 'reportero_1',
                         'reportero_2', 'gerente_1'])
        for user in ac_proxy.getUserList({}):
            self.assertIn(user, user_list)
            user_list.remove(user)
        self.assertEqual(user_list, set())

    #def test_getGroupList(self):
    #    self.login()
    #    ac_proxy = self.rpc_client.get_proxy("ac.")
    #    print ac_proxy.getGroupList({})

if __name__ == '__main__':
    unittest.main()
