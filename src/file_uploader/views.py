# -*- encoding: utf-8 -*-
'''
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
'''
import os
import json
from flask import Flask, request, redirect, url_for, Blueprint
from werkzeug import secure_filename

file_uploader = Blueprint('file_uploader', __name__, template_folder='')

UPLOAD_FOLDER="/tmp"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@file_uploader.route('/', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        file = request.files['file']
        #print " |file=" + file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print " |filename=" + filename 
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            result = {
                     'result': 'ok',
                     'msg': "file saved"
                     }
            return json.dumps(result)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS