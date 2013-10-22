# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org

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
import redis


class pubsub(object):
    @staticmethod
    def subscribe_with_uuid(uuid):
        if True: #TODO: check uuid
            r = redis.Redis()
            pubsub = r.pubsub()
            pubsub.subscribe('uuid='+uuid)
            return pubsub
        else:
            return None

    @staticmethod
    def unsubscribe_with_uuid(uuid):
        if True: #TODO: check uuid
            r = redis.Redis()
            pubsub = r.pubsub()
            pubsub.unsubscribe('uuid='+uuid)
            return pubsub
        else:
            return None