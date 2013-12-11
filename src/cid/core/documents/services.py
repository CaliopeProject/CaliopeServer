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

from flask.globals import current_app

from tinyrpc.dispatch import public

from flask import current_app

from cid.core.pubsub import PubSub

from cid.core.entities import (VersionedNode, CaliopeDocument,
                               CaliopeServices)

from cid.utils.fileUtils import human_readable_size
from cid.utils.thumbnails import get_thumbnail


class DocumentServices(CaliopeServices):
    def __init__(self, *args, **kwargs):
        super(DocumentServices, self).__init__(*args, **kwargs)


    @classmethod
    @public("getData")
    def get_data(cls, uuids):
        rv = list()

        storage_setup = current_app.config['storage']

        if 'local' in storage_setup and 'absolut_path' in storage_setup['local']:
            STORAGE = storage_setup['local']['absolut_path']

        for uuid in uuids:
            vnode = CaliopeDocument.pull(uuid)
            filename = os.path.join(STORAGE, vnode.uuid)
            size = os.stat(filename).st_size
            data = {
                'result': 'ok',
                'name': vnode.filename,
                'size': human_readable_size(size),
                'mime': vnode.mimetype,
                'id': vnode.uuid,
                'thumbnail': get_thumbnail(filename, field_name='data', mimetype=vnode.mimetype)
            }
            rv.append(data)

        return rv
