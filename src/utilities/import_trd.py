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



def main(argv):
    if len(argv) is not 1:
        print "Usage import_trd.py trd.csv"
    else:
        print "Preparing to import from "
        print argv
        import_trd_from_csv(argv[0])


def import_trd_from_csv(filename):
    with open(filename, 'rb') as csvfile:
        records = csv.reader(csvfile, delimiter='|', quotechar='"')
        head0 = records.next()
        head1 = records.next()
        current_serie = None
        for row in records:
            code = row[0].split('.')
            name = row[1]
            type = row[2]
            if type not in ['TD', 'S', 'SS']:
                print row + "unclassified entry"

            if type == 'TD':
                dtnode = OrfeoDocumentType.index.search(name=name)
                if not len(dtnode):
                    dtnode = OrfeoDocumentType()
                    dtnode.name = row[1]
                    dtnode.save()



if __name__ == '__main__':
    main(sys.argv[1:])