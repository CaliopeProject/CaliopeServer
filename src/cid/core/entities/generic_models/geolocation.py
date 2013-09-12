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


class CaliopeCountry(CaliopeEntity):
    pass


class CaliopeState(CaliopeEntity):
    pass


class CaliopeMunicipality(CaliopeEntity):
    pass


class CaliopePopulatedCenterType(CaliopeEntity):
    pass


class CaliopePopulatedCenter(CaliopeEntityData):
    pass


class CaliopeCountyData(CaliopeEntityData):
    entity_type = CaliopeCountry

    name = StringProperty()
    code = StringProperty(index=True)
    phone_code = StringProperty()
    currency_code = StringProperty()
    iso_code = StringProperty()


class CaliopeCountry(CaliopeEntity):
    entity_data_type = CaliopeCountyData


class CaliopeStateData(CaliopeEntityData):
    entity_type = CaliopeState
    name = StringProperty()
    code = StringProperty(index=True)
    area_code = StringProperty()
    part_of = RelationshipTo(CaliopeCountry, 'PART_OF', One)


class CaliopeState(CaliopeEntity):
    entity_data_type = CaliopeStateData


class CaliopeMunicipalityData(CaliopeEntityData):
    entity_type = CaliopeMunicipality
    name = StringProperty()
    code = StringProperty(index=True)
    part_of = RelationshipTo(CaliopeState, 'PART_OF', One)


class CaliopeMunicipality(CaliopeEntity):
    entity_data_type = CaliopeMunicipalityData


class CaliopePopulatedCenterTypeData(CaliopeEntityData):
    entity_type = CaliopePopulatedCenterType
    name = StringProperty()
    code = StringProperty(index=True)


class CaliopePopulatedCenterType(CaliopeEntity):
    entity_data_type = CaliopePopulatedCenterTypeData

    def __init__(self, *args, **kwargs):
        super(CaliopePopulatedCenterType, self).__init__(*args, **kwargs)


class CaliopePopulatedCenterData(CaliopeEntityData):
    entity_type = CaliopePopulatedCenter
    name = StringProperty()
    code = StringProperty(index=True)
    type = RelationshipTo(CaliopePopulatedCenterType, 'IS_TYPE', One)
    part_of = RelationshipTo(CaliopeMunicipality, 'PART_OF', One)


class CaliopePopulatedCenter(CaliopeEntity):
    entity_data_type = CaliopePopulatedCenterData

    def __init__(self, *args, **kwargs):
        super(CaliopePopulatedCenter, self).__init__(*args, **kwargs)

