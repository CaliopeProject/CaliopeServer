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
from .contact import CaliopeContact
from .identification_document import CaliopeIdentificationDocument


class CaliopePerson(VersionedNode):
    #: primer nombre
    first_name = StringProperty()
    #: segundo nombre
    second_name = StringProperty()
    #: primer apellido
    last_name = StringProperty()
    #: segundo_apellido
    sur_name = StringProperty()
    identification_document = RelationshipTo(CaliopeIdentificationDocument, 'IDENTIFIED_BY', ZeroOrOne)
    #: información de contacto
    contact_information = RelationshipTo(CaliopeContact, 'CONTACT_INFORMATION', ZeroOrOne)
