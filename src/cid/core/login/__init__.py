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

from tinyrpc.dispatch import public
from flask import current_app


class LoginManager(object):

    @staticmethod
    @public
    def autenticate(username, password, domain=None):
        try:
            #: TODO: Add support to domain
            userNode = CaliopeUser.index.get(username=username)
            if userNode.password == password:
                #valid user, domain, password combination
                lm = LoginManager(user=userNode)
                current_app.g.lm = lm
                session_uuid = lm.validate_user_session(username)
                return {'login': True, 'uuid': session_uuid}
        except DoesNotExist:
                return {'login': False, 'uuid': None}

    def __int__(self, *args, **kwargs):
        self.user = kwargs['user'] if 'user' in kwargs else None

    def get_user(self):
        if self.user is not None:
            return self.user
        else:
            #: TODO: Raise some exception
            return None

    def validate_user_session(self, username):
        """

        This methods effectively register the session of an authenticated user,
        if the session timestamp is newer than 30 minutes, the session uuid remains the same,
        and the timestamp is updated, if the session timestamp is old than 30 minutes, a new uuid
        is generated.

        If the session did not existed at all, a new uuid with fresh timestamp are added to user session.

        """
        #: TODO: Load refresh timeout from app configuration.
        #: TODO: Review the best way to send uuid to client, maybe a "api_key" hmaced ;)?
        #: TODO: Change key for session_storage key value should be the uuid or api_key?s
        app = current_app
        session_storage = app.config['session_storage']
        if username in session_storage:
            user_session = session_storage[username]
            if datetime.now() > user_session['timestamp'] + timedelta(minutes=30):
                user_session['timestamp'] = datetime.now()
                user_session['uuid'] = str(uuid4()).decode('utf-8')
            else:
                user_session['timestamp'] = datetime.now()
        else:
            user_session = dict()
            user_session['uuid'] = str(uuid4()).decode('utf-8')
            user_session['timestamp'] = datetime.now()
            session_storage[username] = user_session
        return user_session['uuid']

    @staticmethod
    def login_required(func):
        app = current_app
        session_storage = app.config['session_storage']
        @wraps(func)
        def decorated_view(*args, **kwargs):
            #: TODO: Define a way to validate request
            #: TODO: Change this, for now if user is logged it will work, else false.
            if 'user' in session_storage:
                return func(*args, **kwargs)
            else:
                return Exception('Not authorized')
            return decorated_view

    #: TODO: Not implemented yet
    #def _is_fresh_session(session):
    #    return True




