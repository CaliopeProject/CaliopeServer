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

from cid.core.entities.base_models.entities_models import *


class CaliopeDocument(VersionedNode):
    owner = RelationshipFrom(CaliopeUser, 'OWNER', cardinality=One)
    holders = RelationshipFrom(CaliopeUser, 'HOLDER')

    url = StringProperty()
    sha256 = StringProperty()
    insertion_date = DateTimeProperty(default=timeStampGenerator)
    description = StringProperty()
    state = StringProperty()


class ContentDocument(VersionedNode):
    __index__ = 'ContentFulltext'
    content = StringProperty(index=True)
    document = RelationshipFrom(CaliopeDocument, 'CONTENT_OF', cardinality=One)
