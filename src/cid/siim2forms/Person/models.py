from cid.core.entities import (RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class Person(VersionedNode):
    name = StringProperty()
    surname = StringProperty()
    surname1 = StringProperty()
    genero = StringProperty()

