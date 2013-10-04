# -*- coding: utf-8 -*-
"""
    cid.core.entities.model
    ~~~~~~~~~~~~~~

    :author: Nelson Castillo <nelsoneci@gmail.com>
    :copyright: (c) 2013 por Fundación CorreLibre
    :license:  GNU AFFERO GENERAL PUBLIC LICENSE

SIIM2 Storage is the base of SIIM2's Framework
Copyright (C) 2013  Fundación Correlibre

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

from neomodel import *
from neomodel.contrib import SemiStructuredNode
from neomodel import RelationshipDefinition
from py2neo import neo4j

from cid.core.utils import uuidGenerator, timeStampGenerator

class VersionedNode(SemiStructuredNode):
    """
    :class: VersionedNode
    """

    __index__ = 'CaliopeStorage'

    uuid = StringProperty(default = uuidGenerator, unique_index = True)

    parent_uuid  = StringProperty(default = '')

    #: All timestamps should be in UTC using pytz.utc
    timestamp = DateTimeProperty(default = timeStampGenerator)

    def _attributes_to_save(self):
        return [a for a in self.__dict__ if a[:1] != '_' and a != 'timestamp']

    def _should_save_history(self, stored_node):
        for field in set(self._attributes_to_save() +
                         stored_node._attributes_to_save()):
            # Versioned nodes have different fields, so they are different.
           if not hasattr(stored_node, field) or not hasattr(self, field):
               return True
           # A field has a different value.
	   if getattr(self, field) != getattr(stored_node, field):
               return True
        # Versioned nodes have the save fields and field values.
        return False

    def save(self, skip_difference = False):
        if not skip_difference:
            stored_node = None
            try:
                stored_node = self.__class__.index.get(uuid = self.uuid)
            except:
                pass
            if stored_node and self._should_save_history(stored_node):
                # The following operations need to be atomic.
                # 1. Create a copy of the stored node and save it.
                copy = stored_node.__class__()
	        for field in stored_node._attributes_to_save():
                    setattr(copy, field, getattr(stored_node, field))
                copy.uuid = uuidGenerator() # TODO(nel): This is wrong. Fix.
                copy.save(skip_difference = True)
                self.parent_uuid = copy.uuid
        super(VersionedNode, self).save()

    def __init__(self, *args, **kwargs):
        super(VersionedNode, self).__init__(*args, **kwargs)
