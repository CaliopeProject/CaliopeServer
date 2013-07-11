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
import sys

from datetime import datetime

#neomodel exceptiosn

from neomodel.exception import UniqueProperty

#Model imports
from cid.model.SIIMModel import RegistroPredioCatastroTipo2


def main(argv):
    if len(argv) is not 1:
        print "Usage import_predios.py predios.csv"
    else:
        print "Preparing to import from "
        print argv
        importPrediosWithCreateMethod(argv[0])


def parseDateFromTwoDigitYear(dumbdate):
    day, month, year = map(int, dumbdate.split('/'))
    if year <= 13:
        year += 2000
    else:
        year += 1900
    return datetime(year, month, day)


def importPredios(filename):
    ins = open(filename, "r")
    line = ins.readline()
    header = map(lambda f: f.strip('\n').strip('"').lower(), line.split('|'))
    print header
    for line in ins:
        fields = map(lambda f: f.strip('\n').strip('"'),
                     line.replace(',', '.').split('|'))
        node = RegistroPredioCatastroTipo2()
        record = {}
        map(lambda k, v: record.update({k: v}), header, fields)
        map(lambda k, v: setattr(node, k, v), header, fields)
        node.fecha_documento = parseDateFromTwoDigitYear(record['fecha_documento'])
        try:
            node.save()
        except UniqueProperty:
            print record


def importPrediosWithCreateMethod(filename):
    ins = open(filename, "r")
    line = ins.readline()
    header = map(lambda f: f.strip('\n').strip('"').lower(), line.split('|'))
    print header
    batchList = []
    for line in ins:
        fields = map(lambda f: f.strip('\n').strip('"'),
                     line.replace(',', '.').split('|'))
        record = {}
        map(lambda k, v: record.update({k: v}), header, fields)
        record['fecha_documento'] = parseDateFromTwoDigitYear(record['fecha_documento'])
        batchList.append(record)
        if len(batchList) == 300:
            try:
                RegistroPredioCatastroTipo2.create(*batchList)
                batchList = []
            except UniqueProperty:
                print "Error in"
                print batchList
    RegistroPredioCatastroTipo2.create(*batchList)
    print "No more todo"


if __name__ == '__main__':
    main(sys.argv[1:])

