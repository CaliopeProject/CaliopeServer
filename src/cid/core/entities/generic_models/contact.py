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


class CaliopeAddressTypeData(CaliopeEntityData):
    """
    This class allows to mark as home, work, personal etc, an address
    """
    name = StringProperty()
    code = StringProperty()


class CaliopeAddressType(CaliopeEntity):
    entity_data_type = CaliopeAddressTypeData


class CaliopePhoneTypeData(CaliopeEntityData):
    """
    This class allows to mark as home, work, personal, etc and the carrier  a phone number
    """
    name = StringProperty()
    code = StringProperty()
    carrier = StringProperty()


class CaliopePhoneType(CaliopeEntity):
    entity_data_type = CaliopePhoneTypeData


class CaliopeAddressData(CaliopeEntityData):
    address = StringProperty(required=True)
    postal_code = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    populated_center = RelationshipTo(CaliopeMunicipality, 'IS_IN', One)
    type = RelationshipTo(CaliopeAddressType, 'IS_TYPE', ZeroOrOne)


class CaliopeAddress(CaliopeEntity):
    entity_data_type = CaliopeAddressData


class CaliopePhoneData(CaliopeEntityData):
    number = StringProperty()
    area_code = StringProperty()
    type = RelationshipTo(CaliopePhoneType, 'IS_TYPE', ZeroOrOne)


class CaliopePhone(CaliopeEntity):
    entity_data_type = CaliopePhoneData


class CaliopeEmailData(CaliopeEntityData):
    email = StringProperty()
    type = RelationshipTo(CaliopeAddressType, 'IS_TYPE', ZeroOrOne)


class CaliopePhone(CaliopeEntity):
    entity_data_type = CaliopePhoneData


class CaliopeEmail(CaliopeEntity):
    entity_data_type = CaliopeEmailData


class CaliopeContactData(CaliopeEntityData):
    address = RelationshipTo(CaliopeAddress, 'ADDRESS', ZeroOrMore)
    phone_number = RelationshipManager(CaliopePhone, 'PHONE', ZeroOrMore)
    email_address = RelationshipTo(CaliopeEmail, 'EMAIL', ZeroOrMore)


class CaliopeContact(CaliopeEntity):
    entity_data_type = CaliopeContactData
