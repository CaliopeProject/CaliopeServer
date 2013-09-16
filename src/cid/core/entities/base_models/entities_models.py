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

from exceptions import RuntimeError

#neomodel primitives
from neomodel.exception import NotConnected

from neomodel import (RelationshipTo, RelationshipFrom,
                      One, ZeroOrOne, StringProperty, DateTimeProperty)

#Storage
from .caliope_models import *
from cid.core.utils import timeStampGenerator


class CaliopeUser(CaliopeNode):
    __index__ = 'CaliopeStorage'
    username = StringProperty(unique_index=True)
    domainname = StringProperty()
    password = StringProperty()
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    member_of = RelationshipTo('CaliopeGroup', 'IS_MEMBER_OF_GROUP')


class CaliopeGroup(CaliopeNode):
    __index__ = 'CaliopeStorage'
    name = StringProperty(required=True)
    code = StringProperty(unique_index=True)
    members = RelationshipFrom('CaliopeUser', 'IS_MEMBER_OF_GROUP')


class CaliopeEntity(CaliopeNode):
    pass


class CaliopeEntityData(CaliopeNode):
    entity_type = CaliopeEntity

    def __init__(self, *args, **kwargs):
        current = RelationshipFrom(self.entity_type, 'CURRENT', cardinality=ZeroOrOne)
        setattr(self.__class__, 'current', current)
        super(CaliopeEntityData, self).__init__(*args, **kwargs)

    def get_data(self):
        return self._get_node_data()

    def set_data(self, data):
        return self.evolve(**data)


class CaliopeEntity(CaliopeNode):
    entity_data_type = CaliopeEntityData
    context_type = None

    def __new__(cls, *args, **kwargs):
        setattr(cls, "context_type", cls)
        return super(CaliopeEntity, cls).__new__(cls)


    def __init__(self, *args, **kwargs):
        current = RelationshipTo(self.entity_data_type, 'CURRENT', cardinality=One)
        context = RelationshipFrom(self.context_type, 'CONTEXT', cardinality=ZeroOrOne)
        first = RelationshipTo(self.entity_data_type, 'FIRST', cardinality=One)
        setattr(self.__class__, 'context', context)
        setattr(self.__class__, 'current', current)
        setattr(self.__class__, 'first', first)
        super(CaliopeEntity, self).__init__(*args, **kwargs)

    def init_entity_data(self, **data):
        empty_node = self.entity_data_type(**data)
        empty_node.save()
        self.first.connect(empty_node)
        self.current.connect(self.first.single())

    def _get_current(self):
        return self.current.single()

    def _set_current(self, new_current):
        self.current.reconnect(self._get_current(), new_current)

    def set_entity_data(self, **data):
        if 'uuid' in data:
            del data['uuid']
        new_current = self._get_current().set_data(data)
        self._set_current(new_current)
        return self._get_current()

    def get_entity_data(self):
        current_node = self._get_current()
        rv = current_node.get_data()
        for k, v in rv.iteritems():
            if k == 'uuid':
                v = self.uuid
            rv[k] = self._parse_entity_data(v)
        return rv

    def _parse_entity_data(self, v):
        if isinstance(v, list):
            rv = []
            for item in v:
                rv.append(self._parse_entity_data(item))
            return rv
        if isinstance(v, dict):
            rv = {}
            for kr, vr in v.iteritems():
                rv[kr] = self._parse_entity_data(vr)
            return rv
        return {'value': v}

    def get_entity_relationships(self):
        relationships = {k: v for k, v in self._get_current()._class_properties()
                         if isinstance(v, RelationshipDefinition)}
        return relationships
