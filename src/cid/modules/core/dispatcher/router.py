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
from flask import (session, request, Blueprint)

#Apps import
from src.cid.utils.fileUtils import loadJSONFromFile
from src.cid.utils import helpers


#CaliopeStorage
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeUser, CaliopeNode
from src.cid.model import SIIMModel

#Moved to package __init__.py
dispatcher = Blueprint('dispatcher', __name__, template_folder='pages')
storage_sessions = {}


@dispatcher.route('/rest', methods=['POST'])
def rest():
    current_app.logger.debug('POST:' + request.get_data(as_text=True))
    message = request.json
    res = process_message(session, message)
    return json.dumps(res)


@dispatcher.route('/ws')
def index():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            if message is None:
                current_app.logger.warn('Request: ' + request.__str__() + '\tmessage: None')
                break
            try:
                messageJSON = json.loads(message)
                current_app.logger.info('Request: ' + request.__str__() + '\tmessage: ' + message
                                        + '\tmessageJSON: ' + str(messageJSON))
            except ValueError:
                current_app.logger.error('Request ' + request.__str__()
                                         + '\tmessage:' + message)
                messageJSON = json.loads('{}')
            res = process_message(session, messageJSON)
            ws.send(json.dumps(res))


#: TODO: Not implemented yet
def _is_fresh_session(session):
    return True


def login_error(user=False, fresh=False):
    msg = u''
    if user:
        msg += u"Session don't exists for user"
    if fresh:
        msg += u"Session is not fresh"
    res = {
        'result': 'ok',
        'msg': msg,
    }
    return res


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user' in session:
            return func(*args, **kwargs)
        else:
            return login_error(user=True)

    return decorated_view


def event_logging(func):
    @wraps(func)
    def decorated_logging(*args, **kwargs):
        print "log: %s" % (args,)
        return func(*args, **kwargs)

    return decorated_logging


def login_with_uuid(session, message):
    session_uuid = message['uuid']
    if session_uuid in storage_sessions:
        session['user'] = storage_sessions[session_uuid]['user']
        session['session_uuid'] = session_uuid
        response_msg = "uuid found, user=" + session['user']
        return {'result': 'ok', 'msg': response_msg, 'uuid': session_uuid}

    else:
        response_msg = "uuid not found"
        return {'result': 'error', 'msg': response_msg}


def login_with_name(session, message):
    """
    Default username after run CaliopeTestNode is
    user:password
    """
    #: TODO: Enable system to be session oriented, so one user can have multiple active sessions
    #: TODO: Check security of this autentication method

    response = helpers.get_json_response_base(error=True)
    if 'user' in session:
        response['result'] = 'ok'
        response['data'] = {'uuid': session['session_uuid']}
        return response
    try:
        user = CaliopeUser.index.get(username=message['login'])
        #: TODO Add to log
        if user.password == message['password']:
            session['user'] = message['login']
            session['session_uuid'] = str(uuid.uuid4()).decode('utf-8')
            storage_sessions[session['session_uuid']] = {}
            storage_sessions[session['session_uuid']]['user'] = session['user']
            storage_sessions[session['session_uuid']]['start_time'] = datetime.now(utc)
            response = helpers.get_json_response_base()
            response['data'] = {'uuid': session['session_uuid']}
        else:
            response['result'] = 'error'
            response['msg'] = 'The password does not match the username'
    except DoesNotExist:
        response = helpers.get_json_response_base(error=True)
        response['msg'] = "The username does not exists"
    finally:
        return response

#@login_required
def getPrivilegedForm(session, message):
    result = {
        'result': 'ok',
        'data': loadJSONFromFile(current_app.config["FORM_TEMPLATES"]
                                 + "/" + message["formId"] + ".json", current_app.root_path)
    }
    return result


@event_logging
#:TODO Implement the method with different version and domain options.
def getFormTemplate(session, message):
    result = {
        'result': 'error',
        'msg': 'error',
    }
    if 'formId' in message:
        formId = message['formId']
        if 'domain' in message:
            domain = message['domain']
        else:
            domain = ''
        if 'version' in message:
            version = message['version']
        else:
            version = ''
    if formId == 'login':
        result = {
            'result': 'ok',
            'data': loadJSONFromFile(current_app.config['FORM_TEMPLATES']
                                     + "/" + "login.json",  current_app.root_path),
        }
    elif formId == 'proyectomtv':
        result = getPrivilegedForm(session, message)
    elif formId == 'SIIMForm':
        result = getPrivilegedForm(session, message)
    return result


#@login_required
def createFromForm(session, message):
    form_id = message['formId'] if 'formId' in message else 'SIIMForm'
    form_data = message['data'] if 'data' in message else {}
    if form_id == 'SIIMForm':
        form = SIIMModel.SIIMForm(**form_data)
        #: default responde is error
        rv = helpers.get_json_response_base(error=True)
        try:
            form.save()
            rv = helpers.get_json_response_base()
            rv['data'] = {'uuid': form.uuid}
        except Exception:
            rv['msg'] = "Unknown error " + Exception.message()
        finally:
            return rv
    else:
        rv = helpers.get_json_response_base(error=True)
        rv['msg'] = 'Class ' + form_id + ' not found in Model'
        return rv


def getFormData(session, message):
    form_id = message['formId'] if 'formId' in message else 'SIIMForm'
    data_uuid = message['uuid'] if 'uuid' in message else ''
    if form_id == 'SIIMForm':
        try:
            form_node = SIIMModel.SIIMForm.index.get(uuid=data_uuid)
            response = helpers.get_json_response_base()
            response['data'] = form_node.get_form_data()
            #: TODO: Create a helper private method to access forms
            response['form'] = loadJSONFromFile(current_app.config["FORM_TEMPLATES"]
                                 + "/" + message["formId"] + ".json", current_app.root_path)
            response['actions'] = ["create", "delete", "edit"]

        except DoesNotExist:
            response = helpers.get_json_response_base(error=True)
            response['msg'] = 'Not found in db with uuid: ' + uuid
        except Exception:
            response = helpers.get_json_response_base(error=True)
            response['msg'] = Exception.message()
        finally:
            return response



def process_message(session, message):
    res = helpers.get_json_response_base(error=True)
    if "cmd" not in message or 'callback_id' not in message:
        cmd = ''
        callback_id = '0'
        current_app.logger.warn("Message did not contain a valid command, messageJSON: " + str(message))
    else:
        current_app.logger.debug('Command: ' + str(message))
        cmd = message['cmd']
        callback_id = message['callback_id']
        if cmd == 'authentication':
            res = login_with_name(session, message)
        elif cmd == 'authentication_with_uuid':
            res = login_with_uuid(session, message)
        elif cmd == 'getFormTemplate':
            res = getFormTemplate(session, message)
        elif cmd == 'create':
            res = createFromForm(session, message)
        elif cmd == 'getFormData':
            res = getFormData(session, message)
    res['callback_id'] = callback_id
    current_app.logger.debug('Result: ' + str(res))
    return res
