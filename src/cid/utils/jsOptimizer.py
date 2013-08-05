# -*- encoding: utf-8 -*-
"""
@authors: Andrés Calderón andres.calderon@correlibre.org

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
"""
import os
import time
import sys
import hashlib
import re
import uglipyjs

class jsOptimizer(object):
    def __init__(self, prefix="static_cache_"):
        self.jstype = re.compile(".*js$")
        self.prefix = prefix 

    def uglifyjs(self,path):
        str = open(path,'r').read()
        js = unicode(str, errors='ignore')
        if len(js):
            try:
                ujs = uglipyjs.compile(js)
            except:
                pass
            else:
                return ujs
        return None
                       
    def js_file_cache(self, path, cache_store):
        if self.jstype.match(path) is not None:
            h = hashlib.sha1(path).hexdigest()
            key = self.prefix+h
            if cache_store.__contains__(key):
                value = cache_store.get(key)
                return value
            else:
                value = self.uglifyjs(path)
                if value:
                    cache_store.put(key,value)
                    return value
        return None
    

    def js_put_file_cache(self, path, cache_store):
        if self.jstype.match(path) is not None:
            h = hashlib.sha1(path).hexdigest()
            key = self.prefix+h
            print key + " " + path
            value = self.uglifyjs(path)
            if value:
                cache_store.put(key,value)
                return value                    
        return None


    def js_get_file_cache(self, path, cache_store):
        h = hashlib.sha1(path).hexdigest()
        key = self.prefix+h
        if cache_store.__contains__(key):
            value = cache_store.get(key)
            return value
        return None


    def watch(self,rootdir,cache_store):
        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                path = root+'/'+file
                self.js_file_cache(path,cache_store)
            
            for folder in subFolders:
                for file in files:
                    path = root+'/'+file
                    self.js_file_cache(path,cache_store)
