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

    def save(self, *args, **kwargs):
        try:
          # Check if we have a stored version of this object.
          current_node = self.__class__.index.get(uuid = self.uuid)
          print current_node
          for d in current_node.__dict__:
            if d[:1] != '_': # Avoid attributes that start with _.
              if getattr(self, d) != getattr(current_node, d):
                print d, 'is different'
                print 'Now',  getattr(self, d)
                print 'Before', getattr(current_node, d)
        except: # TODO(nel): How to catch the exceptions?
          print 'Node does not exist'
          pass
        super(VersionedNode, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(VersionedNode, self).__init__(*args, **kwargs)

class SamplePerson(VersionedNode):
    name = StringProperty()
    birth = StringProperty()

person = SamplePerson()
person.name = 'Nelson'
person.birth = 'Some time ago'
person.save()

person.name = 'New nelson'
person.save()
