# -*- encoding: utf-8 -*-
'''
@authors: Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Server is the web server of Caliope's Framework
Copyright (C) 2013 Infometrika

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
import sys
import json
import re


def loadJSONFromFile(filename):
    try:
        json_data = re.sub("(?:/\\*(?:[^*]|(?:\\*+[^*/]))*\\*+/)",
                           '', open(filename).read(), re.MULTILINE)
        json_data = json.loads(json_data)
    except IOError:
        json_data = {}
        print "Error: can\'t find file or read data"
    except ValueError:
        json_data = {}
        print "Error, is not a JSON" + filename
    else:
        return json_data
