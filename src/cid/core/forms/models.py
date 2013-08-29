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

#system, and standard library

#neomodel primitives
from neomodel.properties import (Property,
                                 DateTimeProperty,
                                 FloatProperty,
                                 IntegerProperty,
                                 StringProperty)

from neomodel import (StructuredNode, RelationshipTo, RelationshipFrom,
        Relationship, One)

#CaliopeStorage
from cid.core.entities import CaliopeNode, CaliopeUser


class SIIMFormData(CaliopeNode):

    def get_form_data(self):
        return self._get_node_data()

    def set_form_data(self, data):
        return self.evolve(**data)



class SIIMForm(CaliopeNode):
    form_id = StringProperty(index=True)
    owner  = RelationshipFrom(CaliopeUser, 'OWNER', cardinality=One)
    holder = RelationshipFrom(CaliopeUser, 'HOLDER')

    def __init__(self, *args, **kwargs):
        super(SIIMForm, self).__init__(*args, **kwargs)

    def get_form_data(self):
        return self._get_node_data()

    def set_form_data(self, data):
        if 'uuid' in data:
            del data['uuid']
        return self.evolve(**data)




