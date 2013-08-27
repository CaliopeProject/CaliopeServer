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

#
from neomodel import DoesNotExist
from cid.modules.reg2bogota.readonly_models import RegistroPredioCatastroTipoII

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

#Flask

#from groupmodel import GroupNode

class PredioCatastros(object):
    @staticmethod
    @public
    def getPredio(sector):
        try:
            rec = RegistroPredioCatastroTipoII.index.get(sector=sector)
            
            if rec:
                data  = {}
                for k, v in rec._get_node_data().items():
                    if not isinstance(v, unicode):
                        v = unicode(v)
                    data[k] = v
                    
                print str(data)
                return  {'value': data}
            return {'record': False}

        except DoesNotExist as e:
            raise JSONRPCInvalidRequestError(e)

  