from cid.core.entities import (RelationshipFrom,
                               CaliopeUser, ZeroOrMore,
                               RelationshipTo,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class Person(VersionedNode):
    name = StringProperty(index=True, index_name="PersonNames",
                          index_config={"type" : "fulltext"})
    surname = StringProperty()
    surname1 = StringProperty()
    gender = StringProperty()
    address = RelationshipTo(VersionedNode, 'IS_IN', cardinality=ZeroOrMore)

