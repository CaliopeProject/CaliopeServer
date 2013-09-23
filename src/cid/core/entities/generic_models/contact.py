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


class CaliopeAddressType(CaliopeEntity):
    pass


class CaliopePhoneType(CaliopeEntity):
    pass


class CaliopeAddress(CaliopeEntity):
    pass


class CaliopePhone(CaliopeEntity):
    pass


class CaliopeEmail(CaliopeEntity):
    pass


class CaliopeContact(CaliopeEntity):
    pass


class CaliopeAddressTypeData(CaliopeEntityData):
    """
    This class allows to mark as home, work, personal etc, an address
    """
    __entity_type__ = CaliopeAddressType
    name = StringProperty()
    code = StringProperty()


class CaliopeAddressType(CaliopeEntity):
    __entity_data_type__ = CaliopeAddressTypeData


class CaliopePhoneTypeData(CaliopeEntityData):
    """
    This class allows to mark as home, work, personal, etc and the carrier  a phone number
    """
    __entity_type__ = CaliopePhoneType
    name = StringProperty()
    code = StringProperty()
    carrier = StringProperty()


class CaliopePhoneType(CaliopeEntity):
    __entity_data_type__ = CaliopePhoneTypeData


class CaliopeAddressData(CaliopeEntityData):
    __entity_type__ = CaliopeAddress
    address = StringProperty(required=True)
    postal_code = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    populated_center = RelationshipTo(CaliopeMunicipality, 'IS_IN', One)
    type = RelationshipTo(CaliopeAddressType, 'IS_TYPE', ZeroOrOne)


class CaliopeAddress(CaliopeEntity):
    __entity_data_type__ = CaliopeAddressData


class CaliopePhoneData(CaliopeEntityData):
    __entity_type__ = CaliopePhone
    number = StringProperty()
    area_code = StringProperty()
    type = RelationshipTo(CaliopePhoneType, 'IS_TYPE', ZeroOrOne)


class CaliopePhone(CaliopeEntity):
    __entity_data_type__ = CaliopePhoneData


class CaliopeEmailData(CaliopeEntityData):
    __entity_type__ = CaliopeEmail
    email = StringProperty()
    type = RelationshipTo(CaliopeAddressType, 'IS_TYPE', ZeroOrOne)


class CaliopeEmail(CaliopeEntity):
    __entity_data_type__ = CaliopeEmailData


class CaliopeContactData(CaliopeEntityData):
    __entity_type__ = CaliopeContact
    address = RelationshipTo(CaliopeAddress, 'ADDRESS', ZeroOrMore)
    phone_number = RelationshipTo(CaliopePhone, 'PHONE', ZeroOrMore)
    email_address = RelationshipTo(CaliopeEmail, 'EMAIL', ZeroOrMore)


class CaliopeContact(CaliopeEntity):
    __entity_data_type__ = CaliopeContactData
