# -*- coding: utf-8 -*-
"""
    cid.core.entities.base_models
    ~~~~~~~~~~~~~~

    Este módulo contiene la clase CaliopeNode, que es el elemento atómico
    de la arquitectura de almancenamiento. Toda la información del sistema
    es contenida en elementos que heredan de  CaliopeNode.

    :author: Sebastián Ortiz <neoecos@gmail.com>
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

#from cid.core.utils import uuidGenerator, timeStampGenerator
# TODO(nel): Remove the following imports and uncomment the previous line.
import uuid
import hashlib
from datetime import datetime
from pytz import utc

def uuidGenerator():
    return str(uuid.uuid4()).decode('utf-8')
#: All timestamps should be in UTC
def timeStampGenerator():
    return datetime.now(utc)

class VersionedNode(SemiStructuredNode):
    """
    :class: VersionedNode
    """
    __index__ = 'CaliopeStorage'

    uuid = StringProperty(default = uuidGenerator, unique_index = True)

    parent_uuid  = StringProperty(default = '')

    #: All timestamps should be in UTC using pytz.utc
    timestamp = DateTimeProperty(default = timeStampGenerator)


    def attributes_to_save(self):
      ret = []
      for field in self.__dict__:
        # Timestamp issue.
        if field[:1] != '_' and field != 'timestamp':
          ret.append(field)
      return ret

    def should_save_history(self, stored_node):
            print 'should have history?'
	    for field in self.attributes_to_save():
              # TODO(nel): In some cases the new objec will have less/more fields than the old one. Fix.
	      if getattr(self, field) != getattr(stored_node, field):
                # TODO(nel): Delete this code.
	        print field, 'is different'
	        print 'Now',  getattr(self, field)
	        print 'Before', getattr(stored_node, field)
                return True
            return False

    def save(self, skip_difference = False):
        if not skip_difference:
          stored_node = None
          try:
            stored_node = self.__class__.index.get(uuid = self.uuid)
          except:
            pass
          if stored_node and self.should_save_history(stored_node):
            print 'should save history'
            # The following operations need to be atomic.
            # 1. Create a copy of the stored node and save it.
            copy = stored_node.__class__()
	    for field in stored_node.attributes_to_save():
              setattr(copy, field, getattr(stored_node, field))
            copy.uuid = uuidGenerator() # TODO(nel): This is wrong. Fix.
            copy.save(skip_difference = True)
            self.parent_uuid = copy.uuid
        super(VersionedNode, self).save()

    def __init__(self, *args, **kwargs):
        super(VersionedNode, self).__init__(*args, **kwargs)

class SamplePerson(VersionedNode):
    name = StringProperty()
    birth = StringProperty()

person = SamplePerson()
person.name = 'Name'
person.birth = 'Some time ago'
person.save()
person.name = 'Name 1'
person.save()
person.name = 'Name 2'
person.save()
