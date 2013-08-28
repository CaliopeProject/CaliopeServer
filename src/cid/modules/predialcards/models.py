# -*- encoding: utf-8 -*-
"""
@authors: Nelson Daniel Ochoa ndaniel8a@gmail.com

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
from neomodel.properties import ( DateTimeProperty,
                                  StringProperty, IntegerProperty, JSONProperty)

#Caliope Entities
from cid.core.entities import CaliopeEntityData, CaliopeEntity


class PredialCardData(CaliopeEntityData):
    __index__ = 'CaliopeStorage'

    predial_identifier = StringProperty()
    chip = StringProperty()
    # Change for Entity Address
    address = JSONProperty()
    owner_type = StringProperty() #Propietario o poseedor
    owner_data = JSONProperty()


    def __init__(self, *args, **kwargs):
        super(PredialCardData, self).__init__(*args, **kwargs)

    def get_predial_card_data(self):
        return self._get_node_data()

    def set_predial__card_data(self, data):
        return self.evolve(**data)


class PredialCardEntity(CaliopeEntity):
    __index__ = 'CaliopeStorage'

    entity_data_type = PredialCardData

    def __init__(self, *args, **kwargs):
        super(PredialCardEntity, self).__init__(*args, **kwargs)





