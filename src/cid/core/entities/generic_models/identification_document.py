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

from ..base_models.entities_models import *
from .geolocation import CaliopeMunicipality


class CaliopeIdentificationDocumentType(CaliopeEntity):
    pass


class CaliopeIdentificationDocument(CaliopeEntity):
    pass


class CaliopeIdentificationDocumentTypeData(CaliopeEntityData):
    entity_type = CaliopeIdentificationDocumentType
    name = StringProperty()
    code = StringProperty()
    maximum_length = IntegerProperty()
    minimum_length = IntegerProperty


class CaliopeIdentificationDocumentType(CaliopeEntity):
    entity_data_type = CaliopeIdentificationDocumentTypeData


class CaliopeIdentificationDocumentData(CaliopeEntityData):
    entity_type = CaliopeIdentificationDocument
    number = StringProperty()
    issue_date = DateTimeProperty()
    type = RelationshipTo(CaliopeIdentificationDocumentType, 'IS_TYPE', One)
    issue_location = RelationshipTo(CaliopeMunicipality, 'ISSUED_AT', ZeroOrOne)


class CaliopeIdentificationDocument(CaliopeEntity):
    entity_data_type = CaliopeIdentificationDocumentData

