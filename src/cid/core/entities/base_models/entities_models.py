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
                      One )

#Storage
from caliope_models import *


class CaliopeEntityData(CaliopeNode):
    __index__ = 'CaliopeStorage'

    owner = RelationshipFrom(CaliopeUser, 'OWNER', cardinality=One)
    holders = RelationshipFrom(CaliopeUser, 'HOLDER')
    attachments = RelationshipTo(CaliopeDocument, 'ATTACHMENT')

    def get_form_data(self):
        return self._get_node_data()

    def set_form_data(self, data):
        return self.evolve(**data)

    def set_owner(self, owner_node):
        if isinstance(owner_node, CaliopeUser):
            if self.owner.count() >= 1:
                self.owner.disconnect(self.owner.single())
            self.owner.connect(owner_node)
        else:
            raise RuntimeError('No valid owner class')

    def add_holder(self, holder_node, **props):
        if isinstance(holder_node, CaliopeUser):
            self.holders.connect(holder_node, **props)
        else:
            raise RuntimeError('No valid holder class')

    def remove_holder(self, holder_node):
        if isinstance(holder_node, CaliopeUser):
            if self.holders.is_connected(holder_node):
                self.holders.disconnect(holder_node)
            else:
                raise NotConnected('User is not a valid holder')
        else:
            raise RuntimeError('No valid holder class')

    def add_attachment(self, attachment):
        if isinstance(attachment, CaliopeDocument):
            self.attachments.connect(attachment)
        else:
            raise RuntimeError('No valid attachment class')

    def remove_attachment(self, attachment):
        if isinstance(attachment, CaliopeDocument):
            if self.attachments.is_connected(attachment):
                self.attachments.disconnect(attachment)
            else:
                raise NotConnected('Attachment is not valid')
        else:
            raise RuntimeError('Not valid attachment class')


class CaliopeEntity(CaliopeNode):

    __index__ = 'CaliopeStorage'

    entity_data_type = CaliopeEntityData

    def __init__(self, *args, **kwargs):
        current = RelationshipTo(self.entity_data_type, 'CURRENT', cardinality=One)
        first = RelationshipTo(self.entity_data_type, 'FIRST', cardinality=One)
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
        new_current = self._get_current().evolve(**data)
        self._set_current(new_current)
        return self._get_current()

    def set_owner(self, owner):
        self._get_current().set_owner(owner)

    def set_holder(self, holder, **props):
        self._get_current().add_holder(holder, **props)

    def get_entity_data(self):
        current_node = self._get_current()
        rv = current_node._get_node_data()
        for k, v in rv.iteritems():
            if k == 'uuid':
                v = self.uuid
            rv[k] = self._parse_entity_data(v)

        holders_nodes = current_node.holders.all()
        holders = [holder_node.username for holder_node in holders_nodes]
        #TODO: Why is this hardcored here?
        rv['ente_asignado'] = {'value': holders}
        return rv

    def _parse_entity_data(self, v):
        if isinstance(v, datetime):
            v = unicode(v)
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
