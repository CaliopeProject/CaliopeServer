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
import csv
import sys

from cid.forms.orfeo.models import OrfeoSerie, OrfeoDocumentType


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def main(argv):
    if len(argv) is not 1:
        print "Usage import_trd.py trd.csv"
    else:
        print "Preparing to import from "
        print argv
        import_trd_from_csv(argv[0])


import unicodedata


def excludeAccents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def import_trd_from_csv(filename):
    with open(filename, 'rb') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        records = unicode_csv_reader(csvfile, dialect, delimiter='|', quotechar='"')

        #records = csv.reader(csvfile, delimiter='|', quotechar='"')
        head0 = records.next()
        head1 = records.next()
        current_serie = None
        for row in records:
            code = row[0]
            name = excludeAccents(row[1]).strip(' ')
            type = row[2]
            if type not in ['TD', 'S', 'SS']:
                print row + "unclassified entry"

            if type == 'S' or type == 'SS':
                #if len(code) != 2:
                #    print "error code at " + str(code)
                snode = OrfeoSerie.index.search(name=name)
                if not len(snode):
                    snode = OrfeoDocumentType()
                    snode.name = name
                    snode.code = code
                    snode.save()
                    current_serie = snode
                    print name + " code = " + code + " serie added"
                else:
                    current_serie = snode[0]

            if type == 'TD':
                dtnode = OrfeoDocumentType.index.search(name=name)
                if not len(dtnode):
                    dtnode = OrfeoDocumentType()
                    dtnode.name = name
                    dtnode.save()
                    current_dt= dtnode
                else:
                    current_dt = dtnode[0]
#                    snode.document_type
                    #print name + " added type"
                #current_dt.add_or_update_relationship_target(target_uuid=current_serie.uuid, rel_name='document_type')


if __name__ == '__main__':
    main(sys.argv[1:])