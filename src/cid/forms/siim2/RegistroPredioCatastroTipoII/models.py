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

from cid.core.forms import FormNode

from cid.core.entities import (DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty)


class RegistroPredioCatastroTipoII(FormNode):
    #: Unique and indexed properties first
    sector = StringProperty(unique_index=True)
    chip = StringProperty(unique_index=True)
    cedula_catastral = StringProperty(unique_index=True)
    #: All other
    matricula = StringProperty()
    id_lote = StringProperty()
    codigo_direccion = StringProperty()
    direccion_actual = StringProperty()
    escritura = StringProperty()
    notaria = IntegerProperty()
    fecha_documento = DateTimeProperty()
    area_terreno = FloatProperty()
    area_construida = FloatProperty()
    tipo_propiedad = IntegerProperty()
    codigo_destino = IntegerProperty()
    clase_predio = StringProperty()
    codigo_estrato = IntegerProperty()
    zona_fisica_geoeconomica = StringProperty()