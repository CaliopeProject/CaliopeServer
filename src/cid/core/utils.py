# -*- coding: utf-8 -*-
"""
    cid.core.utils
    ~~~~~~~~~~~~~~

    Este módulo contiene funciones y clases que son utilizadas por
    el módelo de almacenamiento.

    :author: Sebastián Ortiz <neoecos@gmail.com>
    :copyright: (c) 2013 por Fundación CorreLibre
    :license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Storage is the base of Caliope's Framework
Copyright (C) 2013  Fundación Correlibre

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

import uuid
import hashlib
from datetime import datetime
from pytz import utc


#: uuid version 4
def uuidGenerator():
    return str(uuid.uuid4()).decode('utf-8')


#: All timestamps should be in UTC
def timeStampGenerator():
    return datetime.now(utc)


def getBase64():
    pass


def get_sha256(file_name):
    with open(file_name) as f:
        m = hashlib.sha256()
        m.update(f.read())
        return m.hexdigest()

#http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary/1165552#1165552
#https://github.com/hughdbrown/dictdiffer
class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

