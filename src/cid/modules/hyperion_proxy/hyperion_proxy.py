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
import requests

#flask
from flask.globals import current_app
from flask import (session, request, Blueprint)

import requests

hyperion_proxy = Blueprint('hyperion_proxy', __name__, template_folder='')


@hyperion_proxy.route('/<path:filename>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_file(filename):
    print filename

    r = requests.get(
            'http://localhost:9020/d/' + filename)
    return r.content

'''
    params = ""
    for k in request.values.keys():
        print k + " " + request.values[k]
        params = params + '&' + k + '=' + request.values[k]
    if "wfs" in filename:
        r = requests.post('http://siim2.infometrika.net:8080/geoserver/mtv_gis/ows?', data=request.data)
    elif "wms" in filename:
        r = requests.get('http://siim2.infometrika.net:8080/geoserver/mtv_gis/wms?' + params)
    else:
        r = requests.get(
            'http://mapas.catastrobogota.gov.co/arcgiswsh/Mapa_Referencia/Mapa_referencia/MapServer/WMSServer?' + params)
    return r.content

'''

