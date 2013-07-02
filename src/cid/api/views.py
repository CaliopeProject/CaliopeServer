# -*- encoding: utf-8 -*-
'''
Created on 27/06/2013

@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

Caliope Server is the web server of Caliope's Framework
Copyright (C) 2013 Fundación Correlibre

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
'''
#system, and standard library
import json
import uuid

#flask
from flask.globals import current_app
from flask import (Flask, render_template, session, request, Response, abort,
                   Blueprint)


#Apps import
from cid.utils.fileUtils import loadJSONFromFile

#CaliopeStorage
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeUser

api = Blueprint('api', __name__, template_folder='pages')

storage_sessions = {}


@api.route('/rest', methods=['POST'])
def rest():
    print request.json
    message = request.json
    res = process_message(session, message)
    return json.dumps(res)


@api.route('/ws')
def index():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            if current_app.debug:
                print message
            if message is None:
                break
            try:
                messageJSON = json.loads(message)
            except ValueError:
                messageJSON = json.loads('{}')
            res = process_message(session, messageJSON)
            ws.send(json.dumps(res))


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
    try:
        if 'user' in session:
            result = {
                     'result': 'ok',
                     'msg': "already logged",
                     'uuid': session['session_uuid']
                     }
        user = CaliopeUser.index.get(username=message['login'])
        print user.password, message['password']
        if user.password == message['password']:
            session['user'] = message['login']
            session['session_uuid'] = str(uuid.uuid4()).decode('utf-8')
            storage_sessions[session['session_uuid']] = {}
            storage_sessions[session['session_uuid']]['user'] = session['user']
            response_msg = "new session:" + message['login'] \
                           + " uuid=" + session['session_uuid']
            result = {
                     'result': 'ok',
                     'msg': response_msg,
                     'uuid': session['session_uuid']
                     }
    except DoesNotExist:
        response_msg = "login error" + "(" + message['login'] + ", " \
                       + message['password'] + ")"
        result = {
                 'result': 'error',
                 'msg': response_msg
                 }

    return result


def getFormTemplate(message):
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
                                           + "/" + "login.json"),
                  }
    else:
        if current_app.debug:
            print result
    return result


def process_message(session, message):
    res = {
           'result': 'error',
           'msg': 'error',
          }
    if "cmd" not in message or 'callback_id' not in message:
        cmd = ''
        callback_id = '0'
    else:
        cmd = message['cmd']
        callback_id = message['callback_id']
        if current_app.debug:
            print "Received a command: " + cmd + " with args "\
                  + message.__repr__()
        if cmd == 'authentication':
            res = login_with_name(session, message)
        elif cmd == 'authentication_with_uuid':
            res = login_with_uuid(session, message)
        elif cmd == 'getFormTemplate':
            res = getFormTemplate(message)
    res['callback_id'] = callback_id
    if current_app.debug:
        print res
    return res
