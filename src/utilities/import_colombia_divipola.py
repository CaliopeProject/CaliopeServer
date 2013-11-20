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
                               CaliopeCounty,
                               CaliopeState,
                               CaliopeMunicipality,
                               CaliopePopulatedCenter,
                               CaliopePopulatedCenterType,
                               Property,
                               DoesNotExist)

from datetime import datetime

#neomodel exceptions

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def main(argv):
    if len(argv) is not 2:
        print u"Usage " + __name__ + u"categorias.csv divipola.csv"
    else:
        print u"Preparing to import from "
        print argv
        importer = Importer()
        if importer.import_categoria_territorial(argv[0]):
            importer.import_divipola(argv[1])

class Importer(object):

    def import_categoria_territorial(self, filename):
        if os.path.exists(filename):
            with open(filename, 'rb') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = unicode_csv_reader(csvfile, dialect)
                header = reader.next()
                header_map = self._get_header_map(header,
                                              CaliopePopulatedCenterType)
                #: Match size between file and class.
                if len(header_map) == len(header):
                    for item in reader:
                        data = self._create_dict(item, header_map)
                        self.find_or_create_entity_with_data(CaliopePopulatedCenterType,
                                                        **data)
                else:
                    raise BaseException("Header does not match with class properties")
            return True


    def import_divipola(self, filename):
        #: All data in in Colombia, so need to create country first.
        country = self._get_default_country()

        if os.path.exists(filename):
            with open(filename, 'rb') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = unicode_csv_reader(csvfile, dialect)
                header = reader.next()
                st_header_map = self._get_header_map(header, CaliopeState)
                mu_header_map = self._get_header_map(header, CaliopeMunicipality)
                pm_header_map = self._get_header_map(header, CaliopePopulatedCenter)
                pmt_header_map = self._get_header_map(header, CaliopePopulatedCenterType)
                #: class attributes that are neomodel Property
                for line in reader:
                    st_data = self._create_dict(line, st_header_map)
                    mu_data = self._create_dict(line, mu_header_map)
                    pm_data = self._create_dict(line, pm_header_map)
                    pmt_data = self._create_dict(line, pmt_header_map)
                    state = self.find_or_create_entity_with_data(
                        CaliopeState, **st_data)
                    municipality = self.find_or_create_entity_with_data(
                                                    CaliopeMunicipality, **mu_data)
                    populated_center = self.find_or_create_entity_with_data(
                                                     CaliopePopulatedCenter,
                                                     **pm_data)
                    populated_center_type = self.find_or_create_entity_with_data(
                                                     CaliopePopulatedCenterType,
                                                     **pmt_data)
                    if not populated_center.type.is_connected(
                            populated_center_type):
                        populated_center.type.connect(populated_center_type)
                    if not populated_center.part_of.is_connected(
                            municipality):
                        populated_center.part_of.connect(municipality)
                    if not municipality.part_of.is_connected(state):
                        municipality.part_of.connect(state)
                    if not state.part_of.is_connected(country):
                        state.part_of.connect(country)




    def _get_default_country(self):
        """
        class CaliopeCounty(VersionedNode):

        name = StringProperty()
        code = StringProperty(index=True)
        phone_code = StringProperty()
        currency_code = StringProperty()
        iso_code = StringProperty()

        """
        colombia_data = {'name':'Colombia',
                        'code':57,
                        'phone_code':'+57',
                        'currency_code':'COP',
                        'iso_code':'co'}

        return self.find_or_create_entity_with_data(CaliopeCounty,
                                                   **colombia_data)

    def _get_header_map(self, header, class_type):
        #: header file
        # "Código Departamento"=>0,"Código Municipio"=>1,"Código Centro Poblado"=>2,
        # "Nombre Departamento"=>3,"Nombre Municipio"=>4,"Nombre Centro Poblado"=>5,
        # "Tipo=>6"
        header_ = copy.deepcopy(header)
        if class_type.__name__ == "CaliopeState" and len(header_) == 7:
            header_[0] = "code"
            header_[3] = "name"
        if class_type.__name__ == "CaliopeMunicipality" and len(header_) == 7:
            header_[1] = "code"
            header_[4] = "name"
        if class_type.__name__ == "CaliopePopulatedCenter" and len(header_) == 7:
            header_[2] = "code"
            header_[5] = "name"
        #: This method is used previusly for this class, that why the len condition
        if class_type.__name__ == "CaliopePopulatedCenterType" and len(header_) ==7:
            header_[6] = "code"

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
            if code is not None:
                entities = cls_entity.index.search(code=code)
                if len(entities) == 0:
                    entity = cls_entity()
                    for k, v in kwargs.items():
                        entity.update_field(k, v)
                    entity.save()
                    print "Created: ", entity.name
                    return entity
                else:
                    return entities[0]


    def _get_class_properties(self, cls):
        return [prop
                for prop, prop_inst in cls.__dict__.items()
                if prop and isinstance(prop_inst, Property)]


    def _create_dict(self, item, header_map):
        dct = {}
        return {key: item[val] for (key, val) in header_map.items()}

if __name__ == '__main__':
    main(sys.argv[1:])

