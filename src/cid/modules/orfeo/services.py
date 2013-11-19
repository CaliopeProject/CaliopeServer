# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM2 Server is the web server of SIIM2 Framework
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
from tinyrpc.dispatch import public

from cid.core.entities import (CaliopeServices)

from redis import Redis


class OrfeoServices(CaliopeServices):
    def __new__(cls, *args, **kwargs):
        cls.r = Redis()
        return cls

    def __init__(self, *args, **kwargs):
        super(OrfeoServices, self).__init__(*args, **kwargs)

    @classmethod
    @public(name='commit')
    def commit(cls, uuid):
        orfeo_sequence = cls.r.incr('orfeo_sequence')
        super(OrfeoServices, cls).update_field(cls, uuid, 'orfeo_sequence', orfeo_sequence)
        rv = super(OrfeoServices, cls).commit(uuid)
        return rv

