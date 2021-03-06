# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

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
#system, and standard library
import uuid
import json
from functools import wraps

#flask
from flask.globals import current_app
from flask import (request, Blueprint, g, copy_current_request_context)

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc import BadRequestError

import gevent
import redis
from hotqueue import HotQueue

from cid.utils.helpers import DatetimeEncoder, DatetimeDecoder

bp = Blueprint('api', __name__, template_folder='pages')

jsonrpc = JSONRPCProtocol()

connection_thread_pool_id = dict()


@bp.route('/api/ws')
def ws_endpoint():
    @copy_current_request_context
    def cmd_greenlet(ws, connection_thread_id):
        connection_thread_pool_id[connection_thread_id] = None
        g.connection_thread_pool_id = connection_thread_pool_id
        while True:
            g.connection_thread_id = connection_thread_id
            ws_message = ws.receive()
            if ws_message is None:
                if ws.socket is None:
                    break
                else:
                    current_app.logger.warn('Request: ' + request.__str__() + '\tmessage: None')
            else:
                handle_incoming_jsonrpc_message(ws_message, ws)
        del connection_thread_pool_id[connection_thread_id]

    def subscribe_greenlet(ps, connection_thread_id):
        queue = HotQueue("connection_thread_id_queue=" + str(connection_thread_id))
        for msg in queue.consume():
            try:
                cmd = json.loads(msg)
                if cmd['cmd'] == 'subscribe':
                    ps.subscribe('uuid=' + cmd['params'])
                elif cmd['cmd'] == 'subscribe':
                    ps.unsubscribe('uuid=' + cmd['params'])
            except:
                pass

    def notifications_greenlet(ws, ps, connection_thread_id):
        ps.subscribe('broadcast')
        for item in ps.listen():
            try:
                data = json.loads(item['data'], object_hook=DatetimeDecoder.json_date_parser)
                if data:
                    #: Do not notify the publisher
                    if data['loopback'] == False and data['thread'] == str(connection_thread_id):
                        pass #omit message
                    else:
                        del data['loopback']
                        del data['thread']

                        ws.send(json.dumps(data, cls=DatetimeEncoder))
            except Exception as e:
                pass

    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        connection_thread_id = uuid.uuid1()

        r = redis.Redis()
        ps = r.pubsub()

        subscriptions = gevent.spawn(subscribe_greenlet, ps, connection_thread_id)
        notifications = gevent.spawn(notifications_greenlet, ws, ps, connection_thread_id)
        cmd = gevent.spawn(cmd_greenlet, ws, connection_thread_id)

        gevent.joinall([cmd])
        gevent.killall([subscriptions, notifications])

        return "Closed WebSocketConnection"


@bp.route('/rest', methods=['POST'])
def rest_endpoint():
    current_app.logger.debug('POST:' + request.get_data(as_text=True))
    post_message = request.data
    if post_message is None:
        current_app.logger.warn('POST: ' + request.__str__() + '\tmessage: None')
    else:
        rv = handle_incoming_jsonrpc_message(post_message)
        return rv


#data can be from any transport layer
def handle_incoming_jsonrpc_message(data, handler=None):
    """
    Validate the RPC, check if batch or single and handle the valid RPC

    :param data: The string containing the json request
    :param handler: The transport handler with method send(data)
    :return: If handler is not present, the data of the response.
    """
    try:
        json_request = jsonrpc.parse_request(data)
    except BadRequestError as e:
        # request was invalid, directly create response
        rpc_response = e.error_respond()
    else:
        if hasattr(json_request, 'create_batch_response'):
            rpc_response = json_request.create_batch_response()
            for request in json_request:
                rpc_response.append(handle_request(request))
        else:
            rpc_response = handle_request(json_request)

    # now send the response to the client
    if rpc_response is not None:
        if handler is not None:
            if handler.socket is not None:
                handler.send(rpc_response.serialize())
            else:
                #:Closed connection
                current_app.logger.warn('Connection closed', None)

        else:
            return rpc_response.serialize()


def handle_request(request):
    try:
        # do magic with method, args, kwargs...
        return getattr(current_app, 'dispatcher', None).dispatch(request)
    except Exception as e:
        # for example, a method wasn't found
        return request.error_respond(e)


def event_logging(func):
    @wraps(func)
    def decorated_logging(*args, **kwargs):
        print "log: %s" % (args,)
        return func(*args, **kwargs)

    return decorated_logging


