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
from functools import wraps

#flask
from flask.globals import current_app
from flask import ( request, Blueprint, g)

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc import BadRequestError


bp = Blueprint('api', __name__, template_folder='pages')

jsonrpc = JSONRPCProtocol()

connection_thread_pool_id = {}


@bp.route('/api/ws')
def ws_endpoint():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        connection_thread_id = uuid.uuid1()
        connection_thread_pool_id[connection_thread_id] = None
        g.connection_thread_pool_id = connection_thread_pool_id
        while True:
            g.connection_thread_id = connection_thread_id
            ws_message = ws.receive()
            if ws_message is None:
                current_app.logger.warn('Request: ' + request.__str__() + '\tmessage: None')
                break
            else:
                handle_incoming_jsonrpc_message(ws_message, ws)

        del connection_thread_pool_id[connection_thread_id]


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
            rpc_response = json_request.create_batch_response(
                handle_request(req) for req in json_request
            )
        else:
            rpc_response = handle_request(json_request)

    # now send the response to the client
    if rpc_response is not None:
        if handler is not None:
            handler.send(rpc_response.serialize())
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

