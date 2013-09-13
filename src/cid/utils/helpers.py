# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM Server is the web server of SIIM's Framework
Copyright (C) 2013 Infometrika Ltda

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
import re
import json
import datetime
import dateutil.parser



class DatetimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(obj)


class DatetimeDecoder(object):

    @staticmethod
    def json_date_parser(dct):
        for (key, value) in dct.items():
            if isinstance(value, list):
                tmp = []
                for v_ in value:
                    tmp.append(DatetimeDecoder._parser(v_))
                dct[key] = tmp
            elif isinstance(value, dict):
                tmp = {}
                for k_, v_ in value.items():
                    tmp[k_] = DatetimeDecoder._parser(v_)
                dct[key] = tmp
            elif isinstance(value, datetime.datetime):
                dct[key] = value
            else:
                dct[key] = DatetimeDecoder._parser(value)
        return dct


    @staticmethod
    def _parser(value):
        try:
            if re.match("(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})[\.(\d{3,6})Z)|(\+|\-)(\d{2}):(\d{2})]", value):
                return dateutil.parser.parse(value)
            return value
        except:
            return value
