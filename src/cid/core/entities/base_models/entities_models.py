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
    __entity_type__ = CaliopeEntity

    def __new__(cls, *args, **kwargs):
        __entity_type__ = kwargs['__entity_type__'] if '__entity_type__' in kwargs else cls.__entity_type__
        setattr(cls, '__entity_type__', __entity_type__)
        current = RelationshipFrom(__entity_type__, 'CURRENT', cardinality=One)
        setattr(cls, 'current', current)
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
    __entity_data_type__ = CaliopeEntityData
    __context_type__ = None

    def __new__(cls, *args, **kwargs):

        if '__entity_data_type__' in kwargs:
            __entity_data_type__ = kwargs['__entity_data_type__']
            del kwargs['__entity_data_type__']
        else:
            __entity_data_type__ = cls.__entity_data_type__

        if '__context_type__' in kwargs:
            __context_type__ = kwargs['__context_type__']
            del kwargs['__context_type__']
        elif cls.__context_type__ is not None:
            __context_type__ = cls.__context_type__
        else:
            __context_type__ = cls

        setattr(cls, '__entity_data_type__', __entity_data_type__)
        setattr(cls, '__context_type__', __context_type__)
        current = RelationshipTo(__entity_data_type__, 'CURRENT', cardinality=ZeroOrOne)
        setattr(cls, 'current', current)
        context = RelationshipFrom(__context_type__, 'CONTEXT', cardinality=ZeroOrOne)
        setattr(cls, 'context', context)
        return super(CaliopeEntity, cls).__new__(cls, *args, **kwargs)


    def __init__(self, *args, **kwargs):
        super(CaliopeEntity, self).__init__(*args, **kwargs)
        self.init_entity_data()

    def init_entity_data(self, *args, **kwargs):
        self.__entity_data__ = self.__entity_data_type__(args, kwargs)

    def _get_current(self):
        if self.__node__ is None:
            return self.__entity_data__
        else:
            return self.current.single()

    def _set_current(self, new_current):
        if self._get_current() is not None:
            self.current.reconnect(self._get_current(), new_current)
        else:
            self.current.connect(new_current)

    def set_entity_data(self, *args, **kwargs):
        if 'uuid' in kwargs:
            del kwargs['uuid']
        if self.__node__ is None:
            self.save()
        current = self._get_current()
        if current is None:
            self.__entity_data__ = self.__entity_data_type__(args, kwargs)
            current = self.__entity_data__
            #: When the set_data, call evolve, the new node is saved before return
        new_current = current.set_data(kwargs)
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
        for k, v in self.__entity_data_type__._get_class_relationships():
            if isinstance(v, RelationshipDefinition):
                rv[k] = v
        return rv

    def _parse_entity_relationships(self, k, v):
        rv = {}
        if k == "current":
            return rv
        current_node = self._get_current()
        if getattr(current_node, '__node__') is not None:
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
        else:
            rel = getattr(current_node, k)
            rv['direction'] = rel.definition['direction']
            target = []
            rel_dct = {}
            for t_name, t_class in rel.target_map.items():
                rel_dct['entity'] = repr(t_class)
                rel_dct['properties'] = {}
                rel_dct['entity_data'] = {}
                target.append(rel_dct)
            rv['target'] = target
        return rv



