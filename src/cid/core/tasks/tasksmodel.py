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
#neomodel primitives
from neomodel.properties import (Property,
                                 DateTimeProperty,
                                 IntegerProperty,
                                 StringProperty)

#CaliopeStorage
from odisea.CaliopeStorage import CaliopeNode

class TaskNode(CaliopeNode):
    userid = StringProperty()
    event_date = DateTimeProperty()
    description = StringProperty()
    state = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

    def get_task_data(self):
        return self._get_node_data()

    def set_task_data(self, data):
        return self.evolve(**data)




