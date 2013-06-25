#!/usr/bin/env python
# coding: utf-8

import os
import json

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, render_template, session, request, Response
from gevent import sleep
from gevent import monkey; monkey.patch_all()
import uuid
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

storage_sessions = {}


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

    if 'user' in session:
        result = {
                 'result': 'ok', 
                 'msg': "already logged", 
                 'uuid': session['session_uuid']
                 }
    elif message['login'] == "admin" and message['password'] ==  hashlib.sha256("admin").hexdigest():
        session['user'] = message['login']
        session['session_uuid'] = str(uuid.uuid4())
        storage_sessions[session['session_uuid']] = {}
        storage_sessions[session['session_uuid']]['user'] = session['user']
        response_msg = "new session:" + message['login'] \
                       + " uuid=" + session['session_uuid']
        result = {
                 'result': 'ok', 
                 'msg': response_msg, 
                 'uuid' : session['session_uuid']
                 }
    else:
        response_msg = "login error" + "(" + message['login'] + ", " \
                       + message['password'] + ")"
        result = {
                 'result': 'error', 
                 'msg': response_msg
                 }

    return result


def process_message(session, message):
    res = {
           'result': 'error', 
           'msg': 'error', 
          }  
    if "cmd" not in message:
        pass
    elif message['cmd'] == 'authentication':
        res = login_with_name(session, message)
    elif message['cmd'] == 'authentication_with_uuid':
        res = login_with_uuid(session, message)
    return res


@app.route('/')
def index():
        return render_template('index.html')


@app.route('/api')
def api():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            if message is None:
                break
            
            message = json.loads(message)
            res = process_message(session, message)
            ws.send(json.dumps(res))


@app.route('/rest', methods = ['POST'])
def rest():
    print request.json
    message=request.json
    res = process_message(session, message)
    return json.dumps(res)

    
def event_stream():
    count = 0
    while True:
        sleep(3)
        f = os.popen('fortune')
        yield 'data: %s\n\n' % f.read()
        f.close()
        # yield 'data: %s\n\n' % count
        count += 1


@app.route('/event_from_server')
def sse_request():
    return Response(
        event_stream(),
        mimetype='text/event-stream')


if __name__ == '__main__':
    http_server = WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
