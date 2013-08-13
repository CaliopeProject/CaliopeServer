# -*- coding: utf-8 -*-
"""
    cid.core.models
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
from py2neo import neo4j
from neomodel.contrib import SemiStructuredNode
from neomodel.properties import ( Property, DateTimeProperty,
                                  StringProperty)
from neomodel.relationship import RelationshipDefinition, RelationshipFrom, RelationshipTo, RelationshipManager
from utils import uuidGenerator, timeStampGenerator


class CaliopeNode(SemiStructuredNode):
    """
    This is the base class for all other items, contains basic properties and
    relations defined by the Caliope's Storage Model.
    This implements the basic operations defined in the model architecture.

    :class: CaliopeNode
    """

    uuid = StringProperty(default=uuidGenerator,
                          unique_index=True)

    #: All timestamps should be in UTC using pytz.utc
    timestamp = DateTimeProperty(default=timeStampGenerator)



    def __init__(self, *args, **kwargs):
        #:RelationshipTo previous node. Root nodes should use "ROOT"
        ancestor_node = RelationshipFrom(self.__class__, 'ANCESTOR_NODE')
        setattr(self.__class__, 'ancestor_node',ancestor_node)
        super(CaliopeNode, self).__init__(*args, **kwargs)
        #self._set_node_attr(**kwargs)

    def _get_node_data(self):
        """
        This method read the metadata saved on a SemiStructuredNode and returns it.
        """
        rv = {}
        for attr in self.__node__.__metadata__['data']:
            if attr in self._class_properties():
                rv[attr] = getattr(self, attr)
            else:
                rv[attr] = self.__node__.__metadata__['data'][attr]
        return rv

    def _set_node_attr(self, **kwargs):
        """
        Method to update or add attributes to  the node.
        """
        for k in kwargs.keys():
            if k in self._class_properties() \
                and issubclass(self._class_properties()[k].__class__, Property):
                if self._class_properties()[k].has_default:
                    pass
                else:
                    self._class_properties()[k].__class__(kwargs[k])
            else:
                setattr(self, k, kwargs[k])

    def evolve(self, **kwargs):
        """
        Copy all predecessor node properties and update it with the new from the
        arguments, and set ancestor_node with the self uuid, and set the relationship
        with the ancestor.
        """
        cls = self.__class__
        new_node = cls(self._get_node_data())
        new_node._set_node_attr(**kwargs)
        new_node.save()
        cls.reconnect(self, new_node)
        new_node.ancestor_node.connect(self)
        return new_node

    @classmethod
    def reconnect(cls, old_node, new_node):
        for key, val in old_node._class_properties().items():
            if issubclass(val.__class__,RelationshipDefinition):
                if hasattr(new_node, key):
                    new_rel = getattr(new_node, key)
                    old_rel = getattr(old_node,key)
                    for n in old_rel.all():
                        new_rel.connect(n)

    @classmethod
    def pull(cls, id_node):
        return cls.index.get(uuid=id_node)

    @classmethod
    def push(cls, **kwargs):
        """
        Creates a single node of one class and return it.
        """
        new_node = cls(**kwargs)
        new_node.save()
        return new_node


class CaliopeUser(CaliopeNode):
    username = StringProperty(unique_index=True)
    domainname = StringProperty()
    password = StringProperty()
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    member_of = RelationshipTo('CaliopeGroup', 'IS_MEMBER_OF_GROUP')


class CaliopeGroup(CaliopeNode):
    name = StringProperty(required=True)
    code = StringProperty(unique_index=True)
    members = RelationshipFrom('CaliopeUser', 'IS_MEMBER_OF_GROUP')


class CaliopeDocument(CaliopeNode):
    url = StringProperty()
    sha256 = StringProperty()
    insertion_date = DateTimeProperty(default=lambda: timeStampGenerator())
    description = StringProperty()
    state = StringProperty()
    owner = RelationshipFrom(CaliopeUser, 'OWNER')

    @staticmethod
    def add_to_repo(parent_uuid, url, description):
        pass
        #u=urlparse(url)
        #if u.scheme=='file':
        #    sha256 = get_sha256(u.path)
        #save()


class CaliopeRelation(RelationshipDefinition):
    """
    This is the base class for relationships within CaliopeNodes, it may contain
    properties as in nodes.
    """
    OUTGOING = neo4j.Direction.OUTGOING
    INCOMING = neo4j.Direction.INCOMING
    EITHER = neo4j.Direction.EITHER
