# -*- encoding: utf-8 -*-
"""
@authors: Nelson Daniel Ochoa ndaniel8a@gmail.com

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
from cid.core.models import CaliopeUser, RelationshipFrom, StringProperty
from cid.core.entities import CaliopeEntityData, CaliopeEntity


class ProjectData(CaliopeEntityData):
    __index__ = 'CaliopeStorage'

    name = StringProperty()
    general_location = StringProperty()
    locality = StringProperty()
    project_type = StringProperty()
    record_document_creation = StringProperty()
    profit_center = StringProperty()

    managers = RelationshipFrom(CaliopeUser, 'MANAGES')

    def __init__(self, *args, **kwargs):
        super(ProjectData, self).__init__(*args, **kwargs)

    def get_task_data(self):
        return self._get_node_data()

    def set_task_data(self, data):
        return self.evolve(**data)


class Project(CaliopeEntity):
    __index__ = 'CaliopeStorage'

    entity_data_type = ProjectData

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)





