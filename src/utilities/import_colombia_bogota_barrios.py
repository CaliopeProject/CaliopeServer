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
import sys, csv, os, copy
from cid.core.entities import (VersionedNode,
                               CaliopeMunicipality,
                               CaliopeDCLocalidad,
                               CaliopeDCBarrioCatastral,
                               CaliopeDCUPZ,
                               Property,
                               DoesNotExist)

from datetime import datetime

#neomodel exceptions

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def main(argv):
    if len(argv) is not 1:
        print u"Usage " + __name__ + u"barrios.csv"
    else:
        print u"Preparing to import from "
        print argv
        importer = Importer()
        if importer.import_barrios(argv[0]):
            print "Done"


class Importer(object):
    def import_barrios(self, filename):
        #: All data in in Colombia, so need to create country first.
        bogota = self._get_bogota_dc()

        if os.path.exists(filename):
            with open(filename, 'rb') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = unicode_csv_reader(csvfile, dialect)
                header = reader.next()
                barrio_header_map = self._get_header_map(header,
                                                         CaliopeDCBarrioCatastral)
                localidad_header_map = self._get_header_map(header,
                                                            CaliopeDCLocalidad)
                upz_header_map = self._get_header_map(header, CaliopeDCUPZ)

                #: class attributes that are neomodel Property
                for line in reader:
                    barrio_data = self._create_dict(line, barrio_header_map)

                    localidad_data = self._create_dict(line,
                                                       localidad_header_map)
                    upz_data = self._create_dict(line, upz_header_map)

                    localidad = self.find_or_create_entity_with_data(
                        CaliopeDCLocalidad, **localidad_data)

                    upz = self.find_or_create_entity_with_data(
                        CaliopeDCUPZ,
                        **upz_data)
                    barrio = self.find_or_create_entity_with_data(
                        CaliopeDCBarrioCatastral,
                        **barrio_data)

                    if not localidad.located_in.is_connected(bogota):
                        localidad.located_in.connect(bogota)

                    if not barrio.part_of.is_connected(localidad):
                        barrio.part_of.connect(localidad)

                    if upz:
                        if not upz.is_in.is_connected(localidad):
                            upz.is_in.connect(localidad)


    def _get_bogota_dc(self):
        bogota = {'code': '11001'}

        return self.find_or_create_entity_with_data(CaliopeMunicipality,
                                                    **bogota)

    def _get_header_map(self, header, class_type):
        #: header file
        # "CODIGO"=>0," NOMBRE"=>1,"CODIGO LOCALIDAD"=>2,"LOCALIDAD"=>3,
        # " CODIGO UPZ"=>4,"UPZ=>5"
        header_ = copy.deepcopy(header)
        if class_type.__name__ == "CaliopeDCBarrioCatastral" and len(header_) \
                == 6:
            header_[0] = "code"
            header_[1] = "name"
        if class_type.__name__ == "CaliopeDCLocalidad" and len(header_) == 6:
            header_[2] = "code"
            header_[3] = "name"
        if class_type.__name__ == "CaliopeDCUPZ" and len(header_) == 6:
            header_[4] = "code"
            header_[5] = "name"

        cls_props = self._get_class_properties(class_type)
        header_map = {}
        for prop in cls_props:
            for i in xrange(len(header_)):
                if prop == header_[i]:
                    header_map[prop] = i
                    break
        return header_map


    def find_or_create_entity_with_data(self, *args, **kwargs):
        cls_entity = args[0] if len(args) > 0 else None
        if cls_entity is not None and issubclass(cls_entity, VersionedNode):
            code = kwargs['code'] if 'code' in kwargs else None
            if code is not None and not code == "":
                entities = cls_entity.index.search(code=code)
                if len(entities) == 0:
                    entity = cls_entity()
                    for k, v in kwargs.items():
                        entity.update_field(k, v)
                    entity.save()
                    print "Created: ", entity.name
                    return entity
                else:
                    if len(entities) == 1:
                        return entities[0]
                    else:
                        print "problemas con", kwargs
                        return None
        return None


    def _get_class_properties(self, cls):
        return [prop
                for prop, prop_inst in cls.__dict__.items()
                if prop and isinstance(prop_inst, Property)]


    def _create_dict(self, item, header_map):
        dct = {}
        return {key: item[val] for (key, val) in header_map.items()}


if __name__ == '__main__':
    main(sys.argv[1:])

