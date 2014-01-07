# -*- encoding: utf-8 -*-
"""
Created on 13/09/2013

@author: Andrés Felipe Calderón andres.calderon@correlibre.org
@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Server is part of Caliope's Framework
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
"""
#system, and standard library

import os
import magic


#flask
from werkzeug import secure_filename
from flask.globals import current_app
from flask import ( request, Blueprint)

#flask
from flask import (Flask,current_app,request)
from flask.helpers import safe_join
from werkzeug.wsgi import wrap_file
from werkzeug.datastructures import Headers

from cid.utils.crossdomain import crossdomain

from cid.core.entities import CaliopeDocument
from cid.core.login import LoginManager

file_server = Blueprint('file_server', __name__, template_folder='')


@file_server.route('/<path:filename>', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin=['*'], headers=['Content-Type', 'Authorization', 'Content-Length', 'X-Requested-With'],
             methods=['POST', 'GET', 'PUT', 'HEAD', 'OPTIONS'])
def server(filename):
    print filename

    storage_setup = current_app.config['storage']


    if 'local' in storage_setup and 'absolut_path' in storage_setup['local']:
            STORAGE = storage_setup['local']['absolut_path']
    else:
            STORAGE = '.'

    filename = filename.split('.')[0]

    node = CaliopeDocument.pull(filename)
    file = open(os.path.join(STORAGE, filename), 'rb')
    data = wrap_file(request.environ, file)
    headers = Headers()

    try:
        mimetype  = node.mimetype
    except:
        mimetype = 'application/octet-stream'

    rv = current_app.response_class(data, mimetype=mimetype, headers=headers,
                                        direct_passthrough=False)
    return rv