# -*- encoding: utf-8 -*-
"""
@authors: Nelson Daniel Ochoa ndaniel8a@gmail.com
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
#Caliope Entities
from cid.core.forms import FormNode

from cid.core.entities import (VersionedNode,
                               ZeroOrMore,
                               RelationshipTo,
                               StringProperty)


class Company(FormNode):
    #: Número de documento o identificacion
    number_identification = StringProperty()
    #: Dígito de verificacion del numero de identificacion
    digit_verification = StringProperty()
    #: Nombre o razón social
    name = StringProperty()
    #: Sigla
    initial = StringProperty()
    #: Representante legal
    legal_representative = RelationshipTo(VersionedNode, 'IS_IN', cardinality=ZeroOrMore)
    #: Teléfono
    telephone = StringProperty()
    #: Dirección
    address = RelationshipTo(VersionedNode, 'IS_IN', cardinality=ZeroOrMore)
    #: Correo electrónico
    email = StringProperty()