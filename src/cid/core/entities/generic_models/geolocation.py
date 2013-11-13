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


class CaliopeCounty(VersionedNode):

    name = StringProperty()
    code = StringProperty(index=True)
    phone_code = StringProperty()
    currency_code = StringProperty()
    iso_code = StringProperty()

class CaliopeState(VersionedNode):
    name = StringProperty()
    code = StringProperty(index=True)
    area_code = StringProperty()
    part_of = RelationshipTo(VersionedNode, 'PART_OF', One)

class CaliopeMunicipality(VersionedNode):
    name = StringProperty()
    code = StringProperty(index=True)
    part_of = RelationshipTo(CaliopeState, 'PART_OF', One)

class CaliopePopulatedCenterType(VersionedNode):
    name = StringProperty()
    code = StringProperty(index=True)

class CaliopePopulatedCenter(VersionedNode):
    name = StringProperty()
    code = StringProperty(index=True)
    type = RelationshipTo(CaliopePopulatedCenterType, 'IS_TYPE', One)
    part_of = RelationshipTo(CaliopeMunicipality, 'PART_OF', One)



