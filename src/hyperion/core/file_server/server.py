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
import json
import uuid

#flask
from werkzeug import secure_filename
from flask.globals import current_app
from flask import ( request, Blueprint)

from cid.core.login import LoginManager

file_server = Blueprint('file_server', __name__, template_folder='')


@file_server.route('/', methods=['GET', 'POST'])
def server():
    pass