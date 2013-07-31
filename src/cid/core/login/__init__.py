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
from uuid import uuid4
from datetime import datetime, timedelta
from functools import wraps

#CaliopeStorage
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeUser

from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError, JSONRPCInternalError
from tinyrpc.dispatch import public
from flask import current_app, g

dummy_storage_for_authenticate_with_uuid = {}

def login_required(func, **kwargs):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            #: TODO: Define a way to validate request
            #: TODO: Change this, for now if user is logged it will work, else false.
            app = current_app
            session_storage = app.config['session_storage']
            if 'user' in session_storage and session_storage['user']['uuid'] == kwargs['uuid']:
                return func(*args, **kwargs)
            else:
                return JSONRPCInternalError('Not authorized')
            return decorated_view

    #: TODO: Not implemented yet
    #def _is_fresh_session(session):
    #    return True

class LoginManager(object):

    @staticmethod
    @public
    def authenticate(username, password, domain=None):
        try:
            #: TODO: Add support to domain
            userNode = CaliopeUser.index.get(username=username)
            if userNode.password == password:
                session_uuid = str(uuid4()).decode('utf-8')
                
                #!!!!!!!!!!!!!!!!!!!!thread safe untested!!!!!!!!!!!!!!!!!!
                g.conection_thread_pool_id[g.conection_thread_id] = session_uuid 
                dummy_storage_for_authenticate_with_uuid[session_uuid] = username
                return {'login': True, 'uuid': session_uuid, 'user': username}
            else:
                return {'login': False}
        except DoesNotExist:
                return {'login': False}
        except Exception as e:
                raise JSONRPCInternalError(e)


    @staticmethod
    @public
    def authenticate_with_uuid(uuid, domain=None):
        if uuid in dummy_storage_for_authenticate_with_uuid:
            username = dummy_storage_for_authenticate_with_uuid[uuid]
            return {'login': True, 'uuid': uuid, 'user': username}
        else:
            raise JSONRPCInternalError('No valid session found')


    @staticmethod
    @public
    def logout(uuid):
        if uuid in dummy_storage_for_authenticate_with_uuid:
            del dummy_storage_for_authenticate_with_uuid[uuid]
        return {'logout': True, 'uuid': uuid}

    @staticmethod
    def check():
        #!!!!!!!!!!!!!!!!!!!!thread safe untested!!!!!!!!!!!!!!!!!!
        if g.conection_thread_id in g.conection_thread_pool_id:
            if g.conection_thread_pool_id[g.conection_thread_id] in dummy_storage_for_authenticate_with_uuid:
                return True
        return False

    @staticmethod
    def get_user():
        #!!!!!!!!!!!!!!!!!!!!thread safe untested!!!!!!!!!!!!!!!!!!
        if g.conection_thread_id in g.conection_thread_pool_id:
            if g.conection_thread_pool_id[g.conection_thread_id] in dummy_storage_for_authenticate_with_uuid:
                return dummy_storage_for_authenticate_with_uuid[g.conection_thread_pool_id[g.conection_thread_id]]
        return None        
    
    #def get_user(self):
        #if self.user is not None:
            #return self.user
        #else:
            ##: TODO: Raise some exception
            #return None

    #def validate_user_session(self, username):
        #"""

        #This methods effectively register the session of an authenticated user,
        #if the session timestamp is newer than 30 minutes, the session uuid remains the same,
        #and the timestamp is updated, if the session timestamp is old than 30 minutes, a new uuid
        #is generated.

        #If the session did not existed at all, a new uuid with fresh timestamp are added to user session.

        #"""
        ##: TODO: Load refresh timeout from app configuration.
        ##: TODO: Review the best way to send uuid to client, maybe a "api_key" hmaced ;)?
        ##: TODO: Change key for session_storage key value should be the uuid or api_key?s
        #app = current_app
        #session_storage = app.config['session_storage']
        #if username in session_storage:
            #user_session = session_storage[username]
            #if datetime.now() > user_session['timestamp'] + timedelta(minutes=30):
                #user_session['timestamp'] = datetime.now()
                #user_session['uuid'] = str(uuid4()).decode('utf-8')
            #else:
                #user_session['timestamp'] = datetime.now()
        #else:
            #user_session = dict()
            #user_session['uuid'] = str(uuid4()).decode('utf-8')
            #user_session['timestamp'] = datetime.now()
            #session_storage[username] = user_session
        #dummy_storage_for_authenticate_with_uuid[user_session['uuid']] = username
        #self.user_session = user_session
        #return user_session['uuid']

    #def invalidate_user_session(self):
        #app = current_app
        #session_storage = app.config['session_storage']
        #if self.user.username in session_storage:
            #session_storage[self.user.username] = None
            #return {'login': False}
        #else:
            #return JSONRPCInvalidRequestError()

    #def is_authenticated(self):
        #return self.get_user() is not None

    #@public
    #def get_session_uuid(self):
        #return {'uuid': self.user_session['uuid']}





