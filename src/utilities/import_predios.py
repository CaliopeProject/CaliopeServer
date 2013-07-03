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
import os


#CaliopeStorage
import odisea.CaliopeStorage 
from odisea.CaliopeStorage import CaliopeNode

from neomodel import DoesNotExist
from neomodel.contrib import SemiStructuredNode
from neomodel.properties import (BooleanProperty,
                                 DateTimeProperty,
                                 FloatProperty,
                                 IntegerProperty,
                                 StringProperty)


class CatastroReg2(CaliopeNode):
    sector  = StringProperty(index=True, unique_index=True)
    chip = StringProperty(index=True, unique_index=True)
    cedula_catastral = StringProperty(index=True, unique_index=True)
    matricula = StringProperty(index=True, unique_index=True)

    #sector  = StringProperty(index=True)
    #id_lote = StringProperty()
    #chip = StringProperty(index=True)
    #codigo_direccion = StringProperty()
    #direccion_actual = StringProperty()
    #cedula_catastral = StringProperty(index=True)
    #matricula = StringProperty(index=True)
    #escritura = StringProperty()
    #notaria = IntegerProperty()
    #fecha_documento = DateTimeProperty()
    #area_terreno = FloatProperty()
    #area_construida = FloatProperty()
    #tipo_propiedad = IntegerProperty()
    #codigo_destino = IntegerProperty()
    #clase_predio = StringProperty()
    #codigo_estrato = IntegerProperty()
    #zona_fisica_geoeconomica = StringProperty()
    
    
ins = open( "Predios.csv", "r" )
line = ins.readline()
header = map(lambda f: f.strip('\n').strip('"').lower(), line.split('|'))

print header

for line in ins:
    
    fields = map(lambda f: f.strip('\n').strip('"'), line.replace(',','.').split('|'))

    node = CatastroReg2()

    record = {}
    map(lambda k, v: record.update({k: v}), header, fields)
    
    

    map(lambda k, v: setattr(node,k, v), header, fields)

    node.area_terreno = float(record["area_terreno"])
    node.area_construida = float(record["area_terreno"])

    
    node.save()
    
    
