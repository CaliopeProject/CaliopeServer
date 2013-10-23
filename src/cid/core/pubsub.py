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
from hotqueue import HotQueue

from flask import g

import json


def pubsub_subscribe_uuid(uuid):
    if True: #TODO: check uuid
        queue = HotQueue("connection_thread_id_queue=" + str(g.connection_thread_id))
        msg = {'cmd': 'subscribe', 'params': str(uuid)}
        queue.put(json.dumps(msg))
        return msg
    else:
        return None

def pubsub_unsubscribe_uuid(uuid):
    if True: #TODO: check uuid
        queue = HotQueue("connection_thread_id_queue=" + str(g.connection_thread_id))
        msg = {'cmd': 'unsubscribe', 'params': str(uuid)}
        queue.put(json.dumps(msg))
        return msg
    else:
        return None