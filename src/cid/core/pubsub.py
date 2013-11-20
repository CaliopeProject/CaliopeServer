# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org

SIIM2 Server is the web server of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

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
from hotqueue import HotQueue

from flask import g

from redis import Redis

import json

from cid.utils.helpers import DatetimeEncoder


class PubSub(object):
    def __new__(cls, *args, **kwargs):
        cls.r = Redis()
        return cls

    @classmethod
    def register_uuid_and_thread_id(cls, user_uuid):
        cls.r.hset('thread_pool_id', str(g.connection_thread_id), str(user_uuid))
        cls.r.sadd(str(user_uuid)+'_threads',str(g.connection_thread_id))

    @classmethod
    def subscribe_uuid_with_user_uuid(cls, user_uuid, uuid):
        if True: #TODO: check user_uuid
            list = cls.r.smembers(str(user_uuid)+'_threads')
            for thread_id in list:
                cls._subscribe_uuid_with_connection_thread_id(thread_id,uuid)

    @classmethod
    def subscribe_uuid(cls, uuid):
        if True: #TODO: check uuid
            return cls._subscribe_uuid_with_connection_thread_id(g.connection_thread_id,uuid)
        else:
            return None

    @classmethod
    def _subscribe_uuid_with_connection_thread_id(cls, connection_thread_id,uuid):
        if True: #TODO: check connection_thread_id
            queue = HotQueue("connection_thread_id_queue=" + str(connection_thread_id))
            msg = {'cmd': 'subscribe', 'params': str(uuid)}
            queue.put(json.dumps(msg))
            return msg
        else:
            return None

    @classmethod
    def unsubscribe_uuid(cls, uuid):
        if True: #TODO: check uuid
            queue = HotQueue("connection_thread_id_queue=" + str(g.connection_thread_id))
            msg = {'cmd': 'unsubscribe', 'params': str(uuid)}
            queue.put(json.dumps(msg))
            return msg
        else:
            return None

    @classmethod
    def publish_command(cls, from_uuid, res_uuid, method, data):
        if True: #TODO:  check from_uuid, res_uuid

            cmd = {
                "jsonrpc": "2.0",
                "method": method,
                "params": data,
                "id": str(res_uuid),
                "thread": str(g.connection_thread_id)
            }
            cls.r.publish('uuid=' + str(res_uuid), json.dumps(cmd, cls=DatetimeEncoder))

            return True
        else:
            return False

