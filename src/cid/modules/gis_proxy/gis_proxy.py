# -*- encoding: utf-8 -*-
"""
Created on 23/07/2013

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
from flask.globals import current_app
from flask import (session, request, Blueprint)
 
import requests

gis_proxy = Blueprint('gis_proxy', __name__, template_folder='')

@gis_proxy.route('/<path:filename>', methods=['GET', 'POST', 'OPTIONS'])
def catastrobogota(filename):    
    params=""
    for k in request.values.keys():
        print k + " " + request.values[k]
        params = params+'&'+k+'='+request.values[k]

    r = requests.get('http://mapas.catastrobogota.gov.co/arcgiswsh/Mapa_Referencia/Mapa_referencia/MapServer/WMSServer?'+params)
    return r.content

