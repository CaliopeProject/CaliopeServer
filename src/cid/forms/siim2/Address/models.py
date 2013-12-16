from cid.core.forms import FormNode

from cid.core.entities import StringProperty

from cid.core.entities.base_models.versioned_node import VersionedNode


class Address(FormNode):
    direccion = StringProperty()
