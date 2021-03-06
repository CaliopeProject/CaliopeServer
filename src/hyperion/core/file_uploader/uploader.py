# -*- encoding: utf-8 -*-
"""
Created on 27/06/2013

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
import json
import uuid
from werkzeug.utils import secure_filename

#flask
from flask.globals import current_app
from flask import ( request, Blueprint)

from cid.core.login import LoginManager
from cid.utils.thumbnails import get_thumbnail
from cid.utils.fileUtils import human_readable_size
from cid.core.forms import FormManager
from cid.utils.crossdomain import crossdomain
from cid.core.entities import CaliopeServices
import mimetypes

import urlparse


file_uploader = Blueprint('file_uploader', __name__, template_folder='')

#: TODO: This items should be came from configuration files.
UPLOAD_FOLDER = "/tmp"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def local_document_url(parent_uuid, path, description):
    netloc = params = query = fragment = ''
    scheme = 'localstorage'
    url = urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
    return url


@file_uploader.route('/', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin=['*'], headers=['Content-Type', 'Authorization', 'Content-Length', 'X-Requested-With'],
             methods=['POST', 'GET', 'PUT', 'HEAD', 'OPTIONS'])
def uploader():
    if request.method == 'POST':
        #print request.form['id']
        #print str(request.form.viewitems())
        attachment_params = {k: v[0] for k, v in [x for x in request.form.viewitems()]}
        if 'session_uuid' in request.form:
            if LoginManager().check_with_uuid(request.form['session_uuid']):
                print "OK"
            else:
                return "unrecheable"
        else:
            return "unrecheable"

        app = current_app
        storage_setup = app.config['storage']

        if 'local' in storage_setup and 'absolut_path' in storage_setup['local']:
            UPLOAD_FOLDER = storage_setup['local']['absolut_path']

        if 'local' in storage_setup and 'allowed_extensions' in storage_setup['local']:
            ALLOWED_EXTENSIONS = storage_setup['local']['allowed_extensions']

        rv = []
        for uploaded_file in request.files.getlist('files[]'):
            filename = secure_filename(uploaded_file.filename)
            if uploaded_file and allowed_file(uploaded_file.filename, ALLOWED_EXTENSIONS):
                model = FormManager().get_empty_model('CaliopeDocument', data=True)
                idfile = model['data']['uuid']['value']
                uploaded_file.save(os.path.join(UPLOAD_FOLDER, idfile))

                mimetype = mimetypes.guess_type(filename)[0]
                if mimetype is None:
                    mimetype = 'application/octet-stream'

                CaliopeServices().update_field(idfile, 'mimetype', mimetype)
                CaliopeServices().update_field(idfile, 'filename', filename)
                CaliopeServices().update_field(idfile, 'url', local_document_url('', idfile, ''))
                #DocumentProcess().enqueue(doc)

                result = {
                    'result': 'ok',
                    'name': filename,
                    'size': human_readable_size(uploaded_file.tell()),
                    'id': idfile,
                    'thumbnail': get_thumbnail(os.path.join(UPLOAD_FOLDER, idfile), mimetype=mimetype,
                                               field_name='data')
                }
                CaliopeServices().update_relationship(attachment_params['uuid'], attachment_params['field'], idfile)
            else:
                result = {
                    'result': 'error',
                    'name': filename
                }
            rv.append(result);

        return json.dumps(rv)
    return "unrecheable"


def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
