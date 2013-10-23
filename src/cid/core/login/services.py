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
import os
from uuid import uuid4
from functools import wraps

#CaliopeStorage
from neomodel import DoesNotExist

from tinyrpc.protocols.jsonrpc import JSONRPCInternalError
from tinyrpc.dispatch import public
from flask import current_app, g
from cid.core.entities.base_models.entities_models import CaliopeUser
from cid.utils.thumbnails import get_thumbnail
from cid.core.pubsub import pubsub_subscribe_uuid


prefix_session_manager = "prefix_session_manager_"


class LoginManager(object):
    @staticmethod
    @public
    def authenticate(username, password, domain=None):
        try:
            #: TODO: Add support to domain
            userNode = CaliopeUser.index.get(username=username)
            if userNode.password == password:
                session_uuid = str(uuid4()).decode('utf-8')

                g.connection_thread_pool_id[g.connection_thread_id] = session_uuid
                current_app.storekv.put(prefix_session_manager + session_uuid, username)
                pubsub_subscribe_uuid(userNode.uuid)
                return {
                    'login': True,
                    'session_uuid': {'value': session_uuid},
                    'user_uuid': {'value': userNode.uuid},
                    'user': {'value': username},
                    "first_name": {'value': userNode.first_name},
                    "last_name": {'value': userNode.last_name},
                    "image": get_thumbnail(os.path.join(current_app.config['STATIC_PATH'], userNode.avatar))
                }
            else:
                return {'login': False}
        except DoesNotExist:
            return {'login': False}
        except Exception as e:
            raise JSONRPCInternalError(e)


    @staticmethod
    @public
    def authenticate_with_uuid(session_uuid, domain=None):
        if session_uuid is not None:
            if current_app.storekv.__contains__(prefix_session_manager + session_uuid):
                try:
                    username = current_app.storekv.get(prefix_session_manager + session_uuid)
                    g.connection_thread_pool_id[g.connection_thread_id] = session_uuid
                    userNode = CaliopeUser.index.get(username=username)
                    pubsub_subscribe_uuid(userNode.uuid)
                    return {'login': True,
                            'session_uuid': {'value': session_uuid},
                            'user_uuid': {'value': userNode.uuid},
                            'user': {'value': username},
                            "first_name": {'value': userNode.first_name},
                            "last_name": {'value': userNode.last_name},
                            "image": get_thumbnail(
                                os.path.join(current_app.config['STATIC_PATH'], userNode.avatar))
                    }
                except Exception as e:
                    raise JSONRPCInternalError(e)
            #: if not returned is not a  valid session
        return {'login': False}


    @staticmethod
    @public
    def logout(uuid):
        if current_app.storekv.__contains__(prefix_session_manager + uuid):
            username = current_app.storekv.delete(prefix_session_manager + uuid)
        return {'logout': True, 'uuid': uuid}

    @staticmethod
    def check():
        #!!!!!!!!!!!!!!!!!!!!thread safe untested!!!!!!!!!!!!!!!!!!
        if g.connection_thread_id in g.connection_thread_pool_id:
            key = prefix_session_manager + g.connection_thread_pool_id[g.connection_thread_id]
            if current_app.storekv.__contains__(key):
                return True
        return False

    @staticmethod
    def check_with_uuid(uuid):
        if current_app.storekv.__contains__(prefix_session_manager + uuid):
            return True
        else:
            return False

    @staticmethod
    def get_user():
        #!!!!!!!!!!!!!!!!!!!!thread safe untested!!!!!!!!!!!!!!!!!!
        if g.connection_thread_id in g.connection_thread_pool_id:
            key = prefix_session_manager + g.connection_thread_pool_id[g.connection_thread_id]
            if current_app.storekv.__contains__(key):
                return current_app.storekv.get(key)
        return None


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

