# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org

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

from cid.core.entities import (VersionedNode, DateTimeProperty,
                               StringProperty, IntegerProperty, RelationshipTo, CaliopeDocument, timeStampGenerator,
                               ZeroOrOne, ZeroOrMore)


class OrfeoDocumentType(VersionedNode):
    name = StringProperty(index=True)


class OrfeoSerie(VersionedNode):
    name = StringProperty(index=True)
    code = StringProperty(index=True)
    member_of = RelationshipTo(VersionedNode, 'MEMBER_OF', ZeroOrOne)
    document_type = RelationshipTo(OrfeoDocumentType, 'DOCUMENT_TYPE', ZeroOrMore)


class OrfeoAttachment(VersionedNode):
    description = StringProperty()
    pages = IntegerProperty()
    document_type = StringProperty()
    document_attachment = RelationshipTo(CaliopeDocument, 'FILE')


class Orfeo(VersionedNode):
    register_time = DateTimeProperty(default=timeStampGenerator)
    document_time = DateTimeProperty()
    reference_code = StringProperty()
    guide_number = StringProperty()
    subject = StringProperty()
    type = StringProperty()
    sequence = StringProperty(unique_index=True)

    attachment = RelationshipTo(OrfeoAttachment, 'ATTACHMENT')

