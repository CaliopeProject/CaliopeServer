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
from cid.core.utils import uuidGenerator, timeStampGenerator


class CaliopeNode(SemiStructuredNode):
    """
    This is the base class for all other items, contains basic properties and
    relations defined by the Caliope's Storage Model.
    This implements the basic operations defined in the model architecture.

    :class: CaliopeNode
    """

    __index__ = 'CaliopeStorage'

    uuid = StringProperty(default=uuidGenerator,
                          unique_index=True)

    #: All timestamps should be in UTC using pytz.utc
    timestamp = DateTimeProperty(default=timeStampGenerator)

    def __new__(cls, *args, **kwargs):
        #:RelationshipTo previous node. Root nodes should use "ROOT"
        __ancestor_node__ = RelationshipFrom(cls, 'ANCESTOR_NODE', ZeroOrOne)
        setattr(cls, 'ancestor_node', __ancestor_node__)
        inst = super(CaliopeNode, cls).__new__(cls, *args, **kwargs)
        return inst


    def __init__(self, *args, **kwargs):
        super(CaliopeNode, self).__init__(*args, **kwargs)

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

    def _get_inst_data(self):
        return self.__properties__


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
                    setattr(self, k, kwargs[k])
            else:
                setattr(self, k, kwargs[k])

    def evolve(self, **kwargs):
        """
        Copy all predecessor node properties and update it with the new from the
        arguments, and set ancestor_node with the self uuid, and set the relationship
        with the ancestor.
        """
        cls = self.__class__
        if self.__node__ is not None:
            new_node = cls(self._get_node_data())
            new_node._set_node_attr(**kwargs)
            new_node.save()
            cls.reconnect(self, new_node)
            new_node.ancestor_node.connect(self)
        else:
            new_node = cls(**kwargs)
            new_node.save()
        return new_node

    @classmethod
    def reconnect(cls, old_node, new_node):
        for key, val in old_node._class_properties().items():
            if issubclass(val.__class__, RelationshipDefinition):
                if (key != 'ancestor_node') and hasattr(new_node, key):
                    new_rel = getattr(new_node, key)
                    old_rel = getattr(old_node, key)
                    for n in old_rel.all():
                        saved = False
                        for node_class_rel in n._get_class_relationships():
                            node_rel = getattr(n,node_class_rel[0], None)
                            if issubclass(node_rel.__class__, (One, ZeroOrOne)):
                                if (getattr(node_rel, 'relation_type', None) ==
                                    getattr(new_rel, 'relation_type', None)):
                                    node_rel.reconnect(old_node, new_node)
                                    saved = True
                        if not saved:
                            new_rel.connect(n)

    @classmethod
    def pull(cls, id_node):
        return cls.index.get(uuid=id_node)

    @classmethod
    def push(cls, *args, **kwargs):
        """
        Creates a single node of one class and return it.
        """
        new_node = cls(*args, **kwargs)
        new_node.save()
        return new_node

    @classmethod
    def _get_class_properties(cls):
        return [(prop, prop_inst)
                for prop, prop_inst in cls.__dict__.items()
                if prop and isinstance(prop_inst, Property)]

    @classmethod
    def _get_class_relationships(cls):
        return [(rel, rel_inst)
                for rel, rel_inst in cls.__dict__.items()
                if rel and isinstance(rel_inst, RelationshipDefinition)]


class CaliopeRelation(RelationshipDefinition):
    """
    This is the base class for relationships within CaliopeNodes, it may contain
    properties as in nodes.
    """
    OUTGOING = neo4j.Direction.OUTGOING
    INCOMING = neo4j.Direction.INCOMING
    EITHER = neo4j.Direction.EITHER