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


class CaliopeDocumentData(CaliopeEntityData):
    __index__ = 'CaliopeStorage'

    owner = RelationshipFrom(CaliopeUser, 'OWNER', cardinality=One)
    holders = RelationshipFrom(CaliopeUser, 'HOLDER')

    url = StringProperty()
    sha256 = StringProperty()
    insertion_date = DateTimeProperty(default=timeStampGenerator)
    description = StringProperty()
    state = StringProperty()

    def __init__(self, *args, **kwargs):
        super(CaliopeDocumentData, self).__init__(*args, **kwargs)

    def get_document_data(self):
        return self.get_data()

    def set_document_data(self, data):
        return self.set_data(**data)

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


class CaliopeDocument(CaliopeEntity):
    __index__ = 'CaliopeStorage'

    entity_data_type = CaliopeDocumentData

    def __init__(self, *args, **kwargs):
        super(CaliopeDocument, self).__init__(*args, **kwargs)

    def set_owner(self, owner):
        self._get_current().set_owner(owner)

    def set_holder(self, holder, **props):
        self._get_current().add_holder(holder, **props)

    def remove_holders(self):
        current_node = self._get_current()
        holders_nodes = current_node.holders.all()
        for holder in holders_nodes:
            current_node.remove_holder(holder)

    def get_entity_data(self):
        #: Added due to extra logic of holders
        rv = super(CaliopeDocument, self).get_entity_data()
        current_node = self._get_current()
        holders_nodes = current_node.holders.all()
        holders = [holder_node.username for holder_node in holders_nodes]
        rv['holders'] = {'value': holders}
        return rv
