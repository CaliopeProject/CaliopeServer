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
from cid.core.entities import RelationshipFrom, StringProperty
from cid.core.entities import VersionedNode, CaliopeJSONProperty



class CaliopeProject(VersionedNode):

    name = StringProperty()
    general_location = StringProperty()
    locality = StringProperty()
    project_type = StringProperty()
    record_document_creation = StringProperty()
    profit_center = StringProperty()
    areas = CaliopeJSONProperty()
