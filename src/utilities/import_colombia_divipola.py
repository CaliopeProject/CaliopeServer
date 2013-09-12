#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Server is the web server of Caliope's Framework
Copyright (C) 2013 Fundación Correlibre

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
'''
#system, and standard library
import sys, csv, os
from cid.core.entities import (CaliopePopulatedCenterType, CaliopePopulatedCenterTypeData,
                               CaliopeEntityData, CaliopeEntity, Property)

from datetime import datetime

#neomodel exceptions

from neomodel.exception import UniqueProperty

#Model imports
from cid.modules.siim2_forms.models import RegistroPredioCatastroTipoII


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def main(argv):
    if len(argv) is not 1:
        print u"Usage " + __name__ + u"categorias.csv divipola.csv"
    else:
        print u"Preparing to import from "
        print argv
        if import_categoria_territorial(argv[0]):
            import_divipola(argv[1])


def import_categoria_territorial(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = unicode_csv_reader(csvfile, dialect)
            header = reader.next()
            #: class attributes that are neomodel Property
            cls_props = _get_class_properties(CaliopePopulatedCenterTypeData)
            header_map = {}
            for prop in cls_props:
                for i in xrange(len(header)):
                    if prop == header[i]:
                        header_map[prop] = i
                        break
            if len(header_map) == len(header):
                for item in reader:
                    data = _create_dict(item, header_map)
                    find_or_create_entity_with_data(CaliopePopulatedCenterTypeData, **data)
            else:
                raise BaseException("Header does not match with class properties")


def import_divipola(filename):
    pass


def find_or_create_entity_with_data(*args, **kwargs):
    cls_entity_data = args[0] if len(args) > 0 else None
    cls_entity = None
    if cls_entity_data is not None and issubclass(cls_entity_data, CaliopeEntityData):
        cls_entity = cls_entity_data.entity_type
    if cls_entity is not None:
        code = kwargs['code'] if 'code' in kwargs else None
        if code is not None:
            data_entities = cls_entity_data.index.search(code=code)
            if len(data_entities) == 0:
                #: Catch this bug
                if issubclass(cls_entity.entity_data_type, cls_entity_data):
                    setattr(cls_entity, 'entity_data_type', cls_entity_data)
                entity = cls_entity()
                entity.save()
                entity.init_entity_data(**kwargs)
                return entity
            else:
                return data_entities[0].current.single()


def _get_class_properties(cls):
    return [prop
            for prop, prop_inst in cls.__dict__.items()
            if prop and isinstance(prop_inst, Property)]


def _create_dict(item, header_map):
    dct = {}
    if len(item) == len(header_map):
        return {key: item[val] for (key, val) in header_map.items()}
    else:
        None


if __name__ == '__main__':
    main(sys.argv[1:])

