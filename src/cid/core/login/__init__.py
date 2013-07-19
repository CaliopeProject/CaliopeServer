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
from datetime import datetime

#CaliopeStorage
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeUser

from tinyrpc.dispatch import public
from flask import current_app, session


class LoginManager(object):

    @staticmethod
    @public
    def autenticate(username, password, domain=''):
        try:
            #: TODO: Add support to domain
            userNode = CaliopeUser.index.get(username=username)
            if userNode.password == password:
                #valid user, domain, password combination
                lm = LoginManager()
                session_uuid = lm.validate_user_session(username)
                return {'login': True, 'uuid': session_uuid}
        except DoesNotExist:
                return {'login': False, 'uuid': None}

    def validate_user_session(self, username):
        app = current_app
        session_storage = app.config['session_storage']
        if username in session_storage:
            user_session = session_storage[username]
            user_session['uuid'] = str(uuid4()).decode('utf-8')
            user_session['timestamp'] = datetime.now()
        else:
            user_session = dict()
            user_session['uuid'] = str(uuid4()).decode('utf-8')
            user_session['timestamp'] = datetime.now()
        return  user_session['uuid']







