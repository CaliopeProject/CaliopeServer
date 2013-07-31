# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

SIIM Models are the data definition of SIIM2 Framework
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
#neomodel primitives
from neomodel.properties import (Property,
                                 DateTimeProperty,
                                 IntegerProperty,
                                 StringProperty)

#CaliopeStorage
from odisea.CaliopeStorage import CaliopeNode

from urlparse import urlparse

import hashlib # For SHA-256 Encoding


#urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
#ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html', params='', query='', fragment='')

class DocumentNode(CaliopeNode):
    url = StringProperty()
    sha256 = StringProperty()
    insertion_date = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    description = StringProperty()
    state = StringProperty()

    def add_to_repo(parent_uuid, url, description):
        u=urlparse(url)
        if u.scheme=='file':
            sha256 = get_sha256(u.path)
        save()
        
    @staticmethod
    def get_sha256(file_name):
        with open(file_name) as f:
            m = hashlib.sha256()
            m.update(f.read())
            return m.hexdigest()
