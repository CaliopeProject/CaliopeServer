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
import json
import uuid
from functools import wraps
from datetime import datetime
from pytz import utc

#flask
from flask.globals import current_app
from flask import (session, request, Blueprint, make_response)

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc import BadRequestError, RPCBatchRequest
from tinyrpc.dispatch import RPCDispatcher

#CaliopeStorage
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeUser, CaliopeNode

#Apps import
from ...utils import loadJSONFromFile
from ...model import SIIMModel
from ..login import LoginManager
from ..forms import FormManager

dispatcher_bp = Blueprint('dispatcher', __name__, template_folder='pages')

storage_sessions = {}

dispatcher = RPCDispatcher()

jsonrpc = JSONRPCProtocol()

#This does magics
dispatcher.register_instance(LoginManager(), 'login.')
dispatcher.register_instance(FormManager(), 'form.')

@dispatcher_bp.route('/ws')
def ws_endpoint():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            ws_message = ws.receive()
            if ws_message is None:
                current_app.logger.warn('Request: ' + request.__str__() + '\tmessage: None')
                break
            else:
                handle_incoming_jsonrpc_message(ws_message, ws)

@dispatcher_bp.route('/rest', methods=['POST'])
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
        rpc_response = json_request.error_respond(e)
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
        return dispatcher.dispatch(request)
    except Exception as e:
        # for example, a method wasn't found
        return request.error_respond(e)


def event_logging(func):
    @wraps(func)
    def decorated_logging(*args, **kwargs):
        print "log: %s" % (args,)
        return func(*args, **kwargs)

    return decorated_logging


#@login_required
def getPrivilegedForm(session, params):
    error = None
    result = {
        'result': 'ok',
        'form': loadJSONFromFile(current_app.config["FORM_TEMPLATES"]
                                 + "/" + params["formId"] + ".json", current_app.root_path),
        'actions': ["create"]
    }
    return result, error


@event_logging
#:TODO Implement the method with different version and domain options.
def getFormTemplate(session, params):
    result = None
    error = None

    if 'formId' in params:
        formId = params['formId']
        if 'domain' in params:
            domain = params['domain']
        else:
            domain = ''
        if 'version' in params:
            version = params['version']
        else:
            version = ''
    if formId == 'login':
        result = {
            'result': 'ok',
            'form': loadJSONFromFile(current_app.config['FORM_TEMPLATES']
                                     + "/" + "login.json", current_app.root_path),
            'actions': ["authenticate"]
        }   

    elif formId == 'proyectomtv':
        result, error = getPrivilegedForm(session, params)
    elif formId == 'SIIMForm':
        result, error = getPrivilegedForm(session, params)
    else:
        error = {
            'code': -32600,
            'message': "invalid form"
        }
    return result, error


#@login_required
def createFromForm(session, params):
    error = None
    result = None

    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    form_data = params['data'] if 'data' in params else {}
    if form_id == 'SIIMForm':
        form = SIIMModel.SIIMForm(**form_data)
        #: default responde is error
        try:
            form.save()
            result = {'uuid': form.uuid}
        except Exception:
            error = {
                'code': -32600,
                'message': "Unknown error : " + Exception.params()
            }
        finally:
            return result, error
    else:
        error = {
            'code': -32600,
            'message': 'Class ' + form_id + ' not found in Model'
        }
        return result, error

#@login_required
def editFromForm(session, params):
    error = None
    result = None
    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    form_data = params['data'] if 'data' in params else {}
    if form_id == 'SIIMForm':
        #: TODO: Update to SIIMForm.pull(uuid) when update to Caliope_Odisea > 0.0.4
        form = SIIMModel.SIIMForm.index.get(uuid=form_data['uuid'])
        try:
            #: this will evolve the node
            form = form.set_form_data(form_data)
            result = {'uuid': form.uuid}
        except Exception:
            error = {
                'code': -32600,
                'message': "Unknown error : " + Exception.params()
            }
        finally:
            return result, error
    else:
        error = {
            'code': -32600,
            'message': 'Class ' + form_id + ' not found in Model'
        }
        return result, error

#: TODO: This method is NOT doing what is suppose to do.
#@login_required
def deleteFromForm(session, params):
    error = None
    result = None
    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    form_data = params['data'] if 'data' in params else {}
    if form_id == 'SIIMForm':
        form = SIIMModel.SIIMForm.index.get(uuid=form_data['uuid'])
        #form.set_form_data(form_data)
        try:
            #form.save()
            result = {'uuid': form.uuid}
        except Exception:
            error = {
                'code': -32600,
                'message': "Unknown error : " + Exception.params()
            }
        finally:
            return result, error
    else:
        error = {
            'code': -32600,
            'message': 'Class ' + form_id + ' not found in Model'
        }
        return result, error


def getFormData(session, params):
    error = None
    result = None
    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    data_uuid = params['uuid'] if 'uuid' in params else ''
    if form_id == 'SIIMForm':
        try:
            form_node = SIIMModel.SIIMForm.index.get(uuid=data_uuid)
            result = {
                'data': form_node.get_form_data(),
                #: TODO: Create a helper private method to access forms
                'form': loadJSONFromFile(current_app.config["FORM_TEMPLATES"]
                                         + "/" + params["formId"] + ".json", current_app.root_path),
                'actions': ["create", "delete", "edit"]
            }

        except DoesNotExist:
            error = {
                'code': -32600,
                'message': 'Not found in db with uuid: ' + uuid
            }
        except Exception:
            error = {
                'code': -32600,
                'message': Exception.params()
            }

        finally:
            return result, error


def getFormDataList(session, params):
    error = None
    result = None
    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    filters = params['filters'] if 'filters' in params else {}
    if form_id == 'SIIMForm':
        try:
            #: TODO: Implement filters and ranged searchs
            form_nodes_list = SIIMModel.SIIMForm.index.search('uuid:*')
            form_nodes_data_list = []
            for node in form_nodes_list:
                form_nodes_data_list.append(node.get_form_data())

            result = {
                'data': form_nodes_data_list,
            }

        except DoesNotExist:
            error = {
                'code': -32600,
                'message': 'Not found in db with uuid: ' + uuid
            }
        except Exception:
            error = {
                'code': -32600,
                'message': Exception.params()
            }

        finally:
            return result, error

