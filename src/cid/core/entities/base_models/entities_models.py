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

    def __new__(cls, *args, **kwargs):
        entity_type = kwargs['entity_type'] if 'entity_type' in kwargs else cls.entity_type
        setattr(cls, 'entity_type', entity_type)
        return super(CaliopeEntityData, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        #current = RelationshipFrom(self.entity_type, 'CURRENT', cardinality=ZeroOrOne)
        #setattr(self.__class__, 'current', current)
        super(CaliopeEntityData, self).__init__(*args, **kwargs)

    def get_data(self):
        if self.__node__ is None:
            return self._get_inst_data()
        return self._get_node_data()

    def set_data(self, data):
        return self.evolve(**data)


class CaliopeEntity(CaliopeNode):
    entity_data_type = CaliopeEntityData
    context_type = None

    def __new__(cls, *args, **kwargs):

        if 'entity_data_type' in kwargs:
            entity_data_type = kwargs['entity_data_type']
            del kwargs['entity_data_type']
        else:
            entity_data_type = cls.entity_data_type

        if 'context_type' in kwargs:
            context_type = kwargs['context_type']
            del kwargs['context_type']
        elif cls.context_type is not None:
            context_type = cls.context_type
        else:
            context_type = cls

        setattr(cls, 'entity_data_type', entity_data_type)
        setattr(cls, 'context_type', context_type)
        current = RelationshipTo(entity_data_type, 'CURRENT', cardinality=ZeroOrOne)
        setattr(cls, 'current', current)
        context = RelationshipFrom(context_type, 'CONTEXT', cardinality=ZeroOrOne)
        setattr(cls, 'context', context)
        return super(CaliopeEntity, cls).__new__(cls, *args, **kwargs)


    def __init__(self, *args, **kwargs):
        super(CaliopeEntity, self).__init__(*args, **kwargs)
        self.init_entity_data()

    def init_entity_data(self, *args, **kwargs):
        self.empty_entity_data = self.entity_data_type(args, kwargs)

    def _get_current(self):
        if self.__node__ is None:
            return self.empty_entity_data
        else:
            return self.current.single()

    def _set_current(self, new_current):
        self.current.reconnect(self._get_current(), new_current)

    def set_entity_data(self, **data):
        if 'uuid' in data:
            del data['uuid']
        new_current = self._get_current().set_data(data)
        self._set_current(new_current)
        return self._get_current()

    def serialize(self):
        rv = self.get_entity_data()
        for k, v in self.get_entity_relationships().items():
            rv[k] = self._parse_entity_relationships(k, v)
        return rv

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
        rv = {}
        for k, v in self.entity_data_type._get_class_relationships():
            if isinstance(v, RelationshipDefinition):
                rv[k] = v
        return rv

    def _parse_entity_relationships(self, k, v):
        rv = {}
        current_node = self._get_current()
        rel = getattr(current_node, k)
        rv['direction'] = rel.definition['direction']
        target = []
        for t in rel.all():
            rel_dct = {}
            rel_inst = rel.relationship(t)
            rel_dct['entity'] = repr(t.__class__)
            rel_dct['properties'] = {k: v for k, v in rel_inst._properties.items()}
            rel_dct['entity_data'] = {'uuid': t.uuid}
            target.append(rel_dct)
        rv['target'] = target
        return rv



