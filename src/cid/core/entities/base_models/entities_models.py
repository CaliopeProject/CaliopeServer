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
from datetime import datetime

#neomodel primitives
from neomodel.exception import NotConnected

from .versioned_node import (RelationshipTo,
                             RelationshipFrom,
                             StringProperty,
                             IntegerProperty,
                             CaliopeJSONProperty,
                             FloatProperty,
                             DateTimeProperty,
                             One,
                             ZeroOrOne,
                             ZeroOrMore
                             )

from .versioned_node import VersionedNode, timeStampGenerator


class CaliopeContext(VersionedNode):
    name = StringProperty()
    elements = RelationshipFrom(VersionedNode, "CONTEXT", ZeroOrMore)


class CaliopeUser(VersionedNode):
    username = StringProperty(unique_index=True)
    domainname = StringProperty()
    password = StringProperty()
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    avatar = StringProperty()
    member_of = RelationshipTo('CaliopeGroup', 'IS_MEMBER_OF_GROUP')


class CaliopeGroup(VersionedNode):
    name = StringProperty(required=True)
    code = StringProperty(unique_index=True)
    members = RelationshipFrom('CaliopeUser', 'IS_MEMBER_OF_GROUP')


class CaliopeTransaction(VersionedNode):
    uuid_object= StringProperty(index=True)
    uuid_agent = StringProperty(index=True)
    uuid_session = StringProperty(index=True)
    change_type = StringProperty()
    change_value = CaliopeJSONProperty()


