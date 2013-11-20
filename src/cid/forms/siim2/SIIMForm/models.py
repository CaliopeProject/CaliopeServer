from cid.core.entities import (RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               RelationshipFrom,
                               RelationshipTo,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class SIIMForm(VersionedNode):

    ficha = StringProperty()
    estado = StringProperty()
    nombre = StringProperty()
    forma_intervencion = StringProperty()
    localidad = StringProperty()
    localizacion_general = StringProperty()
    acta_creacion_proyecto = StringProperty()
    areas = CaliopeJSONProperty
    propietario = RelationshipTo(VersionedNode, 'PROPIETARIO')
